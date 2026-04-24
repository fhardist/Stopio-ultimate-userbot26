import os, asyncio, requests, time
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ChatMemberStatus
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv()

# ===============================================================
# ⚙️ KONFIGURASI
# ===============================================================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")
BOT_TOKEN = os.getenv("BOT_TOKEN")

app = Client("my_userbot", session_string=STRING_SESSION, api_id=API_ID, api_hash=API_HASH)
bot = Client("asisten_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

geolocator = Nominatim(user_agent="my_userbot_2026")
active_fake_tasks, autoreply_db = {}, {}
is_welcome_on = False

# ===============================================================
# 🛠️ MODUL 1: ADMIN & GROUP MGMT (KICK, BAN, MUTE)
# ===============================================================
@app.on_message(filters.me & filters.command(["kick", "ban", "mute"], "."))
async def admin_tools(client, message):
    cmd = message.command[0]
    reply = message.reply_to_message
    if not reply: return await message.edit("❌ Reply ke orangnya!")
    
    user_id = reply.from_user.id
    try:
        if cmd == "kick":
            await client.ban_chat_member(message.chat.id, user_id)
            await client.unban_chat_member(message.chat.id, user_id)
            await message.edit(f"🚀 **{reply.from_user.first_name} ditendang!**")
        elif cmd == "ban":
            await client.ban_chat_member(message.chat.id, user_id)
            await message.edit(f"🚫 **{reply.from_user.first_name} di-banned!**")
        elif cmd == "mute":
            await client.restrict_chat_member(message.chat.id, user_id, permissions=None)
            await message.edit(f"🙊 **{reply.from_user.first_name} dibisukan!**")
    except Exception as e: await message.edit(f"❌ Error: {e}")

# ===============================================================
# 📥 MODUL 2: DOWNLOADER (SOSMED)
# ===============================================================
@app.on_message(filters.me & filters.command("dl", "."))
async def downloader(client, message):
    if len(message.command) < 2: return await message.edit("❌ `.dl [link]`")
    link = message.text.split(None, 1)[1]
    await message.edit("⏳ `Downloading via API...` ")
    try:
        # Menggunakan API pihak ketiga gratis untuk TikTok/IG/YT
        res = requests.get(f"https://api.tiklydown.eu.org/api/download?url={link}").json()
        video_url = res.get("video", {}).get("noWatermark") or res.get("url")
        if video_url:
            await client.send_video(message.chat.id, video_url, caption="✅ Berhasil Download!")
            await message.delete()
        else: await message.edit("❌ Link gak support.")
    except: await message.edit("❌ Gagal download.")

# ===============================================================
# 🎨 MODUL 3: MEDIA TOOLS (STIKER, GIF, INFO)
# ===============================================================
@app.on_message(filters.me & filters.command("stiker", "."))
async def sticker_maker(client, message):
    reply = message.reply_to_message
    if not reply or not (reply.photo or reply.document): return await message.edit("❌ Reply ke foto!")
    path = await reply.download()
    await client.send_sticker(message.chat.id, path)
    await message.delete()
    if os.path.exists(path): os.remove(path)

@app.on_message(filters.me & filters.command("togif", "."))
async def to_gif(client, message):
    reply = message.reply_to_message
    if not reply or not reply.video: return await message.edit("❌ Reply ke video!")
    await message.edit("🔄 `Converting to GIF...` ")
    path = await reply.download()
    await client.send_animation(message.chat.id, path)
    await message.delete()
    if os.path.exists(path): os.remove(path)

# ===============================================================
# 📡 FITUR ASLI (PING, SG, LOKASI, EM, GAMES, FAKE)
# ===============================================================
@app.on_message(filters.me & filters.command("ping", "."))
async def ping_handler(_, message):
    start = time.time()
    await message.edit("🚀 `Pinging...` ")
    latency = round((time.time() - start) * 1000, 2)
    await message.edit(f"🚀 **Online!**\n📡 **Latency:** `{latency} ms`\n👤 **Status:** `Admin IT Mode` ")

@app.on_message(filters.me & filters.command("sg", "."))
async def sangmata_handler(client, message):
    reply = message.reply_to_message
    if not reply: return await message.edit("❌ Reply orangnya!")
    user_id = reply.from_user.id
    await message.edit("🔍 `Checking history...` ")
    await client.send_message("SangMata_BOT", f"/search_id {user_id}")
    await asyncio.sleep(2)
    async for sg_msg in client.get_chat_history("SangMata_BOT", limit=1):
        await message.edit(f"🎭 **Riwayat Nama:**\n\n{sg_msg.text}")

@app.on_message(filters.me & filters.command("em", "."))
async def em_handler(_, message):
    for s in ["📦", "🚀", "📦 — 🚀", "📦 —— 🚀", "📍 Paket Sampai!"]:
        await message.edit(s)
        await asyncio.sleep(0.4)

@app.on_message(filters.me & filters.command(["dadu", "slot", "basket", "bola", "panah"], "."))
async def game_handler(client, message):
    emoji = {"dadu":"🎲","slot":"🎰","basket":"🏀","bola":"⚽","panah":"🎯"}.get(message.command[0])
    await message.delete()
    await client.send_dice(message.chat.id, emoji=emoji)

# ===============================================================
# 💬 AUTO REPLY & WELCOME (DENGAN FIX)
# ===============================================================
@app.on_message(filters.me & filters.command("set", "."))
async def set_reply(_, message):
    try:
        _, data = message.text.split(" ", 1)
        jawaban, kunci = data.split("|")
        autoreply_db[kunci.strip().lower()] = jawaban.strip()
        await message.edit(f"✅ Auto Reply: `{kunci.strip()}`")
    except: await message.edit("❌ `.set jawaban | kunci` ")

@app.on_message(filters.me & filters.command("reset", "."))
async def reset_reply(_, message):
    autoreply_db.clear()
    await message.edit("🗑️ Auto Reply direset!")

@app.on_message(filters.me & filters.command("welcome", "."))
async def welcome_toggle(_, message):
    global is_welcome_on
    is_welcome_on = (message.command[1].lower() == "on") if len(message.command) > 1 else False
    await message.edit(f"👋 Welcome: {'ON' if is_welcome_on else 'OFF'}")

@app.on_message(filters.new_chat_members)
async def welcome_process(_, message):
    if is_welcome_on:
        for m in message.new_chat_members:
            await message.reply(f"Selamat Datang {m.mention}! 🔥")

@app.on_message(filters.text & ~filters.me)
async def auto_respond(_, message):
    for k, v in autoreply_db.items():
        if k in message.text.lower(): await message.reply(v)

# ===============================================================
# 🤖 ASISTEN & LAUNCH
# ===============================================================

@bot.on_message(filters.command("help"))
async def bot_help(_, message):
    help_text = (
        "✨ **USERBOT ULTIMATE V4 CONTROL** ✨\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📡 **INTEL & KONEKSI**\n"
        "• `.ping` : Cek latency server (ms).\n"
        "• `.sg` : Cek riwayat nama (Reply target).\n"
        "• `.uncast` : Hapus 50 pesan lu di chat.\n\n"
        "🔨 **ADMIN GRUP** (Reply Target)\n"
        "• `.kick` : Tendang member dari grup.\n"
        "• `.ban`  : Banned member permanen.\n"
        "• `.mute` : Bisukan member (Read-only).\n\n"
        "📥 **DOWNLOAD & MEDIA**\n"
        "• `.dl [link]` : Download TikTok/IG/YT.\n"
        "• `.stiker` : Foto -> Stiker (Reply foto).\n"
        "• `.togif`  : Video -> GIF (Reply video).\n\n"
        "⚙️ **OTOMATISASI**\n"
        "• `.set [jawab] | [kunci]` : Auto Reply.\n"
        "• `.reset` : Hapus semua daftar Auto Reply.\n"
        "• `.welcome on/off` : Sapaan member baru.\n\n"
        "🎭 **STATUS & GAMES**\n"
        "• `.fake [typing/off]` : Status palsu.\n"
        "• `.em` : Animasi kurir paket.\n"
        "• `.slot` | `.dadu` | `.bola` : Games.\n\n"
        "🤖 **ASISTEN AI**\n"
        "• `/tanya [teks]` : Tanya AI GPT-4.\n"
        "• `/id` : Cek ID User / ID Grup.\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💬 *Gunakan prefix titik (.) untuk Userbot*"
    )
    await message.reply(help_text)

async def main():
    await app.start()
    await bot.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
