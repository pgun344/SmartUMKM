# SMARTUMKM Finance Tracker

Aplikasi desktop pencatatan keuangan untuk UMKM, dibangun dengan Python + CustomTkinter.

## Fitur Utama
- **Dashboard** — ringkasan saldo, pendapatan, pengeluaran, laba + grafik tren
- **Transaksi** — tambah/edit/hapus transaksi pemasukan & pengeluaran
- **Insight** — analitik margin laba, breakdown kategori, arus kas harian
- **Profil Bisnis** — kelola info bisnis, rekening bank, dan kategori

## Teknologi
- Python 3.10+
- CustomTkinter 5.2+
- SQLite (database lokal, tidak perlu server)

## Cara Menjalankan

```bash
# 1. Install dependensi
pip install customtkinter

# 2. Jalankan aplikasi
python app.py
```

## Struktur File
```
umkm_finance/
├── app.py          # Entry point & navigasi
├── style.py        # Tema, warna, font, helper widget
├── database.py     # SQLite layer (CRUD semua data)
├── dashboard.py    # Halaman Dashboard
├── transaction.py  # Halaman Transaksi
├── insight.py      # Halaman Insight & Analitik
├── account.py      # Halaman Profil Bisnis & Akun
└── README.md
```

## Cara Pakai Pertama Kali
1. Buka halaman **Profil** → isi nama bisnis & info
2. Klik **+ Tambah** di bagian Rekening → tambah akun pertama
3. Buka halaman **Transaksi** → mulai catat pemasukan/pengeluaran
4. Pantau di **Dashboard** & **Insight**
