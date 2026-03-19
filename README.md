=== Face Library 18 Update v1.0.0 ===
📅 19 Maret 2026

🔥 System
- Integrasi Dropbox API dengan refresh token
- Auto sync tanpa expired token

✨ Features
- Scan otomatis folder FaceLibrary18
- Generate JSON player otomatis
- Auto generate link image & zip

⚡ Improvements
- Semua link menggunakan dl=1 (direct download)

# 📦 Face Library Admin Guide

Panduan ini digunakan untuk memastikan semua face yang diupload dapat terbaca oleh sistem otomatis dan masuk ke database.

---

## 🎯 Tujuan

* Auto detect face dari Dropbox
* Auto generate JSON (`facelibrary18.json`)
* Auto generate link image & download
* Standarisasi struktur file

---

## 📁 Struktur Folder

### ✅ Format Wajib

```
ID_Nama Player_Nama Club
```

### ✔️ Contoh Benar

```
63490_Tom Haye_Persib Bandung
77777_Joao Cancelo_Barcelona
88888_Cristiano Ronaldo_Al Nassr
```

### ❌ Contoh Salah

```
Tom Haye_Persib Bandung
63490_TomHaye
63490_Tom_Haye_Persib
```

---

## 📦 Isi Folder (WAJIB)

Setiap folder harus berisi:

```
1 file .png  → thumbnail
1 file .zip  → face file
```

---

### 🖼️ Thumbnail (PNG)

* Format: `.png`
* Contoh:

```
haye.png
```

📌 Digunakan untuk preview di launcher / web

---

### 📁 File Face (ZIP)

* Format: `.zip`
* Contoh:

```
63490.zip
```

📌 Berisi file face (#Win, sourceimages)

---

## ⚠️ Rules Penting

* Wajib hanya **1 PNG**
* Wajib hanya **1 ZIP**
* Gunakan `_` sebagai pemisah nama folder
* ID harus berupa angka
* Nama & club boleh menggunakan spasi
* Hindari karakter aneh (`@ # %`)

---

## 📂 Lokasi Upload

Upload ke folder:

```
FaceLibrary18/
```

### Contoh Struktur

```
FaceLibrary18/
 ├── 63490_Tom Haye_Persib Bandung/
 │    ├── haye.png
 │    └── 63490.zip
```

---

## 🔄 Sistem Otomatis

Setelah upload:

* Sistem akan scan otomatis
* Generate JSON player
* Generate link image & zip

⏱️ Waktu proses: ±30 menit atau manual run

---

## 📄 Output JSON

```
{
  "id": "63490",
  "version": "v1",
  "name": "Tom Haye",
  "club": "Persib Bandung",
  "image": "https://...",
  "zip_url": "https://..."
}
```

---

## ❌ Error yang Sering Terjadi

| Masalah              | Penyebab                 |
| -------------------- | ------------------------ |
| Tidak muncul         | Nama folder tidak sesuai |
| Image tidak tampil   | File PNG tidak ada       |
| ZIP tidak terdeteksi | File ZIP tidak ada       |
| Link error           | File belum di-share      |

---

## 💡 Tips

* Gunakan nama file sederhana:

```
haye.png
63490.zip
```

* Pastikan hanya 1 PNG & 1 ZIP
* Jangan gunakan karakter aneh
* Gunakan ID yang unik

---


