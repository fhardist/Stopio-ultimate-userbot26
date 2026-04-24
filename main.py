import os
import asyncio
import requests
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv()

# ===============================================================
# ⚙️ KONFIGURASI SERVER & API
# ===============================================================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("my_userbot", session_string=STRING_SESSION, api_id=API_ID, api_hash=API_HASH)
bot = Client("asisten_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

geolocator = Nominatim(user_agent="my_userbot_2026")
active_fake_tasks = {}
autoreply_db = {}
is_welcome_on = False

# ===============================================================
# ⚡ FITUR PING (DENGAN LATENCY) & UNCAST
# ===============================================================

@app.on_message(filters.me & filters.command("ping", "."))
async def ping_handler(_, message):
    start = time.time()
    await message.edit("🚀 `Pinging...` ")
    end = time.time()
    latency = round((end - start) * 1000, 2)
    await message.edit(
        f"🚀 **Userbot Online!**\n"
        f"📡 **Latency:** `{latency} ms`\n"
        f"👤 **Status:** `Stable (V3 Final)`"
    )

@app.on_message(filters.me & filters.command("uncast", "."))
async def uncast_handler(client, message):
    await message.edit("🧹 `Cleaning messages...` ")
    async for msg in client.get_chat_history(message.chat.id, limit=50):
        if msg.from_user and msg.from_user.is_self:
            try: await msg.delete()
            except: pass

# ===============================================================
# ⚡ FITUR AUTO REPLY & WELCOME
# ===============================================================

@app.on_message(filters.me & filters.command("set", "."))
async def set_autoreply(_, message):
    if "|" not in message.text:
        return await message.edit("❌ Format: `.set jawaban | kata_kunci` ")
    try:
        _, data = message.text.split(" ", 1)
        jawaban, kunci = data.split("|")
        autoreply_db[kunci.strip().lower()] = jawaban.strip()
        await message.edit(f"✅ **Auto Reply Aktif!**\n🔑 Keyword: `{kunci.strip()}`\n💬 Balasan: `{jawaban.strip()}`")
    except: await message.edit("❌ Gagal. Cek format pemisah `|` ")

@app.on_message(filters.me & filters.command("welcome", "."))
async def welcome_toggle(_, message):
    global is_welcome_on
    status = message.command[1].lower() if len(message.command) > 1 else ""
    if status == "on":
        is_welcome_on = True
        await message.edit("✅ **Welcome Message: ON**")
    else:
        is_welcome_on = False
        await message.edit("📴 **Welcome Message: OFF**")

@app.on_message(filters.new_chat_members)
async def welcome_process(_, message):
    if is_welcome_on:
        for member in message.new_chat_members:
            await message.reply(f"Selamat Datang {member.mention}! 🔥")

# ===============================================================
# 🖼️ FITUR STIKER MAKER
# ===============================================================

@app.on_message(filters.me & filters.command("stiker", "."))
async def sticker_maker(client, message):
    reply = message.reply_to_message
    if not reply or not (reply.photo or reply.document):
        return await message.edit("❌ Balas ke foto untuk jadi stiker.")
    await message.edit("⏳ `Processing Sticker...` ")
    path = await reply.download()
    try:
        await client.send_sticker(message.chat.id, path)
        await message.delete()
    except Exception as e: await message.edit(f"❌ Error: {e}")
    if os.path.exists(path): os.remove(path)

# ===============================================================
# 📍 FITUR LOKASI & ANIMASI KURIR
# ===============================================================

@app.on_message(filters.me & filters.command("lokasi", "."))
async def lokasi_handler(client, message):
    if len(message.command) < 2: return await message.edit("❌ Contoh: `.lokasi Jakarta` ")
    query = message.text.split(None, 1)[1]
    await message.edit(f"📍 `Mencari: {query}...` ")
    try:
        location = geolocator.geocode(query)
        if location:
            await client.send_location(message.chat.id, location.latitude, location.longitude)
            await message.delete()
        else: await message.edit("❌ Gak ketemu.")
    except: await message.edit("❌ API Error.")

@app.on_message(filters.me & filters.command("em", "."))
async def em_handler(_, message):
    steps = ["📦", "🚀", "📦 — 🚀", "📦 —— 🚀", "📦 ——— 🚀", "📍 Paket Sampai!"]
    for s in steps:
        await message.edit(s)
        await asyncio.sleep(0.4)

# ===============================================================
# 🎲 FITUR GAME & FAKE STATUS
# ===============================================================

@app.on_message(filters.me & filters.command(["dadu", "slot", "basket", "bola", "panah"], "."))
async def game_handler(client, message):
    emoji = {"dadu":"🎲","slot":"🎰","basket":"🏀","bola":"⚽","pan—nah":"🎯"}.get(message.command[0])
    await message.delete()
    await client.send_dice(message.chat.id, emoji=emoji)

@app.on_message(filters.me & filters.command("fake", "."))
async def fake_handler(client, message):
    global active_fake_tasks
    if len(message.command) < 2: return await message.edit("❌ `.fake typing` / `.fake off` ")
    action_type = message.command[1].lower()
    chat_id = message.chat.id
    actions = {"typing": ChatAction.TYPING, "playing": ChatAction.PLAYING, "recording": ChatAction.RECORD_AUDIO}
    if action_type == "off":
        if chat_id in active_fake_tasks:
            active_fake_tasks[chat_id].cancel()
            active_fake_tasks.pop(chat_id, None)
            return await message.edit("📴 **Fake Status Off.**")
        return await message.edit("❌ Gak ada yang aktif.")
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

# ===============================================================
# 🤖 ASISTEN & LOGIC
# ===============================================================

@app.on_message(filters.text & ~filters.me)
async def auto_respond_process(_, message):
    msg_text = message.text.lower()
    for kunci, jawaban in autoreply_db.items():
        if kunci in msg_text: await message.reply(jawaban)

@bot.on_message(filters.command("help"))
async def bot_help(_, message):
    await message.reply(
        "📖 **USERBOT ULTIMATE CONTROL**\n"
        "━━━━━━━━━━━━━━━━━━━━\n"
        "📡 `.ping` (Latency) | `.uncast` \n"
        "📍 `.lokasi [nama]` | `.em` (Kurir)\n"
        "🎲 `.slot` `.dadu` `.basket` `.bola` `.panah` \n"
        "🎭 `.fake typing` | `.fake off` \n"
        "🖼️ `.stiker` (Reply ke foto)\n"
        "💬 `.set jawaban | kunci` \n"
        "👋 `.welcome on/off` \n"
        "🤖 `/tanya` (AI) | `/id` \n"
        "━━━━━━━━━━━━━━━━━━━━"
    )

@bot.on_message(filters.command("tanya"))
async def bot_ai(_, message):
    if len(message.command) < 2: return
    prompt = message.text.split(None, 1)[1]
    res = requests.get(f"https://api.sandipbaruwal.com/gpt4?query={prompt}").json()
    await message.reply(f"🤖 **AI:**\n\n{res['answer']}")

async def main():
    await app.start()
    await bot.start()
    print("✅ SEMUA ONLINE!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
