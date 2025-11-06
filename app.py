from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Story, Comment, StoryLike, CommentLike, Notification
from config import Config
from datetime import datetime
import os

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Helper functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_image(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
        
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        try:
            from PIL import Image
            image = Image.open(file)
            if image.width > 800:
                ratio = 800 / image.width
                new_height = int(image.height * ratio)
                image = image.resize((800, new_height), Image.Resampling.LANCZOS)
            
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            image.save(image_path, optimize=True, quality=85)
        except ImportError:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(image_path)
        
        return f"uploads/{unique_filename}"
    return None

def is_story_liked_by_user(story_id, user_id):
    if not user_id:
        return False
    return StoryLike.query.filter_by(story_id=story_id, user_id=user_id).first() is not None

def is_comment_liked_by_user(comment_id, user_id):
    if not user_id:
        return False
    return CommentLike.query.filter_by(comment_id=comment_id, user_id=user_id).first() is not None

def get_comments_with_replies(story_id):
    return Comment.query.filter_by(story_id=story_id, parent_id=None).order_by(Comment.created_at.asc()).all()

def create_notification(user_id, story_id=None, comment_id=None, type='', message=''):
    notification = Notification(
        user_id=user_id,
        story_id=story_id,
        comment_id=comment_id,
        type=type,
        message=message
    )
    db.session.add(notification)
    db.session.commit()

def get_unread_notifications_count(user_id):
    return Notification.query.filter_by(user_id=user_id, is_read=False).count()

@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_count = get_unread_notifications_count(current_user.id)
        return dict(unread_notifications_count=unread_count)
    return dict(unread_notifications_count=0)

# ===== ROUTES ===== (HANYA SATU SET ROUTE)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    latest_stories_pagination = Story.query.order_by(Story.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    popular_stories = db.session.query(Story).outerjoin(StoryLike).group_by(Story.id).order_by(
        db.func.count(StoryLike.id).desc()
    ).limit(6).all()
    
    for story in latest_stories_pagination.items:
        story.user_has_liked = is_story_liked_by_user(story.id, current_user.id if current_user.is_authenticated else None)
    
    for story in popular_stories:
        story.user_has_liked = is_story_liked_by_user(story.id, current_user.id if current_user.is_authenticated else None)
    
    return render_template('index.html', 
                         stories=latest_stories_pagination, 
                         popular_stories=popular_stories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if not username or not email or not password:
            flash('Semua field harus diisi!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Password tidak cocok!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username sudah digunakan!', 'error')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email sudah digunakan!', 'error')
            return render_template('register.html')
        
        hashed_password = generate_password_hash(password)
        user = User(username=username, email=email, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registrasi berhasil! Silakan login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False
        
        if not username or not password:
            flash('Username dan password harus diisi!', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash('Login berhasil!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Login gagal. Periksa username dan password!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Anda telah logout.', 'info')
    return redirect(url_for('index'))

@app.route('/post', methods=['GET', 'POST'])
@login_required
def post_story():
    if request.method == 'POST':
        content = request.form.get('content')
        is_anonymous = 'is_anonymous' in request.form
        image_file = request.files.get('image')
        
        if not content or content.strip() == '':
            flash('Konten tidak boleh kosong!', 'error')
            return render_template('post_story.html')
        
        if len(content) > 1000:
            flash('Konten terlalu panjang! Maksimal 1000 karakter.', 'error')
            return render_template('post_story.html')
        
        # Handle image upload
        image_url = None
        if image_file and image_file.filename != '':
            image_url = save_image(image_file)
            if not image_url:
                flash('Format gambar tidak didukung! Gunakan JPG, PNG, atau GIF.', 'error')
                return render_template('post_story.html')
        
        story = Story(
            content=content.strip(),
            is_anonymous=is_anonymous,
            image_url=image_url,
            user_id=current_user.id
        )
        db.session.add(story)
        db.session.commit()
        flash('Curhatan berhasil diposting!', 'success')
        return redirect(url_for('index'))
    
    return render_template('post_story.html')

@app.route('/story/<int:story_id>')
def story_detail(story_id):
    story = Story.query.get_or_404(story_id)
    
    # Preload like status for current user
    story.user_has_liked = is_story_liked_by_user(story.id, current_user.id if current_user.is_authenticated else None)
    
    # Get comments with proper hierarchy
    comments = get_comments_with_replies(story_id)
    
    # Preload like status for comments
    for comment in comments:
        comment.user_has_liked = is_comment_liked_by_user(comment.id, current_user.id if current_user.is_authenticated else None)
        for reply in comment.replies:
            reply.user_has_liked = is_comment_liked_by_user(reply.id, current_user.id if current_user.is_authenticated else None)
    
    return render_template('story_detail.html', story=story, comments=comments)

@app.route('/like_story/<int:story_id>', methods=['POST'])
@login_required
def like_story(story_id):
    story = Story.query.get_or_404(story_id)
    existing_like = StoryLike.query.filter_by(user_id=current_user.id, story_id=story_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        like = StoryLike(user_id=current_user.id, story_id=story_id)
        db.session.add(like)
        liked = True
        
        # Buat notifikasi hanya jika bukan pemilik story
        if story.user_id != current_user.id:
            create_notification(
                user_id=story.user_id,
                story_id=story_id,
                type='story_like',
                message=f'{current_user.username} menyukai curhatan Anda'
            )
    
    db.session.commit()
    
    like_count = StoryLike.query.filter_by(story_id=story_id).count()
    return jsonify({'liked': liked, 'like_count': like_count})

@app.route('/comment/<int:story_id>', methods=['POST'])
@login_required
def add_comment(story_id):
    story = Story.query.get_or_404(story_id)
    content = request.form.get('content')
    parent_id = request.form.get('parent_id')
    
    if not content:
        flash('Komentar tidak boleh kosong!', 'error')
        return redirect(url_for('story_detail', story_id=story_id))
    
    comment = Comment(
        content=content,
        user_id=current_user.id,
        story_id=story_id,
        parent_id=parent_id if parent_id else None
    )
    db.session.add(comment)
    db.session.commit()
    
    # Buat notifikasi
    if parent_id:
        # Ini adalah reply
        parent_comment = Comment.query.get(parent_id)
        if parent_comment and parent_comment.user_id != current_user.id:
            create_notification(
                user_id=parent_comment.user_id,
                story_id=story_id,
                comment_id=comment.id,
                type='reply',
                message=f'{current_user.username} membalas komentar Anda'
            )
    else:
        # Ini adalah komentar baru
        if story.user_id != current_user.id:
            create_notification(
                user_id=story.user_id,
                story_id=story_id,
                comment_id=comment.id,
                type='new_comment',
                message=f'{current_user.username} mengomentari curhatan Anda'
            )
    
    flash('Komentar berhasil ditambahkan!', 'success')
    return redirect(url_for('story_detail', story_id=story_id))

@app.route('/like_comment/<int:comment_id>', methods=['POST'])
@login_required
def like_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    existing_like = CommentLike.query.filter_by(user_id=current_user.id, comment_id=comment_id).first()
    
    if existing_like:
        db.session.delete(existing_like)
        liked = False
    else:
        like = CommentLike(user_id=current_user.id, comment_id=comment_id)
        db.session.add(like)
        liked = True
        
        # Buat notifikasi hanya jika bukan pemilik comment
        if comment.user_id != current_user.id:
            create_notification(
                user_id=comment.user_id,
                comment_id=comment_id,
                type='comment_like',
                message=f'{current_user.username} menyukai komentar Anda'
            )
    
    db.session.commit()
    
    like_count = CommentLike.query.filter_by(comment_id=comment_id).count()
    return jsonify({'liked': liked, 'like_count': like_count})

@app.route('/delete_story/<int:story_id>', methods=['POST'])
@login_required
def delete_story(story_id):
    story = Story.query.get_or_404(story_id)
    
    if story.user_id != current_user.id:
        flash('Anda tidak memiliki akses untuk menghapus curhatan ini!', 'error')
        return redirect(url_for('index'))
    
    db.session.delete(story)
    db.session.commit()
    flash('Curhatan berhasil dihapus!', 'success')
    return redirect(url_for('index'))


@app.route('/edit/<int:story_id>', methods=['GET', 'POST'])
@login_required
def edit_story(story_id):
    story = Story.query.get_or_404(story_id)

    if story.user_id != current_user.id:
        flash('Anda tidak memiliki akses untuk mengedit curhatan ini!', 'error')
        return redirect(url_for('story_detail', story_id=story_id))

    if request.method == 'POST':
        content = request.form.get('content')
        is_anonymous = 'is_anonymous' in request.form
        remove_image = 'remove_image' in request.form
        image_file = request.files.get('image')

        if not content or content.strip() == '':
            flash('Konten tidak boleh kosong!', 'error')
            return render_template('post_story.html', story=story)

        if len(content) > 1000:
            flash('Konten terlalu panjang! Maksimal 1000 karakter.', 'error')
            return render_template('post_story.html', story=story)

        # Handle image upload or removal
        if image_file and image_file.filename != '':
            image_url = save_image(image_file)
            if not image_url:
                flash('Format gambar tidak didukung! Gunakan JPG, PNG, atau GIF.', 'error')
                return render_template('post_story.html', story=story)

            # Remove old image file if present
            if story.image_url:
                old_path = os.path.join(app.root_path, 'static', story.image_url)
                try:
                    if os.path.exists(old_path):
                        os.remove(old_path)
                except Exception:
                    pass

            story.image_url = image_url
        else:
            if remove_image:
                if story.image_url:
                    old_path = os.path.join(app.root_path, 'static', story.image_url)
                    try:
                        if os.path.exists(old_path):
                            os.remove(old_path)
                    except Exception:
                        pass
                story.image_url = None

        story.content = content.strip()
        story.is_anonymous = is_anonymous

        db.session.commit()
        flash('Curhatan berhasil diperbarui!', 'success')
        return redirect(url_for('story_detail', story_id=story.id))

    # GET
    return render_template('post_story.html', story=story)

@app.route('/delete_comment/<int:comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    story_id = comment.story_id
    
    if comment.user_id != current_user.id:
        flash('Anda tidak memiliki akses untuk menghapus komentar ini!', 'error')
        return redirect(url_for('story_detail', story_id=story_id))
    
    db.session.delete(comment)
    db.session.commit()
    flash('Komentar berhasil dihapus!', 'success')
    return redirect(url_for('story_detail', story_id=story_id))

@app.route('/profile')
@login_required
def profile():
    # Hitung statistik user
    user_stories = Story.query.filter_by(user_id=current_user.id).count()
    
    # Hitung total likes yang diterima dari semua story user
    user_likes = db.session.query(StoryLike).join(Story).filter(Story.user_id == current_user.id).count()
    
    user_comments = Comment.query.filter_by(user_id=current_user.id).count()
    
    # Stories terbaru user
    recent_stories = Story.query.filter_by(user_id=current_user.id).order_by(Story.created_at.desc()).limit(5).all()
    
    return render_template('profile.html', 
                         user_stories=user_stories,
                         user_likes=user_likes,
                         user_comments=user_comments,
                         recent_stories=recent_stories)

@app.route('/notifications')
@login_required
def notifications():
    # Tandai semua notifikasi sebagai dibaca
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True})
    db.session.commit()
    
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notifications=notifications)

@app.route('/delete_notification/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    
    if notification.user_id != current_user.id:
        flash('Anda tidak memiliki akses untuk menghapus notifikasi ini!', 'error')
        return redirect(url_for('notifications'))
    
    db.session.delete(notification)
    db.session.commit()
    flash('Notifikasi berhasil dihapus!', 'success')
    return redirect(url_for('notifications'))

@app.route('/clear_notifications', methods=['POST'])
@login_required
def clear_notifications():
    Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash('Semua notifikasi berhasil dihapus!', 'success')
    return redirect(url_for('notifications'))

@app.route('/search')
def search_stories():
    query = request.args.get('q', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 6
    
    if query:
        # Search dengan pagination
        stories_pagination = Story.query.filter(
            Story.content.ilike(f'%{query}%')
        ).order_by(Story.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Preload like status
        for story in stories_pagination.items:
            story.user_has_liked = is_story_liked_by_user(story.id, current_user.id if current_user.is_authenticated else None)
    else:
        stories_pagination = None
    
    return render_template('search.html', 
                         stories=stories_pagination, 
                         query=query,
                         page=page)

@app.route('/api/stories')
def api_stories():
    page = request.args.get('page', 1, type=int)
    per_page = 6
    category = request.args.get('category', 'latest')
    
    if category == 'latest':
        stories_query = Story.query.order_by(Story.created_at.desc())
    else:  # popular
        stories_query = db.session.query(Story).outerjoin(StoryLike).group_by(Story.id).order_by(
            db.func.count(StoryLike.id).desc()
        )
    
    stories_pagination = stories_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Preload like status
    for story in stories_pagination.items:
        story.user_has_liked = is_story_liked_by_user(story.id, current_user.id if current_user.is_authenticated else None)
    
    stories_data = []
    for story in stories_pagination.items:
        # ✅ PERBAIKI: Gunakan url_for untuk generate image URL
        image_url = None
        if story.image_url:
            image_url = url_for('static', filename=story.image_url, _external=False)
        
        stories_data.append({
            'id': story.id,
            'content': story.content,
            'is_anonymous': story.is_anonymous,
            'image_url': image_url,  # ✅ Sekarang pakai URL yang benar
            'created_at': story.created_at.strftime('%d %b %Y %H:%M'),
            'author_name': 'Anonymous' if story.is_anonymous else story.author.username,
            'like_count': len(story.likes),
            'comment_count': len(story.comments),
            'user_has_liked': story.user_has_liked,
            'can_delete': current_user.is_authenticated and current_user.id == story.user_id
        })
    
    return jsonify({
        'stories': stories_data,
        'has_next': stories_pagination.has_next,
        'next_page': stories_pagination.next_num if stories_pagination.has_next else None,
        'total_pages': stories_pagination.pages
    })

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("🚀 Server starting on http://localhost:5000")
    app.run(debug=True)