import os
from flask import Flask, render_template_string, request, redirect, Response

app = Flask(__name__)

# Konfigurasi folder penyimpanan file foto upload
UPLOAD_FOLDER = 'static'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ================= KREDENSI LOGIN ADMIN =================
ADMIN_USERNAME = 'adlu'
ADMIN_PASSWORD = 'pcr'

# ================= DATABASE SEMENTARA (DYNAMIC DATA) =================
web_data = {
    "home_title": "Welcome to Adlu's Electronics Space",
    "home_desc": "Selamat datang di portofolio digital saya. Sebagai mahasiswa Teknologi Rekayasa Sistem Elektronika di PCR, fokus saya mencakup pemrograman embedded system, instrumentasi industri, otomasi, dan perancangan sirkuit perangkat keras.",
    
    # Menampung nama file foto profil (Kosongkan/None di awal agar pakai avatar default)
    "profile_foto": None,
    "profile_nama": "Muhammad Adlu",
    "profile_kampus": "Politeknik Caltex Riau",
    "profile_jurusan": "Teknologi Rekayasa Sistem Elektronika (TRSE)",
    "profile_status": "Mahasiswa Aktif - Angkatan 2024",
    "profile_keahlian": "Microcontroller (Arduino/ESP32), PCB Design, IoT System",
    
    "galeri": [
        {
            "judul": "Laboratorium Elektronika PCR",
            "foto": "https://images.unsplash.com/photo-1581092334651-ddf26d9aae9d?w=500"
        }
    ]
}

# ================= STYLING CSS =================
CSS_STYLE = """
<style>
    * { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; box-sizing: border-box; }
    body { background: #f0f4f8; color: #1a202c; min-height: 100vh; display: flex; flex-direction: column; }
    
    header { background: #003366; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    header .logo { font-weight: bold; font-size: 20px; letter-spacing: 1px; color: #ffcc00; }
    nav a { color: white; text-decoration: none; margin-left: 20px; font-weight: 500; transition: color 0.3s; }
    nav a:hover { color: #ffcc00; }
    
    .container { max-width: 1000px; width: 90%; margin: 40px auto; flex: 1; }
    .card { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); border-top: 5px solid #003366; }
    
    h1 { color: #003366; margin-bottom: 20px; font-size: 32px; }
    h2 { color: #003366; margin-top: 30px; margin-bottom: 15px; font-size: 22px; border-bottom: 2px solid #ffcc00; padding-bottom: 5px; }
    p { color: #4a5568; line-height: 1.8; margin-bottom: 20px; font-size: 16px; }
    .badge { display: inline-block; background: #e2e8f0; color: #4a5568; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold; margin-bottom: 15px; }
    
    /* Lingkaran Foto Profil */
    .avatar-container { width: 140px; height: 140px; margin: 0 auto 15px; border-radius: 50%; border: 4px solid #003366; overflow: hidden; display: flex; justify-content: center; align-items: center; background: #e2e8f0; }
    .avatar-container img { width: 100%; height: 100%; object-fit: cover; }
    .avatar-default { font-size: 70px; }

    .info-table { width: 100%; border-collapse: collapse; margin-top: 20px; margin-bottom: 25px; }
    .info-table td { padding: 12px 15px; border-bottom: 1px solid #e2e8f0; font-size: 16px; }
    .info-table td.label { font-weight: bold; color: #003366; width: 30%; }
    
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; margin-top: 20px; }
    .project-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.02); }
    .project-card img { width: 100%; height: 200px; object-fit: cover; }
    .project-card .p-info { padding: 15px; text-align: center; font-weight: bold; color: #2d3748; }
    
    .form-section { background: #f7fafc; border: 1px solid #e2e8f0; padding: 25px; border-radius: 8px; margin-bottom: 30px; }
    .form-group { margin-bottom: 15px; }
    label { display: block; font-weight: bold; margin-bottom: 5px; color: #4a5568; }
    input[type="text"], textarea, input[type="file"] { width: 100%; padding: 10px; border: 1px solid #cbd5e0; border-radius: 5px; font-size: 14px; }
    textarea { resize: vertical; height: 100px; }
    
    .btn { display: inline-block; background: #003366; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; border: none; cursor: pointer; }
    .btn-submit { background: #319795; width: 100%; margin-top: 10px; color: white; }
    footer { text-align: center; padding: 20px; background: #1a202c; color: #a0aec0; font-size: 14px; margin-top: auto; }
</style>
"""

