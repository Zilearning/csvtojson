# 📊 CSV → JSON Converter — Medical Vital Signs

Aplikasi web lokal untuk mengkonversi file CSV dari monitor pasien (ECG, SpO2, Tensi, Suhu, dll.) menjadi output JSON terstruktur.

---

## 📂 Struktur Folder

```
csv to json/
├── server.py           ← Backend Flask (jalankan ini)
├── index.html          ← Frontend web (otomatis terbuka di browser)
├── uploads/            ← File CSV yang diupload (dibuat otomatis)
├── results/            ← File JSON hasil konversi (dibuat otomatis)
├── .venv/              ← Virtual environment Python
└── README.md           ← Dokumentasi ini
```

---

## ⚡ Cara Running (Setiap Kali Mau Pakai)

Buka **PowerShell** atau **Terminal** di folder `csv to json`, lalu jalankan:

```powershell
# Langkah 1 — Aktifkan virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Langkah 2 — Jalankan server
python server.py
```

Output yang muncul di terminal:

```
=======================================================
  🚀  CSV → JSON Converter  |  Server Running
=======================================================
  Local   : http://127.0.0.1:5000
  Network : http://192.168.X.X:5000
=======================================================
  Tekan Ctrl+C untuk menghentikan server.
```

Browser akan **terbuka otomatis**. Jika tidak, buka manual di:
- **Komputer ini** → `http://127.0.0.1:5000`
- **Device lain (HP/tablet)** di jaringan yang sama → gunakan URL **Network**

> ✅ **IP otomatis terdeteksi** setiap server dijalankan — tidak perlu ubah apapun saat ganti device atau jaringan.

---

## 🖥️ Cara Menggunakan Aplikasi

1. **Upload CSV** — Drag & drop file ke area upload, atau klik **Pilih File CSV**
2. **Tunggu konversi** — Progress bar akan tampil selama proses berlangsung
3. **Lihat hasil** — JSON tampil langsung di halaman dengan syntax highlight
4. **Download / Salin** — Klik **⬇ Download JSON** atau **📋 Salin JSON**

---

## 🔧 Setup Awal (Hanya 1 Kali)

Lakukan ini hanya saat pertama kali setup di komputer baru.

### 1. Pastikan Python sudah terinstall

```powershell
python --version
# Output: Python 3.x.x
```

Jika belum, download di [python.org](https://python.org/downloads).

### 2. Buat Virtual Environment

```powershell
python -m venv .venv
```

### 3. Aktifkan Virtual Environment

```powershell
& ".\.venv\Scripts\Activate.ps1"
```

> Jika error `execution policy`, jalankan dulu:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

### 4. Install Dependencies

```powershell
pip install flask flask-cors
```

### 5. Jalankan Server

```powershell
python server.py
```

---

## 📋 Format CSV yang Didukung

| Baris | Isi |
|-------|-----|
| Baris 1 | Header kolom (contoh: `ECG/HR`, `SpO2_A/SpO2`, dst.) |
| Baris 2 | Satuan unit |
| Baris 3 | Label/type (dilewati otomatis) |
| Baris 4+ | Data vital sign |

**Kolom yang dikenali:**

| Kolom CSV | Keterangan | Satuan |
|-----------|-----------|--------|
| `ECG/HR` | Heart Rate | bpm |
| `SpO2_A/SpO2` | Saturasi Oksigen A | % |
| `SpO2_B/SpO2` | Saturasi Oksigen B | % |
| `PR/PR` | Pulse Rate | bpm |
| `RR/RR` | Respiratory Rate | rpm |
| `TEMP/T1` | Suhu Tubuh T1 | °C |
| `TEMP/T2` | Suhu Tubuh T2 | °C |
| `CNBP/SYS` | Tekanan Darah Sistolik | mmHg |
| `CNBP/DIA` | Tekanan Darah Diastolik | mmHg |
| `Art/SYS` | Tekanan Arteri Sistolik | mmHg |
| `Art/MAP` | Mean Arterial Pressure | mmHg |

---

## 🌐 Akses dari Device Lain (HP / Tablet)

1. Pastikan HP/tablet terhubung ke **WiFi yang sama** dengan komputer
2. Lihat URL **Network** di terminal ketika server berjalan
3. Ketik URL tersebut di browser HP, contoh: `http://192.168.18.45:5000`

---

## 🛑 Menghentikan Server

Tekan **Ctrl + C** di terminal yang menjalankan `server.py`.

---

## ❓ Troubleshooting

| Masalah | Solusi |
|---------|--------|
| `ModuleNotFoundError: flask` | Aktifkan `.venv` dulu, lalu `pip install flask flask-cors` |
| Browser tidak terbuka otomatis | Buka manual: `http://127.0.0.1:5000` |
| Tidak bisa akses dari HP | Pastikan satu WiFi, coba matikan Windows Firewall sementara |
| Error `execution policy` | Jalankan `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| File CSV tidak dikenali | Pastikan encoding `latin-1` dan format baris sesuai tabel di atas |

---

## ⚙️ Konfigurasi (Opsional)

Edit bagian ini di `server.py` untuk menyesuaikan data pasien dan device:

```python
PATIENT_INFO = {
    "pid": "ANON123456",   # ID Pasien
    "vid": "",
    "name": "ANON PATIENT",
    "gender": "male"
}

DEVICE_ID = "ANONDEVICE001"  # ID device monitor
```

---

*Built with Python + Flask + Vanilla HTML/CSS/JS*
