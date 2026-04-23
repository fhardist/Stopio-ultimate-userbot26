import os
import asyncio
import requests
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

# ===============================================================
# ⚡ FITUR DASAR & PRIVASI (AKUN UTAMA)
# ===============================================================

@app.on_message(filters.me & filters.command("ping", "."))
async def ping_handler(_, message):
    await message.edit("🚀 **Userbot Online (V2)!**\nStatus: `Stable & Complete`")

@app.on_message(filters.me & filters.command("uncast", "."))
async def uncast_handler(client, message):
    await message.edit("🧹 `Membersihkan 50 pesan Anda...` ")
    async for msg in client.get_chat_history(message.chat.id, limit=50):
        if msg.from_user and msg.from_user.is_self:
            try:
                await msg.delete()
            except:
                pass

# ===============================================================
# 📦 FITUR ANIMASI KURIR (PAKET)
# ===============================================================

@app.on_message(filters.me & filters.command("em", "."))
async def em_handler(_, message):
    animation_steps = [
        "📦", "🚀", "📦 ——— 🚀", "📦 —————— 🚀", "📦 —————————— 🚀",
        "📦 —————————————— 🚀", "📦 —————————————————— 🚀",
        "📍 Paket Sampai, Boss!"
    ]
    for step in animation_steps:
        await message.edit(step)
        await asyncio.sleep(0.5)

# ===============================================================
# 🎲 FITUR GAME & EMOJI INTERAKTIF
# ===============================================================

@app.on_message(filters.me & filters.command(["dadu", "slot", "basket", "bola", "panah"], "."))
async def game_handler(client, message: Message):
    cmd = message.command[0]
    emoji_map = {"dadu": "🎲", "slot": "🎰", "basket": "🏀", "bola": "⚽", "panah": "🎯"}
    emoji = emoji_map.get(cmd)
    await message.delete()
    await client.send_dice(message.chat.id, emoji=emoji)

# ===============================================================
# 📍 FITUR LOKASI (SHARE LOC PALSU)
# ===============================================================

@app.on_message(filters.me & filters.command("lokasi", "."))
async def lokasi_handler(client, message: Message):
    if len(message.command) < 2:
        return await message.edit("❌ Contoh: `.lokasi Sumatra` ")
    query = message.text.split(None, 1)[1]
    await message.edit(f"📍 `Memproses lokasi: {query}...` ")
    try:
        if "," in query and any(char.isdigit() for char in query):
            try:
                lat, lon = map(float, query.split(","))
                await client.send_location(message.chat.id, latitude=lat, longitude=lon)
                return await message.delete()
            except: pass
        location = geolocator.geocode(query)
        if location:
            await client.send_location(message.chat.id, latitude=location.latitude, longitude=location.longitude)
            await message.delete()
        else: await message.edit("❌ Lokasi tidak ditemukan.")
    except Exception as e: await message.edit(f"❌ Error: {str(e)}")

# ===============================================================
# 🎭 FITUR FAKE STATUS (TYPING ABADI)
# ===============================================================

@app.on_message(filters.me & filters.command("fake", "."))
async def fake_handler(client, message: Message):
    global active_fake_tasks
    if len(message.command) < 2: return await message.edit("❌ `.fake typing` / `.fake off` ")
    action_type = message.command[1].lower()
    chat_id = message.chat.id
    actions = {"typing": ChatAction.TYPING, "playing": ChatAction.PLAYING, "recording": ChatAction.RECORD_AUDIO}
    if action_type == "off":
        if chat_id in active_fake_tasks:
            active_fake_tasks[chat_id].cancel()
            active_fake_tasks.pop(chat_id, None)
            return await message.edit("📴 **Status Palsu Mati.**")
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
# 🤖 FITUR ASISTEN BOT (SECRETARY)
# ===============================================================

@bot.on_message(filters.command("start"))
async def bot_start(_, message):
    await message.reply("👋 **Halo Boss!**\nKetik `/help` buat liat semua fitur.")

@bot.on_message(filters.command("help"))
async def bot_help(_, message):
    menu_text = (
        "📖 **PANDUAN LENGKAP USERBOT**\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📍 **LOKASI & ANIMASI**\n"
        "• `.lokasi [nama]` - Kirim shareloc\n"
        "• `.em` - Animasi Kurir Paket\n\n"
        "🎲 **GAMES**\n"
        "• `.dadu` | `.slot` | `.basket` | `.bola` | `.panah` \n\n"
        "🎭 **STATUS**\n"
        "• `.fake typing` - Status ngetik terus\n"
        "• `.fake off` - Matikan status\n\n"
        "⚡ **BASIC & PRIVASI**\n"
        "• `.ping` | `.uncast` \n\n"
        "🤖 **ASISTEN (Chat Sini)**\n"
        "• `/id` | `/tanya [teks]` \n"
        "━━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(menu_text)

@bot.on_message(filters.command("id"))
async def bot_id(_, message):
    await message.reply(f"🆔 ID Anda: `{message.from_user.id}`\n📍 Chat ID: `{message.chat.id}`")

@bot.on_message(filters.command("tanya"))
async def bot_ai(_, message):
    if len(message.command) < 2: return
    prompt = message.text.split(None, 1)[1]
    wait = await message.reply("🔍 `Mikir...` ")
    try:
        res = requests.get(f"https://api.sandipbaruwal.com/gpt4?query={prompt}").json()
        await wait.edit(f"🤖 **Jawaban AI:**\n\n{res['answer']}")
    except: await wait.edit("❌ API Error.")

async def main():
    print("🚀 Memulai Userbot & Asisten...")
    await app.start()
    await bot.start()
    print("✅ SEMUA ONLINE!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
