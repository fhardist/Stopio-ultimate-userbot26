import os
import asyncio
import requests
import time
from pyrogram import Client, filters, idle
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ChatMemberStatus
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv()
start_time = datetime.now()

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
# 🛠️ MODUL PRODUCTIVITY (OCR & INFO)
# ===============================================================

@app.on_message(filters.me & filters.command("uptime", "."))
async def uptime_handler(_, message):
    now = datetime.now()
    delta = now - start_time
    # Menghitung durasi bot online
    uptime_str = str(delta).split('.')[0]
    await message.edit(f"⏳ **Bot Uptime:** `{uptime_str}`\n🚀 **Status:** `Stable`")

@app.on_message(filters.me & filters.command("info", "."))
async def info_handler(client, message):
    reply = message.reply_to_message
    user = reply.from_user if reply else message.from_user
    # Cek detail user buat kebutuhan IT/Admin
    info_text = (
        f"👤 **USER INFORMATION**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** `{user.id}`\n"
        f"👤 **Name:** `{user.first_name}`\n"
        f"🏷️ **Username:** `@{user.username}`\n"
        f"🤖 **Is Bot:** `{'Yes' if user.is_bot else 'No'}`\n"
        f"Premium: `{'Yes' if user.is_premium else 'No'}`\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    await message.edit(info_text)

@app.on_message(filters.me & filters.command("ocr", "."))
async def ocr_handler(client, message):
    reply = message.reply_to_message
    if not (reply and (reply.photo or reply.document)):
        return await message.edit("❌ **Reply ke foto yang ada teksnya, Bro!**")
    
    await message.edit("🔍 `Scanning text (OCR)...` ")
    path = await reply.download()
    
    try:
        # Menggunakan API OCR gratis (OCR.space)
        # Note: Ini basic API, kalau mau lebih powerfull bisa daftar API Key sendiri
        url = "https://api.ocr.space/parse/image"
        with open(path, 'rb') as f:
            res = requests.post(url, files={'file': f}, data={'apikey': 'helloworld', 'language': 'eng'}).json()
        
        parsed_text = res.get("ParsedResults")[0].get("ParsedText")
        if parsed_text:
            await message.edit(f"📝 **Hasil Scan:**\n\n`{parsed_text}`")
        else:
            await message.edit("❌ Gagal baca teks, pastikan gambar jelas.")
    except Exception as e:
        await message.edit(f"❌ Error OCR: {str(e)}")
    
    if os.path.exists(path): os.remove(path)

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
# 📍 MODUL LOKASI (REAL & FAKE GPS)
# ===============================================================

@app.on_message(filters.me & filters.command("lokasi", "."))
async def send_location_handler(client, message):
    if len(message.command) < 2:
        return await message.edit("❌ Format: `.lokasi [nama tempat]`\nContoh: `.lokasi Monas`")
    
    address = message.text.split(None, 1)[1]
    await message.edit(f"🔍 `Mencari lokasi: {address}...` ")
    
    try:
        # Nyari koordinat pake geopy
        location = geolocator.geocode(address)
        if location:
            await client.send_location(
                chat_id=message.chat.id,
                latitude=location.latitude,
                longitude=location.longitude
            )
            await message.delete()
        else:
            await message.edit("❌ Lokasi gak ketemu, Bro!")
    except Exception as e:
        await message.edit(f"❌ Error Geopy: {str(e)}")

@app.on_message(filters.me & filters.command("fakeloc", "."))
async def fake_location_handler(client, message):
    # Fitur kirim lokasi statis tanpa cari nama (input Lat, Long manual)
    if len(message.command) < 3:
        return await message.edit("❌ Format: `.fakeloc [lat] [long]`")
    
    try:
        lat = float(message.command[1])
        lon = float(message.command[2])
        await client.send_location(message.chat.id, lat, lon)
        await message.delete()
    except:
        await message.edit("❌ Masukin angka koordinat yang bener!")

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
        "✨ **USERBOT ULTIMATE** ✨\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📡 **INTEL & KONEKSI**\n"
        "• `.lokasi [nama] : Kirim lokasi palsu via nama tempat.\n"
        "• `.fakeloc [lat] [long] : Kirim lokasi via koordinat.\n"
        "• `.ping`   : Cek latency server (ms).\n"
        "• `.sg`     : Cek riwayat nama (Reply).\n"
        "• `.uncast` : Hapus 50 pesan sendiri.\n\n"
        "🛠️ **SYSTEM & PRODUCTIVITY**\n"
        "• `.ocr`    : Ambil teks dari foto (Reply).\n"
        "• `.info`   : Detail profil user (Reply).\n"
        "• `.uptime` : Cek berapa lama bot ON.\n\n"
        "🔨 **ADMIN GRUP** (Reply Target)\n"
        "• `.kick`   : Tendang member.\n"
        "• `.ban`    : Banned permanen.\n"
        "• `.mute`   : Bisukan member.\n\n"
        "📥 **DOWNLOAD & MEDIA**\n"
        "• `.dl [link]` : Download TikTok/IG/YT.\n"
        "• `.stiker`    : Foto -> Stiker (Reply).\n"
        "• `.togif`     : Video -> GIF (Reply).\n\n"
        "⚙️ **OTOMATISASI**\n"
        "• `.set [jawab] | [kunci]` : Auto Reply.\n"
        "• `.del [kunci]` : Hapus 1 keyword AR.\n"
        "• `.reset`   : Reset semua Auto Reply.\n"
        "• `.welcome on/off` : Sapaan member.\n\n"
        "🎭 **STATUS & GAMES**\n"
        "• `.fake [typing/off]` : Status palsu.\n"
        "• `.em`      : Animasi kurir paket.\n"
        "• `.slot` | `.dadu` | `.bola` : Games.\n\n"
        "🤖 **ASISTEN AI**\n"
        "• `/tanya`  : Tanya AI GPT-4.\n"
        "• `/id`     : Cek ID User / Grup.\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "💬 *Gunakan prefix titik (.) untuk Userbot*"
    )
    await message.reply(help_text)

@bot.on_message(filters.command("id"))
async def bot_id(_, message):
    await message.reply(f"🆔 ID Anda: `{message.from_user.id}`\n📍 Chat ID: `{message.chat.id}`")

@bot.on_message(filters.command("tanya"))
async def bot_ai(_, message):
    if len(message.command) < 2:
        return await message.reply("Contoh: `/tanya cara masak kentang mustopa` ")
    
    prompt = message.text.split(None, 1)[1]
    wait = await message.reply("🔍 `Asisten sedang mencari jawaban...` ")
    try:
        res = requests.get(f"https://api.sandipbaruwal.com/gpt4?query={prompt}").json()
        await wait.edit(f"🤖 **Jawaban AI:**\n\n{res['answer']}")
    except:
        await wait.edit("❌ Gagal terhubung ke AI.")

async def main():
    # Menggunakan 'async with' supaya otomatis handle start & stop koneksi
    async with app:
        async with bot:
            print("✅ Userbot & Asisten Online, Bro!")
            await idle() # Ini kuncinya biar Railway nggak mutus koneksi (heartbeat)

if __name__ == "__main__":
    try:
        app.run(main())
    except KeyboardInterrupt:
        pass # Biar kalau di-stop manual nggak muncul error panjang
