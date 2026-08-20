# SQLite Database Manager

Aplikasi desktop untuk mengelola database SQLite secara visual tanpa perlu menggunakan command line.

## 📋 Deskripsi

SQLite Database Manager adalah aplikasi GUI yang dibangun dengan Python dan PySide6 untuk memudahkan pengelolaan database SQLite. Aplikasi ini menyediakan antarmuka visual untuk membuat, membuka, melihat, mengedit, dan memelihara database SQLite.

## ✨ Fitur Utama

### Manajemen Database
- Membuat database SQLite baru
- Membuka database SQLite yang sudah ada
- Menutup database
- Menampilkan informasi database (path, ukuran, versi SQLite, dll)
- Backup dan restore database
- Vacuum dan analyze database
- Integrity check

### Database Explorer
- Menampilkan struktur database (tabel, view, index, trigger)
- Navigasi hierarkis melalui sidebar

### Data Browser
- Menampilkan data tabel dengan pagination
- Sorting berdasarkan kolom
- Filtering dan pencarian data
- Insert, edit, dan delete row
- Commit dan rollback perubahan

### Table Structure
- Melihat struktur tabel (kolom, tipe data, constraint)
- Membuat tabel baru
- Menambah kolom
- Menghapus kolom
- Mengubah struktur tabel
- Menghapus tabel

### SQL Editor
- Menulis dan mengeksekusi query SQL
- Multi-statement SQL support
- Query history
- Menyimpan query favorit
- Shortcut keyboard (Ctrl+Enter untuk execute)

### Import/Export
- Import dari CSV
- Export ke CSV
- Export ke JSON
- Export ke SQL

### Fitur Lainnya
- Pencarian data di seluruh database
- Dark mode dan light mode
- Logging aktivitas
- Foreign key support
- Trigger dan view management

## 🛠️ Requirements

- Python 3.12 atau versi stabil terbaru
- PySide6 >= 6.6.0
- pytest >= 7.4.0 (untuk testing)

## 📦 Instalasi

### 1. Clone Repository

```bash
git clone <repository-url>
cd sqlite_manager
```

### 2. Buat Virtual Environment (Opsional tapi Disarankan)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 🚀 Cara Menjalankan

### Mode Normal

```bash
python main.py
```

### Dengan Log Level Tertentu

```bash
# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
python main.py --log-level DEBUG
```

### Specify Database pada Startup

```bash
python main.py --database path/to/database.db
```

## 🏗️ Build menjadi EXE (Windows)

### 1. Install PyInstaller

```bash
pip install pyinstaller
```

### 2. Build EXE

```bash
# One-file executable
pyinstaller --onefile --windowed --name "SQLite Database Manager" main.py

# Atau gunakan spec file untuk konfigurasi lebih detail
pyinstaller sqlite_manager.spec
```

### 3. Hasil Build

File executable akan terdapat di folder `dist/`:
- Windows: `dist/SQLite Database Manager.exe`
- Linux: `dist/SQLite Database Manager`
- macOS: `dist/SQLite Database Manager.app`

## 📁 Struktur Project

```
sqlite_manager/
│
├── main.py                      # Entry point aplikasi
├── requirements.txt             # Dependencies Python
├── README.md                    # Dokumentasi (file ini)
├── .gitignore                   # Git ignore rules
│
├── app/                         # Core aplikasi
│   ├── __init__.py
│   ├── application.py           # Main application class
│   └── settings.py              # Pengaturan aplikasi
│
├── core/                        # Utilities inti
│   ├── __init__.py
│   ├── config.py                # Konstanta konfigurasi
│   └── exceptions.py            # Custom exceptions
│
├── database/                    # Layer database
│   ├── __init__.py
│   ├── connection.py            # Manajemen koneksi
│   └── manager.py               # Operasi database
│
├── models/                      # Model data
│   └── __init__.py
│
├── repositories/                # Data access layer
│   └── __init__.py
│
├── services/                    # Business logic
│   └── __init__.py
│
├── ui/                          # User interface
│   ├── __init__.py
│   ├── main_window.py           # Main window
│   ├── explorer/                # Database explorer
│   ├── browser/                 # Data browser
│   ├── structure/               # Table structure
│   ├── editor/                  # SQL editor
│   ├── dialogs/                 # Dialog windows
│   └── widgets/                 # Reusable widgets
│
├── utils/                       # Utilities
│   ├── __init__.py
│   ├── logger.py                # Setup logging
│   └── validators.py            # Validasi input
│
├── styles/                      # Stylesheets
│   └── __init__.py
│
└── tests/                       # Unit tests
    ├── __init__.py
    ├── test_database/
    │   ├── __init__.py
    │   ├── test_connection.py
    │   └── test_manager.py
    ├── test_repositories/
    └── test_services/
```

