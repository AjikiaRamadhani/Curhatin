from app import app, db

with app.app_context():
    # Hapus semua tabel dan buat ulang
    db.drop_all()
    db.create_all()
    print("✅ Database berhasil direset!")