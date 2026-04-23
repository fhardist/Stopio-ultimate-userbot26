# Stopio-ultimate-userbot26
# 🚀 Multi-Functional Userbot V2 (Pyrogram)

Userbot Telegram berbasis **Pyrogram V2** yang dilengkapi dengan fitur **Asisten Bot**, Animasi, Game, Lokasi Palsu, dan integrasi AI (GPT-4). Ringan, stabil, dan siap di-deploy ke **Railway**.

---

## 🛠 Persiapan Bahan (BACA DULU!)

Sebelum melakukan deploy, lu wajib punya 4 "kunci" utama ini:

### 1. Ambil API ID & API HASH
1. Buka [my.telegram.org](https://my.telegram.org).
2. Masukkan nomor HP lu (pake format internasional: `+628...`).
3. Masukkan kode verifikasi yang masuk ke chat Telegram lu.
4. Klik **API Development Tools**.
5. Isi `App title` dan `Short name` bebas (contoh: `BotGw`).
6. Klik **Create application**.
7. Lu bakal dapet **App api_id** dan **App api_hash**. Simpan!

### 2. Ambil BOT TOKEN (Untuk Asisten)
1. Chat [@BotFather](https://t.me/BotFather) di Telegram.
2. Ketik `/newbot`.
3. Kasih nama bot bebas, lalu kasih username (akhiri dengan `_bot`).
4. Lu bakal dapet **HTTP API Token**. Simpan sebagai `BOT_TOKEN`.

### 3. Ambil STRING SESSION (Kunci Akun Utama)
1. Lu bisa pake **String Session Generator** (biasanya pake Replit atau script lokal).
2. **PENTING:** Jangan kasih kode String Session ini ke SIAPAPUN!

---

## 🚀 Panduan Deploy ke Railway

Setelah bahan lengkap, ikuti langkah ini:

### Langkah 1: Push ke GitHub
1. Buat repository baru di GitHub (Private disarankan).
2. Upload file `main.py`, `requirements.txt`, dan `.env`.

### Langkah 2: Setting Variables di Railway
Di dashboard Railway, masuk ke tab **Variables** dan masukkan:
* `API_ID`: (Isi dengan API ID lu)
* `API_HASH`: (Isi dengan API HASH lu)
* `STRING_SESSION`: (Isi dengan String Session lu)
* `BOT_TOKEN`: (Isi dengan Token Bot dari BotFather)

---

## 📜 Daftar Perintah (Commands)

### 👤 Akun Utama (Awalan Titik `.`)
| Perintah | Fungsi |
| :--- | :--- |
| `.ping` | Cek status bot online |
| `.uncast` | Hapus 50 pesan terakhir lu |
| `.lokasi [nama]` | Kirim lokasi palsu (Share Loc) |
| `.em` | Animasi kurir paket jalan |
| `.fake [type]` | Status Mengetik (`typing`/`playing`/`off`) |
| `.slot` / `.dadu` | Fitur game/judi interaktif |

### 🤖 Asisten Bot (Awalan Garing `/`)
| Perintah | Fungsi |
| :--- | :--- |
| `/start` | Memulai bot asisten |
| `/help` | Lihat daftar panduan lengkap |
| `/id` | Cek ID Telegram & Chat ID |
| `/tanya [teks]` | Tanya AI GPT-4 lewat bot |

---
**Build with ❤️ by StopioUbot26**
