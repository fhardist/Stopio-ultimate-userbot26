import os
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

# --- KONFIGURASI DASAR ---
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

# Inisialisasi Client Pyrogram
app = Client(
    "my_userbot_2026",
    session_string=STRING_SESSION,
    api_id=API_ID,
    api_hash=API_HASH
)

geolocator = Nominatim(user_agent="my_userbot_2026")

# ================= 1. FITUR INFORMASI & SELF =================

@app.on_message(filters.me & filters.command("ping", "."))
async def ping_handler(_, message: Message):
    start = asyncio.get_event_loop().time()
    await message.edit("🚀 `Pinging...` ")
    end = asyncio.get_event_loop().time()
    ms = round((end - start) * 1000, 2)
    await message.edit(f"🚀 **Userbot Online!**\nLatency: `{ms}ms` 🟢")

# ================= 2. FITUR ADMIN & PRIVASI (UNCAST) =================

@app.on_message(filters.me & filters.command("uncast", "."))
async def uncast_handler(client, message: Message):
    await message.edit("🧹 `Uncasting...` Menghapus jejak.")
    async for msg in client.get_chat_history(message.chat.id):
        if msg.from_user and msg.from_user.is_self:
            try:
                await msg.delete()
            except:
                pass
    await message.respond("✅ **Uncast Selesai.**")

# ================= 3. FITUR LOKASI =================

@app.on_message(filters.me & filters.command("lokasi", "."))
async def lokasi_handler(_, message: Message):
    if len(message.command) < 2:
        return await message.edit("❌ Masukkan nama tempat!")
    place = message.text.split(None, 1)[1]
    await message.edit(f"🔍 `Mencari:` {place}...")
    try:
        location = geolocator.geocode(place)
        if location:
            await message.delete()
            await app.send_location(message.chat.id, location.latitude, location.longitude)
        else:
            await message.edit("❌ Lokasi tidak ditemukan.")
    except:
        await message.edit("❌ Gagal mencari lokasi.")

# ================= 4. FITUR FAKE STATUS & GAME =================

@app.on_message(filters.me & filters.command("fake", "."))
async def fake_handler(client, message: Message):
    if len(message.command) < 2: 
        return await message.edit("❌ Gunakan: `.fake typing` atau `.fake playing`")
    action = message.command[1].lower()
    await message.delete()
    # Pilihan: typing, playing, recording_audio
    await client.send_chat_action(message.chat.id, action)

@app.on_message(filters.me & filters.command(["dadu", "slot", "bola"], "."))
async def game_handler(_, message: Message):
    game_map = {"dadu": "🎲", "slot": "🎰", "bola": "⚽"}
    emoji = game_map[message.command[0]]
    await message.delete()
    await app.send_dice(message.chat.id, emoji)

# ================= 5. FITUR CERDAS (AI) =================

@app.on_message(filters.me & filters.command("ai", "."))
async def ai_handler(_, message: Message):
    if len(message.command) < 2:
        return await message.edit("❌ Masukkan pertanyaan! Contoh: `.ai apa itu IT Support?` ")
    
    prompt = message.text.split(None, 1)[1]
    await message.edit("🤖 `Meminta jawaban dari AI...` ")
    
    try:
        # Menggunakan API publik yang lebih stabil
        url = f"https://widipe.com/openai?text={prompt}"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            # Terkadang struktur json berbeda, kita ambil field 'result' atau 'data'
            hasil = data.get("result") or data.get("data") or "Maaf, AI sedang bingung."
            await message.edit(f"🤖 **Pertanyaan:** `{prompt}`\n\n**Jawaban:**\n{hasil}")
        else:
            await message.edit("❌ API AI sedang sibuk, coba lagi nanti.")
            
    except Exception as e:
        await message.edit(f"❌ Error: {str(e)}")

print("✅ STOPIO ULTIMATE USERBOT 26 READY!")
app.run()
