# Curhatin - Platform Berbagi Cerita dan Keluh Kesah

Aplikasi web full-stack untuk berbagi cerita, keluh kesah, dan pengalaman hidup menggunakan Flask dan SQLite.

## 🚀 Fitur Utama

- **Authentication System** - Register, Login, Logout dengan Flask-Login
- **Posting Cerita** - Dengan pilihan anonymous posting
- **Like System** - Like/unlike story dan comment dengan AJAX
- **Comment System** - Komentar dan nested replies
- **Notification System** - Notifikasi real-time untuk like dan komentar
- **Image Upload** - Upload gambar untuk cerita dengan preview
- **Search & Filter** - Pencarian cerita dengan pagination
- **Responsive Design** - Dark/Light mode toggle
- **User Profiles** - Statistik dan riwayat cerita user
- **Infinite Scroll** - Load lebih banyak cerita secara otomatis

## 🛠️ Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite dengan SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript vanilla
- **Authentication**: Flask-Login dengan session management
- **File Upload**: Werkzeug dengan image processing
- **Styling**: Custom CSS dengan CSS variables untuk theming

## 📦 Installation & Setup

1. **Clone repository**
   ```bash
   git clone https://github.com/username/curhatin.git
   cd curhatin
2. Intall dependencies
   ```bash
   pip install -r requirements.txt
3. Setup database dengan dummy data (optional)
   ```bash
   python create_dummy_data.py
4. Run aplikasi
   ```bash
   python app.py
