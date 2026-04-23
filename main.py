import os
import asyncio
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

load_dotenv()

# --- KONFIGURASI ---
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Inisialisasi Client (Pyrogram V2)
app = Client(
    "my_userbot",
    session_string=STRING_SESSION,
    api_id=API_ID,
    api_hash=API_HASH
)

bot = Client(
    "asisten_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

geolocator = Nominatim(user_agent="my_userbot_2026")
active_fake_tasks = {}

# ================= 🛠 PERINTAH USERBOT =================

@app.on_message(filters.me & filters.command("ping", "."))
async def ping_handler(_, message):
    start = asyncio.get_event_loop().time()
    await message.edit("🚀 `Pinging...` ")
    ms = round((asyncio.get_event_loop().time() - start) * 1000, 2)
    await message.edit(f"🚀 **Userbot Online (V2)!**\nLatency: `{ms}ms` 🟢")

@app.on_message(filters.me & filters.command("fake", "."))
async def fake_handler(client, message: Message):
    global active_fake_tasks
    if len(message.command) < 2:
        return await message.edit("❌ Gunakan: `.fake typing` atau `.fake off` ")
    
    action_type = message.command[1].lower()
    chat_id = message.chat.id
    actions = {
        "typing": ChatAction.TYPING, 
        "playing": ChatAction.PLAYING, 
        "recording": ChatAction.RECORD_AUDIO
    }

    if action_type == "off":
        if chat_id in active_fake_tasks:
            active_fake_tasks[chat_id].cancel()
            active_fake_tasks.pop(chat_id, None)
            return await message.edit("📴 **Status dihentikan!**")
        return await message.edit("❌ Tidak ada status aktif.")

    if action_type not in actions: return
    if chat_id in active_fake_tasks: active_fake_tasks[chat_id].cancel()

    await message.delete()
    async def looping_action():
        try:
            while True:
                await client.send_chat_action(chat_id, actions[action_type])
                await asyncio.sleep(4)
        except asyncio.CancelledError: pass
    
    task = asyncio.create_task(looping_action())
    active_fake_tasks[chat_id] = task

@app.on_message(filters.me & filters.command("em", "."))
async def anim_handler(_, message):
    frames = ["🚶   ", " 🚶  ", "  🚶 ", "   🚶", "🏃💨 ", " 🏃💨", "  🏃💨", "📍 OK!"]
    for frame in frames:
        try:
            await message.edit(f"{frame}\u200b")
            await asyncio.sleep(0.6)
        except: continue

@app.on_message(filters.me & filters.command("uncast", "."))
async def uncast_handler(client, message):
    await message.edit("🧹 `Uncasting...` (Max 50 pesan)")
    count = 0
    async for msg in client.get_chat_history(message.chat.id, limit=50):
        if msg.from_user and msg.from_user.is_self:
            try:
                await msg.delete()
                count += 1
                await asyncio.sleep(0.3) 
            except: pass
    await message.respond(f"✅ **Bersih! {count} pesan dihapus.**", delete_after=3)

@app.on_message(filters.me & filters.command("ai", "."))
async def ai_handler(_, message):
    if len(message.command) < 2: return
    prompt = message.text.split(None, 1)[1]
    await message.edit("🤖 `AI Berpikir...` ")
    try:
        res = requests.get(f"https://api.sandipbaruwal.com/gpt4?query={prompt}").json()
        await message.edit(f"🤖 **AI:**\n\n{res['answer']}")
    except: await message.edit("❌ Gagal terhubung ke AI.")

# ================= 🤖 ASISTEN BOT =================

@bot.on_message(filters.command("start"))
async def bot_start(_, message):
    await message.reply("Halo Boss! Saya Asisten Userbot Anda. Silakan gunakan perintah dari akun utama.")

# ================= RUNNER (V2 COMPATIBLE) =================

async def main():
    print("🚀 Memulai Userbot & Asisten...")
    await app.start()
    await bot.start()
    print("✅ SEMUA ONLINE!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