# ================= KONTROL KEAMANAN =================
def periksa_login(auth):
    return auth and auth.username == ADMIN_USERNAME and auth.password == ADMIN_PASSWORD

def minta_login():
    return Response(
        'Gagal Masuk!', 401,
        {'WWW-Authenticate': 'Basic realm="Login Admin UTS"'}
    )

def get_header():
    return f"""
    <header>
        <div class="logo">⚡ TRSE - PCR PORTFOLIO</div>
        <nav><a href="/">Home</a><a href="/profiles">Profile</a></nav>
    </header>
    """

def get_footer():
    return f"<footer>&copy; 2026 Muhammad Adlu | Teknologi Rekayasa Sistem Elektronika - Politeknik Caltex Riau</footer>"


# ================= 1. ROUTE HALAMAN HOME =================
@app.route('/')
def home():
    galeri_html = ""
    for item in web_data['galeri']:
        src = item['foto'] if item['foto'].startswith('http') else f"/static/{item['foto']}"
        galeri_html += f"""
        <div class="project-card">
            <img src="{src}" alt="Proyek">
            <div class="p-info">{item['judul']}</div>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Home | Portofolio PCR</title>
        {CSS_STYLE}
    </head>
    <body>
        {get_header()}
        <div class="container">
            <div class="card">
                <span class="badge">SYSTEM ELECTRONICS & AUTOMATION</span>
                <h1>{web_data['home_title']}</h1>
                <p>{web_data['home_desc']}</p>
                
                <h2>⚡ Proyek & Kegiatan Terbaru</h2>
                <div class="grid">
                    {galeri_html}
                </div>
            </div>
        </div>
        {get_footer()}
    </body>
    </html>
    """


