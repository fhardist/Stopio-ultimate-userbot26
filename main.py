import os
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

# --- KONFIGURASI ---
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

app = Client(
    "my_userbot",
    session_string=STRING_SESSION,
    api_id=API_ID,
    api_hash=API_HASH
)

geolocator = Nominatim(user_agent="my_userbot_2026")

# --- 🛠 PERINTAH DASAR ---

@app.on_message(filters.me & filters.command("ping", "."))
async def ping_handler(_, message):
    start = asyncio.get_event_loop().time()
    await message.edit("🚀 `Pinging...` ")
    ms = round((asyncio.get_event_loop().time() - start) * 1000, 2)
    await message.edit(f"🚀 **Userbot Online!**\nLatency: `{ms}ms` 🟢")

@app.on_message(filters.me & filters.command("ai", "."))
async def ai_handler(_, message):
    if len(message.command) < 2:
        return await message.edit("❌ Masukkan pertanyaan!")
    prompt = message.text.split(None, 1)[1]
    await message.edit("🤖 `AI Berpikir...` ")
    try:
        # Menggunakan API Blackbox/Chatgpt yang lebih stabil di 2026
        res = requests.get(f"https://api.sandipbaruwal.com/gpt4?query={prompt}").json()
        await message.edit(f"🤖 **Pertanyaan:** `{prompt}`\n\n**Jawaban:**\n{res['answer']}")
    except:
        await message.edit("❌ Gagal terhubung ke otak AI.")

@app.on_message(filters.me & filters.command("tr", "."))
async def translate_handler(_, message):
    if not message.reply_to_message or len(message.command) < 2:
        return await message.edit("❌ Balas sebuah pesan dan ketik `.tr en` (contoh).")
    lang = message.command[1]
    text = message.reply_to_message.text
    await message.edit("🔄 `Menerjemahkan...` ")
    try:
        res = requests.get(f"https://api.popcat.xyz/translate?to={lang}&text={text}").json()
        await message.edit(f"🌐 **Terjemahan ({lang.upper()}):**\n\n{res['translated']}")
    except:
        await message.edit("❌ Gagal menerjemahkan.")

# --- 🎭 FITUR HIBURAN & STATUS ---

@app.on_message(filters.me & filters.command("fake", "."))
async def fake_handler(client, message):
    if len(message.command) < 2: return
    action = message.command[1].lower()
    await message.delete()
    # Aksi: typing, playing, recording_video
    await client.send_chat_action(message.chat.id, action)

@app.on_message(filters.me & filters.command(["dadu", "slot"], "."))
async def game_handler(_, message):
    emoji = "🎲" if message.command[0] == "dadu" else "🎰"
    await message.delete()
    await app.send_dice(message.chat.id, emoji)

@app.on_message(filters.me & filters.command("em", "."))
async def anim_handler(_, message):
    # Daftar frame animasi yang lebih variatif
    animation_frames = [
        "🚶        ",
        "  🚶      ",
        "    🚶    ",
        "      🚶  ",
        "        🚶",
        "        🏃",
        "      🏃  ",
        "    🏃    ",
        "  🏃      ",
        "🏃        ",
        "🐢        ",
        "  🐢      ",
        "    🐢    "
    ]
    
    # Loop sebanyak 2 kali putaran
    for _ in range(2): 
        for frame in animation_frames:
            try:
                await message.edit(frame)
                # Jeda ideal adalah 0.5 detik agar tidak terkena Flood Limit
                await asyncio.sleep(0.8) 
            except Exception:
                # Jika terkena limit, kita hentikan sementara agar tidak banned
                break 
    
    await message.edit("✅ Animasi Selesai.")

# --- 📍 FITUR LOKASI & PRIVASI ---

@app.on_message(filters.me & filters.command("lokasi", "."))
async def lokasi_handler(_, message):
    if len(message.command) < 2: return
    place = message.text.split(None, 1)[1]
    await message.edit(f"🔍 `Mencari:` {place}...")
    loc = geolocator.geocode(place)
    if loc:
        await message.delete()
        await app.send_location(message.chat.id, loc.latitude, loc.longitude)
    else:
        await message.edit("❌ Lokasi tidak ditemukan.")

@app.on_message(filters.me & filters.command("uncast", "."))
async def uncast_handler(client, message):
    await message.edit("🧹 `Uncasting...` Menghapus pesan Anda.")
    async for msg in client.get_chat_history(message.chat.id):
        if msg.from_user and msg.from_user.is_self:
            try: await msg.delete()
            except: pass
    await message.respond("✅ **Bersih!**", delete_after=3)

@app.on_message(filters.me & filters.command("purge", "."))
async def purge_handler(client, message):
    if not message.reply_to_message:
        return await message.edit("❌ Balas ke pesan awal untuk purge.")
    
    start_id = message.reply_to_message.id
    msgs = []
    async for msg in client.get_chat_history(message.chat.id, offset_id=start_id - 1, reverse=True):
        msgs.append(msg.id)
        if len(msgs) >= 100: # Limit 100 pesan sekali jalan
            break
    await client.delete_messages(message.chat.id, msgs)

print("✅ ULTIMATE USERBOT 2026 IS ONLINE!")
app.run()
