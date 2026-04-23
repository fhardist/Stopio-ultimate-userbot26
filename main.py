import os
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
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

# Untuk menyimpan status fake action agar bisa looping di background
active_fake_tasks = {}

# ================= 🛠 PERINTAH DASAR =================

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
        # API GPT-4 Alternatif
        res = requests.get(f"https://api.sandipbaruwal.com/gpt4?query={prompt}").json()
        await message.edit(f"🤖 **Pertanyaan:** `{prompt}`\n\n**Jawaban:**\n{res['answer']}")
    except:
        await message.edit("❌ Gagal terhubung ke otak AI.")

@app.on_message(filters.me & filters.command("tr", "."))
async def translate_handler(_, message):
    if not message.reply_to_message or len(message.command) < 2:
        return await message.edit("❌ Balas pesan lalu ketik `.tr en`.")
    lang = message.command[1]
    text = message.reply_to_message.text
    await message.edit("🔄 `Translating...` ")
    try:
        res = requests.get(f"https://api.popcat.xyz/translate?to={lang}&text={text}").json()
        await message.edit(f"🌐 **Hasil ({lang.upper()}):**\n\n{res['translated']}")
    except:
        await message.edit("❌ Gagal menerjemahkan.")

# ================= 🎭 FITUR HIBURAN & STATUS =================

@app.on_message(filters.me & filters.command("fake", "."))
async def fake_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("❌ Gunakan: `.fake typing` atau `.fake off` ")
    
    action_type = message.command[1].lower()
    chat_id = message.chat.id
    
    actions = {
        "typing": ChatAction.TYPING,
        "playing": ChatAction.PLAYING,
        "recording": ChatAction.RECORD_AUDIO,
        "video": ChatAction.RECORD_VIDEO
    }

    if action_type == "off":
        if chat_id in active_fake_tasks:
            active_fake_tasks[chat_id].cancel()
            del active_fake_tasks[chat_id]
            return await message.edit("📴 **Status dihentikan!**")
        return await message.edit("❌ Tidak ada status yang sedang berjalan.")

    if action_type not in actions:
        return await message.edit("❌ Aksi tidak valid.")

    if chat_id in active_fake_tasks:
        active_fake_tasks[chat_id].cancel()

    await message.delete()

    async def looping_action():
        try:
            while True:
                await client.send_chat_action(chat_id, actions[action_type])
                await asyncio.sleep(4)
        except asyncio.CancelledError:
            pass

    task = asyncio.create_task(looping_action())
    active_fake_tasks[chat_id] = task

@app.on_message(filters.me & filters.command("em", "."))
async def anim_handler(_, message):
    perjalanan = [
        "🚶        ", "  🚶      ", "    🚶    ", "      🚶  ", "        🚶",
        "🏃💨      ", "  🏃💨    ", "    🏃💨  ", "      🏃💨", "        🏃💨",
        "🏍️         ", "  🏍️       ", "    🏍️     ", "      🏍️   ", "        🏍️ ",
        "🏙️--🏍️--   ", "🏙️----🏍️-- ", "🏙️------🏍️ ", "🏡--🏍️--   ", "🏡----🏍️-- ",
        "📦 ✨       ", "📍 PAKET SAMPAI!"
    ]
    await message.edit("🎬 `Menjalankan Misi...` ")
    for frame in perjalanan:
        try:
            await message.edit(f"{frame}\u200b")
            await asyncio.sleep(0.6) 
        except: continue
    await asyncio.sleep(1)
    await message.edit("✅ **Misi Selesai!**")

@app.on_message(filters.me & filters.command(["dadu", "slot"], "."))
async def game_handler(_, message):
    emoji = "🎲" if message.command[0] == "dadu" else "🎰"
    await message.delete()
    await app.send_dice(message.chat.id, emoji)

# ================= 📍 FITUR LOKASI & PRIVASI =================

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
    await message.edit("🧹 `Uncasting...` ")
    async for msg in client.get_chat_history(message.chat.id):
        if msg.from_user and msg.from_user.is_self:
            try: await msg.delete()
            except: pass
    await message.respond("✅ **Bersih!**", delete_after=3)

@app.on_message(filters.me & filters.command("purge", "."))
async def purge_handler(client, message):
    if not message.reply_to_message:
        return await message.edit("❌ Balas pesan awal untuk purge.")
    start_id = message.reply_to_message.id
    msgs = []
    async for msg in client.get_chat_history(message.chat.id, offset_id=start_id - 1, reverse=True):
        msgs.append(msg.id)
        if len(msgs) >= 100: break
    await client.delete_messages(message.chat.id, msgs)

print("✅ ULTIMATE USERBOT 2026 IS ONLINE!")
app.run()