# ================= 2. ROUTE HALAMAN PROFILES =================
@app.route('/profiles')
def profiles():
    # Logika penentuan foto profil (Pakai file lokal atau avatar emoji)
    if web_data['profile_foto']:
        avatar_html = f'<img src="/static/{web_data["profile_foto"]}" alt="Foto Profil">'
    else:
        avatar_html = '<div class="avatar-default">👨‍💻</div>'

    return f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Profil | Muhammad Adlu</title>
        {CSS_STYLE}
    </head>
    <body>
        {get_header()}
        <div class="container">
            <div class="card" style="text-align: center;">
                
                <div class="avatar-container">
                    {avatar_html}
                </div>
                
                <h1>Profil Mahasiswa</h1>
                <span class="badge" style="background: #ffcc00; color: #003366;">POLITEKNIK CALTEX RIAU</span>
                
                <table class="info-table">
                    <tr><td class="label">Nama Lengkap</td><td>{web_data['profile_nama']}</td></tr>
                    <tr><td class="label">Institusi</td><td>{web_data['profile_kampus']}</td></tr>
                    <tr><td class="label">Program Studi</td><td>{web_data['profile_jurusan']}</td></tr>
                    <tr><td class="label">Status Akademik</td><td>{web_data['profile_status']}</td></tr>
                    <tr><td class="label">Fokus Keahlian</td><td>{web_data['profile_keahlian']}</td></tr>
                </table>
                
                <a href="/" class="btn">&larr; Kembali ke Home</a>
            </div>
        </div>
        {get_footer()}
    </body>
    </html>
    """


# ================= 3. ROUTE HALAMAN ADMIN (TERKUNCI) =================
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    auth = request.authorization
    if not periksa_login(auth):
        return minta_login()

    if request.method == 'POST':
        aksi = request.form.get('action_type')
        
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        # Aksi 1: Update Teks Profil & Beranda
        if aksi == 'update_text':
            web_data['home_title'] = request.form.get('home_title')
            web_data['home_desc'] = request.form.get('home_desc')
            web_data['profile_nama'] = request.form.get('profile_nama')
            web_data['profile_jurusan'] = request.form.get('profile_jurusan')
            web_data['profile_status'] = request.form.get('profile_status')
            web_data['profile_keahlian'] = request.form.get('profile_keahlian')
            return redirect('/profiles')

        # Aksi 2: Ganti/Upload Foto Profil Utama
        elif aksi == 'update_avatar':
            file = request.files.get('avatar_file')
            if file:
                filename = "profile_aktif_" + file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                web_data['profile_foto'] = filename  # Simpan nama file ke database
                return redirect('/profiles')

        # Aksi 3: Upload Foto Galeri Proyek
        elif aksi == 'upload_foto':
            judul_foto = request.form.get('judul_foto')
            file = request.files.get('foto_file')
            
            if file and judul_foto:
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                web_data['galeri'].append({"judul": judul_foto, "foto": filename})
                return redirect('/')

    return f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8">
        <title>Panel Admin | Kendali Web</title>
        {CSS_STYLE}
    </head>
    <body>
        <header>
            <div class="logo">🔒 PANEL ADMIN TERKUNCI</div>
            <nav><a href="/">&larr; Keluar ke Web Publik</a></nav>
        </header>
        <div class="container">
            <div class="card">
                <h1>⚙️ Pusat Kendali Admin (Dashboard)</h1>
                <p>Kelola data informasi portofolio secara real-time.</p>
                
                <h2>👤 Ganti Foto Profil Utama</h2>
                <form class="form-section" method="POST" action="/admin" enctype="multipart/form-data">
                    <input type="hidden" name="action_type" value="update_avatar">
                    <div class="form-group">
                        <label>Pilih Foto Profil Baru Anda (Saran bentuk Square/Kotak):</label>
                        <input type="file" name="avatar_file" accept="image/*" required>
                    </div>
                    <button type="submit" class="btn btn-submit" style="background: #e67e22;">Unggah & Ganti Foto Profil</button>
                </form>

                <h2>📝 Edit Informasi Teks Web</h2>
                <form class="form-section" method="POST" action="/admin">
                    <input type="hidden" name="action_type" value="update_text">
                    <div class="form-group"><label>Judul Beranda:</label><input type="text" name="home_title" value="{web_data['home_title']}" required></div>
                    <div class="form-group"><label>Deskripsi Beranda:</label><textarea name="home_desc" required>{web_data['home_desc']}</textarea></div>
                    <div class="form-group"><label>Nama Mahasiswa:</label><input type="text" name="profile_nama" value="{web_data['profile_nama']}" required></div>
                    <div class="form-group"><label>Jurusan / Prodi:</label><input type="text" name="profile_jurusan" value="{web_data['profile_jurusan']}" required></div>
                    <div class="form-group"><label>Status & Angkatan:</label><input type="text" name="profile_status" value="{web_data['profile_status']}" required></div>
                    <div class="form-group"><label>Keahlian Elektronika:</label><input type="text" name="profile_keahlian" value="{web_data['profile_keahlian']}" required></div>
                    <button type="submit" class="btn btn-submit">Simpan & Perbarui Teks</button>
                </form>
                
                <h2>🖼️ Tambah Foto Kegiatan / Alat Elektronika</h2>
                <form class="form-section" method="POST" action="/admin" enctype="multipart/form-data">
                    <input type="hidden" name="action_type" value="upload_foto">
                    <div class="form-group"><label>Nama Proyek / Keterangan Gambar:</label><input type="text" name="judul_foto" placeholder="Contoh: Pengujian Robot" required></div>
                    <div class="form-group"><label>Pilih File Foto:</label><input type="file" name="foto_file" accept="image/*" required></div>
                    <button type="submit" class="btn btn-submit" style="background: #2b6cb0;">Publish Foto Baru</button>
                </form>
            </div>
        </div>
        {get_footer()}
    </body>
    </html>
    """

# ================= EKSEKUSI SERVER DINAMIS =================
if __name__ == '__main__':
    # Membaca port secara dinamis dari server cloud (Railway/Render)
    # Jika berjalan di lokal laptop, otomatis menggunakan port default 5002
    port = int(os.environ.get("PORT", 5002))
    
    # host='0.0.0.0' wajib agar server cloud menerima koneksi publik
    # use_reloader=False wajib mencegah crash "OK" di Thonny Windows
    app.run(host='0.0.0.0', debug=True, port=port, use_reloader=False)