## 🧪 Cara Menjalankan Test

### 1. Install Dependencies Testing

```bash
pip install -r requirements.txt
```

### 2. Jalankan Semua Test

```bash
pytest
```

### 3. Jalankan Test dengan Coverage

```bash
pytest --cov=. --cov-report=html
```

### 4. Jalankan Test Tertentu

```bash
# Test module tertentu
pytest tests/test_database/test_connection.py

# Test function tertentu
pytest tests/test_database/test_connection.py::test_connect

# Test dengan verbose output
pytest -v
```

## 🔧 Troubleshooting

### Error: "PySide6 requires libEGL.so"

**Solusi (Linux headless server):**
```bash
# Install Xvfb
sudo apt-get install xvfb

# Jalankan dengan Xvfb
xvfb-run python main.py
```

**Solusi (Windows):**
- Pastikan Visual C++ Redistributable terinstall
- Update driver graphics card

### Error: "Database is locked"

**Penyebab:** Database sedang digunakan oleh proses lain.

**Solusi:**
- Tutup aplikasi lain yang menggunakan database
- Restart aplikasi
- Periksa file lock (`*.db-shm`, `*.db-wal`)

### Error: "Unable to init server"

**Solusi (Linux):**
```bash
export DISPLAY=:0
python main.py
```

### Build EXE Gagal

**Solusi:**
```bash
# Bersihkan build sebelumnya
rm -rf build dist *.spec

# Build ulang dengan verbose
pyinstaller --verbose --onefile --windowed main.py
```

### Database Corruption

**Solusi:**
1. Gunakan fitur "Integrity Check" di aplikasi
2. Jika corrupt, coba recover dengan:
   ```bash
   sqlite3 database.db ".recover" > recovered.sql
   sqlite3 new_database.db < recovered.sql
   ```
3. Selalu gunakan backup sebelum operasi besar

## 📝 Log File

Log aplikasi tersimpan di:
- **Windows:** `%APPDATA%/SQLiteManager/logs/app.log`
- **Linux:** `~/.local/share/SQLiteManager/logs/app.log`
- **macOS:** `~/Library/Application Support/SQLiteManager/logs/app.log`

## ⌨️ Shortcut Keyboard

| Shortcut | Fungsi |
|----------|--------|
| `Ctrl+N` | Database baru |
| `Ctrl+O` | Buka database |
| `Ctrl+S` | Save changes |
| `Ctrl+W` | Tutup database |
| `F5` | Refresh |
| `Ctrl+Enter` | Execute SQL query |
| `Ctrl+Q` | Keluar aplikasi |
| `Ctrl+,` | Toggle dark mode |

## 🔒 Keamanan

- Menggunakan parameterized queries untuk mencegah SQL injection
- Tidak menyimpan password (SQLite tidak memiliki authentication native)
- Semua data tetap lokal, tidak dikirim ke internet
- Validasi input untuk nama tabel dan kolom
- Konfirmasi untuk operasi destruktif (DROP, DELETE, dll)

## 📄 Lisensi

[Tambahkan informasi lisensi di sini]

## 👥 Kontribusi

Kontribusi sangat diterima! Silakan:
1. Fork repository
2. Buat feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📞 Support

Untuk pertanyaan atau issue, silakan buat issue di repository GitHub atau hubungi developer.

---

**Dibuat dengan ❤️ menggunakan Python dan PySide6**
