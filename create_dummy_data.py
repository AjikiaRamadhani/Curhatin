from app import app, db
from models import User, Story, Comment, StoryLike, CommentLike, Notification
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta, timezone
import random

def get_indonesia_time():
    return datetime.now(timezone(timedelta(hours=7)))

def create_dummy_data():
    with app.app_context():
        print("🗑️ Menghapus data lama...")
        db.drop_all()
        db.create_all()
        
        print("👥 Membuat user dummy...")
        # Create dummy users
        users = []
        usernames = ['aliya', 'budi', 'citra', 'david', 'eka', 'fajar', 'gita', 'hadi', 'indra', 'jihan']
        names = ['Aliya Sari', 'Budi Santoso', 'Citra Dewi', 'David Wijaya', 'Eka Putri', 
                'Fajar Nugroho', 'Gita Maharani', 'Hadi Pratama', 'Indra Kurniawan', 'Jihan Aulia']
        
        for i, username in enumerate(usernames):
            user = User(
                username=username,
                email=f"{username}@example.com",
                password=generate_password_hash('password123'),
                created_at=get_indonesia_time() - timedelta(days=random.randint(1, 365))
            )
            db.session.add(user)
            users.append(user)
        
        db.session.commit()
        print(f"✅ Created {len(users)} users")
        
        print("📝 Membuat stories dummy...")
        # Create dummy stories
        stories = []
        story_contents = [
            "Hari ini aku merasa sangat bersyukur. Bertemu dengan teman lama yang sudah lama tidak jumpa, ngobrol nostalgia sampai lupa waktu. Hidup memang penuh kejutan yang menyenangkan!",
            
            "Sedih banget hari ini. Barusan putus sama pacar setelah 3 tahun bersama. Rasanya seperti dunia berhenti berputar. Butuh waktu untuk healing...",
            
            "Baru saja mengalami kejadian yang bikin deg-degan. Ketinggalan dompet di taksi, untungnya sopirnya jujur dan mengembalikan. Masih ada orang baik di dunia ini!",
            
            "Lagi stres sama pekerjaan. Deadline menumpuk, atasan terus menuntut, rasanya mau berteriak aja. Kadang pengen lari dari semua tanggung jawab.",
            
            "Bahagia banget! Akhirnya lulus sidang skripsi setelah berjuang 6 bulan. Perjuangan yang sangat melelahkan tapi worth it. Terima kasih untuk semua yang mendukung!",
            
            "Merasa kesepian akhir-akhir ini. Semua teman sibuk dengan kehidupan masing-masing. Pengen punya seseorang yang bisa diajak berbagi cerita setiap hari.",
            
            "Hari yang melelahkan. Dari pagi sampai malam cuma di depan laptop, meeting terus. Kadang bertanya-tanya, apa arti hidup kalau cuma kerja terus?",
            
            "Baru saja membantu nenek menyeberang jalan. Senang bisa melakukan kebaikan kecil. Senyumnya bikin hari jadi lebih berarti.",
            
            "Kecewa sama teman dekat. Dikhianati hanya karena masalah sepele. Apakah pertemanan selama ini hanya palsu?",
            
            "Liburan yang menyenangkan! Akhirnya bisa jalan-jalan ke Bali setelah 2 tahun hanya bermimpi. Pemandangan alamnya bikin hati tenang.",
            
            "Lagi galau mikirin masa depan. Mau lanjut S2 atau kerja dulu? Pilihan yang sulit, takut salah mengambil keputusan.",
            
            "Hari ini belajar hal baru: coding Python. Awalnya sulit, tapi semakin dipelajari semakin menarik. Semoga bisa jadi skill yang berguna!",
            
            "Kangen masa kecil dulu. Hidup sederhana, main bola sampai sore, tidak ada beban pikiran. Sekarang semuanya serba complicated.",
            
            "Baru saja nonton film yang sangat inspiratif. Mengajarkan tentang arti persahabatan dan pengorbanan. Recommended banget!",
            
            "Lagi sakit flu. Badan lemas, pilek, dan batuk-batuk. Pengen cepat sembuh agar bisa beraktivitas normal lagi.",
            
            "Senangnya! Hari ini dapat promosi di kerja. Perjuangan selama 2 tahun akhirnya membuahkan hasil. Ini awal yang baru!",
            
            "Sedih lihat berita tentang bencana alam. Banyak korban yang menderita. Semoga mereka diberikan kekuatan dan bantuan cepat datang.",
            
            "Lagi jatuh cinta sama seseorang. Tapi takut untuk mengungkapkan perasaan. Jangan-jangan cuma bertepuk sebelah tangan?",
            
            "Baru saja memulai bisnis kecil-kecilan. Nervous banget, takut gagal. Tapi lebih baik mencoba daripada menyesal tidak mencoba.",
            
            "Hari yang produktif! Beres-beres rumah, olahraga, dan baca buku. Kadang hal-hal sederhana bikin hidup lebih bermakna."
        ]
        
        for i in range(25):  # Create 25 stories
            user = random.choice(users)
            is_anonymous = random.choice([True, False, False])  # 33% chance anonymous
            
            story = Story(
                content=random.choice(story_contents),
                is_anonymous=is_anonymous,
                user_id=user.id,
                created_at=datetime.utcnow() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23)
                )
            )
            db.session.add(story)
            stories.append(story)
        
        db.session.commit()
        print(f"✅ Created {len(stories)} stories")
        
        print("💬 Membuat komentar dummy...")
        # Create dummy comments
        comments = []
        comment_contents = [
            "Wah, setuju banget! Aku juga pernah ngalamin hal serupa.",
            "Tetap semangat ya! Semua badai pasti akan berlalu.",
            "Terima kasih sudah berbagi cerita, ini sangat menginspirasi.",
            "Aku turut berbahagia untuk kamu! 🎉",
            "Jangan menyerah, kamu lebih kuat dari yang kamu kira.",
            "Ini pelajaran yang berharga buat kita semua.",
            "Aku bisa relate banget dengan ceritamu.",
            "Semoga cepat membaik keadaannya!",
            "Proud of you! Perjuanganmu tidak sia-sia.",
            "Ini reminder yang bagus buat aku, terima kasih!",
            "Keren banget! Lanjutkan perjuangannya.",
            "Aku dukung penuh keputusanmu!",
            "Wah, pengalaman yang menarik!",
            "Semoga diberikan kemudahan dalam segala urusan.",
            "Aku ikut senang membaca ceritamu!",
            "Jangan lupa jaga kesehatan ya!",
            "Ini membuatku berpikir tentang hidupku.",
            "Teruslah berbagi cerita yang positif!",
            "Aku belajar banyak dari pengalamanmu.",
            "Semoga kebahagiaan selalu menyertaimu!"
        ]
        
        for story in stories:
            # Each story gets 0-5 comments
            num_comments = random.randint(0, 5)
            for _ in range(num_comments):
                comment_user = random.choice([u for u in users if u.id != story.user_id])
                
                comment = Comment(
                    content=random.choice(comment_contents),
                    user_id=comment_user.id,
                    story_id=story.id,
                    created_at=story.created_at + timedelta(hours=random.randint(1, 48))
                )
                db.session.add(comment)
                comments.append(comment)
        
        db.session.commit()
        print(f"✅ Created {len(comments)} comments")
        
        print("🔄 Membuat reply komentar...")
        # Create some reply comments
        for comment in random.sample(comments, min(20, len(comments))):
            if random.random() < 0.3:  # 30% chance of having replies
                reply_user = random.choice([u for u in users if u.id != comment.user_id])
                
                reply = Comment(
                    content=random.choice(["Betul sekali!", "Iya nih!", "Setuju!", "Thanks responnya!"]),
                    user_id=reply_user.id,
                    story_id=comment.story_id,
                    parent_id=comment.id,
                    created_at=comment.created_at + timedelta(hours=random.randint(1, 12))
                )
                db.session.add(reply)
        
        db.session.commit()
        
        print("❤️ Membuat likes dummy...")
        # Create dummy likes for stories
        for story in stories:
            # Each story gets 0-8 likes from different users
            likers = random.sample(users, random.randint(0, min(8, len(users))))
            for liker in likers:
                if liker.id != story.user_id:  # Don't like own story
                    like = StoryLike(
                        user_id=liker.id,
                        story_id=story.id,
                        created_at=story.created_at + timedelta(hours=random.randint(1, 72))
                    )
                    db.session.add(like)
        
        db.session.commit()
        
        print("💖 Membuat likes untuk komentar...")
        # Create dummy likes for comments
        for comment in random.sample(comments, min(50, len(comments))):
            # Each comment gets 0-3 likes
            likers = random.sample(users, random.randint(0, min(3, len(users))))
            for liker in likers:
                if liker.id != comment.user_id:  # Don't like own comment
                    like = CommentLike(
                        user_id=liker.id,
                        comment_id=comment.id,
                        created_at=comment.created_at + timedelta(hours=random.randint(1, 24))
                    )
                    db.session.add(like)
        
        db.session.commit()
        
        print("🔔 Membuat notifikasi dummy...")
        # Create some notifications
        for user in users[:5]:  # Only for first 5 users
            # Create 2-5 notifications per user
            for i in range(random.randint(2, 5)):
                # Find a story by this user that has likes/comments
                user_stories = [s for s in stories if s.user_id == user.id]
                if user_stories:
                    story = random.choice(user_stories)
                    
                    notification = Notification(
                        user_id=user.id,
                        story_id=story.id,
                        type=random.choice(['story_like', 'new_comment']),
                        message=random.choice([
                            f"{random.choice(usernames)} menyukai curhatan Anda",
                            f"{random.choice(usernames)} mengomentari curhatan Anda",
                            f"{random.choice(usernames)} membalas komentar Anda"
                        ]),
                        created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 168))
                    )
                    db.session.add(notification)
        
        db.session.commit()
        
        print("🎉 Dummy data berhasil dibuat!")
        print("\n📊 Statistik Data:")
        print(f"   👥 Users: {User.query.count()}")
        print(f"   📝 Stories: {Story.query.count()}")
        print(f"   💬 Comments: {Comment.query.count()}")
        print(f"   ❤️ Story Likes: {StoryLike.query.count()}")
        print(f"   💖 Comment Likes: {CommentLike.query.count()}")
        print(f"   🔔 Notifications: {Notification.query.count()}")
        
        print("\n🔑 Login dengan akun berikut:")
        print("   Username: aliya")
        print("   Password: password123")
        print("\n   Atau gunakan username lain: budi, citra, david, dll.")

if __name__ == '__main__':
    create_dummy_data()