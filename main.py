import os
import asyncio
import requests
import time
from datetime import datetime
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ChatMemberStatus
from pyrogram.handlers import MessageHandler
from pyrogram.errors import (
    FloodWait, 
    UserPrivacyRestricted, 
    UserAlreadyParticipant,
    SessionPasswordNeeded, 
    PhoneCodeInvalid, 
    PhoneCodeExpired
)
from geopy.geocoders import Nominatim
from dotenv import load_dotenv

load_dotenv()
start_time = datetime.now()

# ===============================================================
# ⚙️ KONFIGURASI MULTI-ACCOUNT (MAX 25 SLOT)
# ===============================================================
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# List untuk menampung semua akun userbot yang aktif
active_ubots = []
login_steps = {} # State temporary untuk modul /addslot

# Load Asisten Bot (Ditaruh di atas agar bisa dipakai modul login)
bot = Client(
    "asisten_bot", 
    api_id=API_ID, 
    api_hash=API_HASH, 
    bot_token=BOT_TOKEN,
    ipv6=False
)

geolocator = Nominatim(user_agent="my_userbot_2026")
active_fake_tasks, autoreply_db = {}, {}
is_welcome_on = False

# ===============================================================
# 🛠️ MODUL 1: SUNTIK & SCRAPER MASSAL (MANAJEMEN GRUP)
# ===============================================================
async def suntik_member(client, message):
    chat_id = message.chat.id
    if len(message.command) < 2:
        return await message.edit("❌ Format: `.suntik @username_target`")
        
    user_target = message.command[1]
    await message.edit(f"⏳ Akun [{client.name}] mencoba menyuntik {user_target}...")
    try:
        await client.add_chat_members(chat_id, user_target)
        await message.edit(f"✅ Akun [{client.name}] sukses masukin {user_target}!")
    except FloodWait as e:
        await message.edit(f"⚠️ Kena Limit! Akun ini kudu tidur {e.value} detik.")
    except UserPrivacyRestricted:
        await message.edit("❌ Gagal: Target ngunci privasi kontaknya.")
    except UserAlreadyParticipant:
        await message.edit("ℹ️ Target udah ada di grup ini.")
    except Exception as e:
        await message.edit(f"❌ Error: {e}")

async def scrape_grup_handler(client, message):
    if len(message.command) < 2:
        return await message.edit("❌ Format: `.scrape @username_grup_target`")
    target_chat = message.command[1]
    await message.edit(f"🔍 Memulai scrape member dari {target_chat}... Sabar, Bro.")
    try:
        members_found = []
        async for member in client.get_chat_members(target_chat):
            if member.user and member.user.username and not member.user.is_bot:
                members_found.append(f"@{member.user.username}")
        if not members_found:
            return await message.edit("❌ Gagal scraping atau gak ada member dengan username.")
        with open("members.txt", "w") as f:
            f.write("\n".join(members_found))
        await message.edit(f"✅ **Scrape Selesai!**\n👤 Total Dapet: `{len(members_found)}` username\n💾 Tersimpan di: `members.txt`\n👉 Ketik `.suntikmassal` di grup lu!")
    except Exception as e:
        await message.edit(f"❌ Gagal Scrape: {e}\nPastiin akun utama/kloningan ini udah join ke grup target.")

async def start_suntik_massal(client, message):
    chat_id = message.chat.id
    if not os.path.exists("members.txt"):
        return await message.edit("❌ File `members.txt` gak ketemu! Ketik `.scrape` dulu, Bro.")
    with open("members.txt", "r") as f:
        targets = [line.strip() for line in f.readlines() if line.strip()]
    total_target = len(targets)
    total_akun = len(active_ubots)
    if total_target == 0:
        return await message.edit("❌ File `members.txt` kosong, Bro!")
    await message.edit(f"🚀 **OPERASI MILITER DIMULAI!**\n🎯 Target Suntik: `{total_target}` orang\n🤖 Pasukan: `{total_akun}` Ubot\n⚠️ *Berjalan di background log...*")
    
    success_count, fail_count = 0, 0
    for index, username in enumerate(targets):
        akun_index = index % total_akun
        worker_ubot = active_ubots[akun_index]
        try:
            await worker_ubot.add_chat_members(chat_id, username)
            success_count += 1
            await asyncio.sleep(10) # Jeda aman anti-banned
        except FloodWait as e:
            await asyncio.sleep(2)
            fail_count += 1
            continue
        except (UserPrivacyRestricted, UserAlreadyParticipant):
            fail_count += 1
            continue
        except Exception:
            fail_count += 1
            continue
    await client.send_message(chat_id, f"🏁 **SUNTIK MASSAL FINISH!**\n━━━━━━━━━━━━━━━━━━━━\n✅ Sukses: `{success_count}` member\n❌ Gagal/Skip: `{fail_count}` member\n━━━━━━━━━━━━━━━━━━━━")

# ===============================================================
# 🛠️ MODUL 2: GLOBAL ACTIONS & PRIVASI (JARINGAN SERENTAK)
# ===============================================================
async def global_broadcast_handler(client, message):
    if len(message.command) < 2 and not message.reply_to_message:
        return await message.edit("❌ Format: `.gcast [pesan]` atau reply ke media.")
    await message.edit("📢 `Memulai Global Broadcast...` ")
    grup_terhitung = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                if message.reply_to_message:
                    await message.reply_to_message.forward(dialog.chat.id)
                else:
                    pesan_gcast = message.text.split(None, 1)[1]
                    await client.send_message(dialog.chat.id, pesan_gcast)
                grup_terhitung += 1
                await asyncio.sleep(0.3)
            except: continue
    await message.edit(f"✅ **Gcast Selesai!**\n📦 Terkirim ke `{grup_terhitung}` grup via [{client.name}].")

async def global_ban_handler(client, message):
    reply = message.reply_to_message
    if not reply: return await message.edit("❌ Reply ke orang yang mau di-GBAN!")
    target_user = reply.from_user
    await message.edit(f"🔨 `Memproses GBAN untuk {target_user.first_name}...` ")
    grup_banned = 0
    async for dialog in client.get_dialogs():
        if dialog.chat.type in ["group", "supergroup"]:
            try:
                await client.ban_chat_member(dialog.chat.id, target_user.id)
                grup_banned += 1
            except: continue
    await message.edit(f"⛔ **GLOBAL BAN SUCCESS**\n👤 Target: `{target_user.first_name}`\n🆔 ID: `{target_user.id}`\n🏢 Di-ban dari: `{grup_banned}` grup!")

async def block_user_handler(client, message):
    reply = message.reply_to_message
    if not reply and len(message.command) < 2: return await message.edit("❌ Reply target atau ketik `.block @username`")
    target = reply.from_user.id if reply else message.command[1]
    try:
        await client.block_user(target)
        await message.edit("🔒 **User berhasil diblokir!**")
    except Exception as e: await message.edit(f"❌ Gagal: {e}")

async def unblock_user_handler(client, message):
    reply = message.reply_to_message
    if not reply and len(message.command) < 2: return await message.edit("❌ Reply target atau ketik `.unblock @username`")
    target = reply.from_user.id if reply else message.command[1]
    try:
        await client.unblock_user(target)
        await message.edit("🔓 **User berhasil dibuka blokirnya!**")
    except Exception as e: await message.edit(f"❌ Gagal: {e}")

# ===============================================================
# 🛠️ MODUL 3: PRODUCTIVITY TOOLS (INTEL, SCAN & SYSTEM)
# ===============================================================
async def ping_handler(client, message):
    start = time.time()
    await message.edit("🚀 `Pinging...` ")
    latency = round((time.time() - start) * 1000, 2)
    await message.edit(f"🚀 **Online!**\n📡 **Latency:** `{latency} ms`\n👤 **Akun:** `{client.name}`")

async def uptime_handler(_, message):
    now = datetime.now()
    delta = now - start_time
    uptime_str = str(delta).split('.')[0]
    await message.edit(f"⏳ **Bot Uptime:** `{uptime_str}`\n🚀 **Status:** `{len(active_ubots)} Akun Terhubung`")

async def info_handler(client, message):
    reply = message.reply_to_message
    user = reply.from_user if reply else message.from_user
    info_text = (
        f"👤 **USER INFORMATION**\n━━━━━━━━━━━━━━━━\n"
        f"🆔 **ID:** `{user.id}`\n👤 **Name:** `{user.first_name}`\n"
        f"🏷️ **Username:** `@{user.username}`\n🤖 **Is Bot:** `{'Yes' if user.is_bot else 'No'}`\n"
        f"Premium: `{'Yes' if user.is_premium else 'No'}\n━━━━━━━━━━━━━━━━"
    )
    await message.edit(info_text)

async def ocr_handler(client, message):
    reply = message.reply_to_message
    if not (reply and (reply.photo or reply.document)): return await message.edit("❌ **Reply ke foto, Bro!**")
    await message.edit("🔍 `Scanning text (OCR)...` ")
    path = await reply.download()
    try:
        url = "https://api.ocr.space/parse/image"
        with open(path, 'rb') as f:
            res = requests.post(url, files={'file': f}, data={'apikey': 'helloworld', 'language': 'eng'}).json()
        parsed_text = res.get("ParsedResults")[0].get("ParsedText")
        if parsed_text: await message.edit(f"📝 **Hasil Scan:**\n\n`{parsed_text}`")
        else: await message.edit("❌ Gagal membaca teks.")
    except Exception as e: await message.edit(f"❌ Error OCR: {str(e)}")
    if os.path.exists(path): os.remove(path)

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
# 🛠️ MODUL 4: DOWNLOADER & MEDIA TOOLS (STIKER, GIF & DL)
# ===============================================================
async def downloader(client, message):
    if len(message.command) < 2: return await message.edit("❌ `.dl [link]`")
    link = message.text.split(None, 1)[1]
    await message.edit("⏳ `Downloading via API...` ")
    try:
        res = requests.get(f"https://api.tiklydown.eu.org/api/download?url={link}").json()
        video_url = res.get("video", {}).get("noWatermark") or res.get("url")
        if video_url:
            await client.send_video(message.chat.id, video_url, caption="✅ Berhasil Download!")
            await message.delete()
        else: await message.edit("❌ Link gak support.")
    except: await message.edit("❌ Gagal download.")

async def sticker_maker(client, message):
    reply = message.reply_to_message
    if not reply or not (reply.photo or reply.document): return await message.edit("❌ Reply ke foto!")
    path = await reply.download()
    await client.send_sticker(message.chat.id, path)
    await message.delete()
    if os.path.exists(path): os.remove(path)

async def to_gif(client, message):
    reply = message.reply_to_message
    if not reply or not reply.video: return await message.edit("❌ Reply ke video!")
    await message.edit("🔄 `Converting to GIF...` ")
    path = await reply.download()
    await client.send_animation(message.chat.id, path)
    await message.delete()
    if os.path.exists(path): os.remove(path)

# ===============================================================
# 🛠️ MODUL 5: ANIMASI TEKS & FUN TOOLS (ANIM, EM & LOKASI)
# ===============================================================
async def anim_handler(_, message):
    # Fitur .anim (animasi teks mengetik berjalan khas ubot)
    if len(message.command) < 2: return await message.edit("❌ Format: `.anim [teks]`")
    teks_asal = message.text.split(None, 1)[1]
    tampung = ""
    for char in teks_asal:
        tampung += char
        try:
            await message.edit(f"{tampung} ▒")
            await asyncio.sleep(0.1)
        except: pass
    await message.edit(teks_asal)

async def sangmata_handler(client, message):
    reply = message.reply_to_message
    if not reply: return await message.edit("❌ Reply orangnya!")
    user_id = reply.from_user.id
    await message.edit("🔍 `Checking history...` ")
    await client.send_message("SangMata_BOT", f"/search_id {user_id}")
    await asyncio.sleep(2)
    async for sg_msg in client.get_chat_history("SangMata_BOT", limit=1):
        await message.edit(f"🎭 **Riwayat Nama:**\n\n{sg_msg.text}")

async def em_handler(_, message):
    for s in ["📦", "🚀", "📦 — 🚀", "📦 —— 🚀", "📍 Paket Sampai!"]:
        await message.edit(s)
        await asyncio.sleep(0.4)

async def send_location_handler(client, message):
    if len(message.command) < 2: return await message.edit("❌ Format: `.lokasi [nama tempat]`")
    address = message.text.split(None, 1)[1]
    await message.edit(f"🔍 `Mencari lokasi: {address}...` ")
    try:
        location = geolocator.geocode(address)
        if location:
            await client.send_location(message.chat.id, location.latitude, location.longitude)
            await message.delete()
        else: await message.edit("❌ Lokasi gak ketemu, Bro!")
    except Exception as e: await message.edit(f"❌ Error Geopy: {str(e)}")

async def fake_location_handler(client, message):
    if len(message.command) < 3: return await message.edit("❌ Format: `.fakeloc [lat] [long]`")
    try:
        lat, lon = float(message.command[1]), float(message.command[2])
        await client.send_location(message.chat.id, lat, lon)
        await message.delete()
    except: await message.edit("❌ Masukin angka koordinat yang bener!")

# ===============================================================
# 🛠️ MODUL 6: GAME EMOTICON & GAME INTERNAL SYSTEM
# ===============================================================
async def game_handler(client, message):
    # Menghandle: .dadu, .slot, .basket, .bola, .panah
    cmd = message.command[0].lower()
    emoji = {"dadu":"🎲","slot":"🎰","basket":"🏀","bola":"⚽","panah":"🎯"}.get(cmd)
    if emoji:
        await message.delete()
        await client.send_dice(message.chat.id, emoji=emoji)

# ===============================================================
# 🛠️ MODUL 7: FAKE STATUS & AUTOMATION ENGINE
# ===============================================================
async def fake_handler(client, message):
    global active_fake_tasks
    if len(message.command) < 2: 
        return await message.edit("❌ `.fake [typing/playing/recording/off]`")
    
    action_type = message.command[1].lower()
    chat_id = message.chat.id
    actions = {"typing": ChatAction.TYPING, "playing": ChatAction.PLAYING, "recording": ChatAction.RECORD_AUDIO}
    
    if action_type == "off":
        if chat_id in active_fake_tasks:
            active_fake_tasks[chat_id].cancel()
            active_fake_tasks.pop(chat_id, None)
            return await message.edit("📴 **Fake Status Off.**")
        return await message.edit("❌ Gak ada status fake yang aktif disini.")
        
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

async def set_reply(_, message):
    try:
        _, data = message.text.split(" ", 1)
        jawaban, kunci = data.split("|")
        autoreply_db[kunci.strip().lower()] = jawaban.strip()
        await message.edit(f"✅ Auto Reply Ditambahkan: `{kunci.strip()}`")
    except: await message.edit("❌ Format: `.set jawaban | kata_kunci` ")

async def reset_reply(_, message):
    autoreply_db.clear()
    await message.edit("🗑️ Seluruh database Auto Reply direset!")

async def welcome_toggle(_, message):
    global is_welcome_on
    if len(message.command) < 2: return await message.edit("❌ `.welcome on` / `.welcome off` ")
    is_welcome_on = (message.command[1].lower() == "on")
    await message.edit(f"👋 Welcome Message Status: {'ON' if is_welcome_on else 'OFF'}")

# ===============================================================
# 🛠️ FUNGSI INJEKSI HANDLER (PENGIKAT FITUR KE SEMUA AKUN)
# ===============================================================
def register_all_handlers(client_instance):
    # Bind Modul 1: Manajemen Grup
    client_instance.add_handler(MessageHandler(suntik_member, filters.me & filters.command("suntik", ".")))
    client_instance.add_handler(MessageHandler(scrape_grup_handler, filters.me & filters.command("scrape", ".")))
    client_instance.add_handler(MessageHandler(start_suntik_massal, filters.me & filters.command("suntikmassal", ".")))
    
    # Bind Modul 2: Global Actions
    client_instance.add_handler(MessageHandler(global_broadcast_handler, filters.me & filters.command("gcast", ".")))
    client_instance.add_handler(MessageHandler(global_ban_handler, filters.me & filters.command("gban", ".")))
    client_instance.add_handler(MessageHandler(block_user_handler, filters.me & filters.command("block", ".")))
    client_instance.add_handler(MessageHandler(unblock_user_handler, filters.me & filters.command("unblock", ".")))
    
    # Bind Modul 3 & 4: Intel, System & Media Download
    client_instance.add_handler(MessageHandler(ping_handler, filters.me & filters.command("ping", ".")))
    client_instance.add_handler(MessageHandler(uptime_handler, filters.me & filters.command("uptime", ".")))
    client_instance.add_handler(MessageHandler(info_handler, filters.me & filters.command("info", ".")))
    client_instance.add_handler(MessageHandler(ocr_handler, filters.me & filters.command("ocr", ".")))
    client_instance.add_handler(MessageHandler(admin_tools, filters.me & filters.command(["kick", "ban", "mute"], ".")))
    client_instance.add_handler(MessageHandler(downloader, filters.me & filters.command("dl", ".")))
    client_instance.add_handler(MessageHandler(sticker_maker, filters.me & filters.command("stiker", ".")))
    client_instance.add_handler(MessageHandler(to_gif, filters.me & filters.command("togif", ".")))
    
    # Bind Modul 5 & 6: Animasi, Fun & Game Emo
    client_instance.add_handler(MessageHandler(anim_handler, filters.me & filters.command("anim", ".")))
    client_instance.add_handler(MessageHandler(sangmata_handler, filters.me & filters.command("sg", ".")))
    client_instance.add_handler(MessageHandler(em_handler, filters.me & filters.command("em", ".")))
    client_instance.add_handler(MessageHandler(send_location_handler, filters.me & filters.command("lokasi", ".")))
    client_instance.add_handler(MessageHandler(fake_location_handler, filters.me & filters.command("fakeloc", ".")))
    client_instance.add_handler(MessageHandler(game_handler, filters.me & filters.command(["dadu", "slot", "basket", "bola", "panah"], ".")))
    
    # Bind Modul 7: Fake Status & Otomatisasi
    client_instance.add_handler(MessageHandler(fake_handler, filters.me & filters.command("fake", ".")))
    client_instance.add_handler(MessageHandler(set_reply, filters.me & filters.command("set", ".")))
    client_instance.add_handler(MessageHandler(reset_reply, filters.me & filters.command("reset", ".")))
    client_instance.add_handler(MessageHandler(welcome_toggle, filters.me & filters.command("welcome", ".")))

# ===============================================================
# 🚀 LOADER SEEDER DATA AKUN (SINKRONISASI SLOT 1 - 25)
# ===============================================================

# 1. Load Akun Utama (Slot 1)
MAIN_SESSION = os.getenv("STRING_SESSION")
if MAIN_SESSION:
    app = Client("my_userbot_main", session_string=MAIN_SESSION, api_id=API_ID, api_hash=API_HASH, ipv6=False)
    register_all_handlers(app)
    active_ubots.append(app)
else:
    print("⚠️ WARNING: STRING_SESSION utama kosong!")

# 2. Looping Slot Otomatis untuk Akun Kloningan (Slot 2 sampai 25)
for i in range(2, 26):
    session_env_name = f"SESSION_{i}"
    session_string = os.getenv(session_env_name)
    if session_string:
        print(f"📦 Slot {i} Terisi! Menyiapkan Akun Kloningan_{i}...")
        cloning_client = Client(f"ubot_slot_{i}", session_string=session_string, api_id=API_ID, api_hash=API_HASH, ipv6=False)
        register_all_handlers(cloning_client)
        active_ubots.append(cloning_client)

# Global Event Listeners untuk Event Chat (Bawaan Lama Lu)
@Client.on_message(filters.new_chat_members)
async def welcome_process(_, message):
    if is_welcome_on:
        for m in message.new_chat_members: await message.reply(f"Selamat Datang {m.mention}! 🔥")

@Client.on_message(filters.text & ~filters.me)
async def auto_respond(_, message):
    for k, v in autoreply_db.items():
        if k in message.text.lower(): await message.reply(v)


# ===============================================================
# 🤖 MODUL 8: BOT ASISTEN & INTERACTIVE CHAT LOGIN
# ===============================================================
@bot.on_message(filters.command("addslot"))
async def add_slot_start(client, message):
    if len(message.command) < 2:
        return await message.reply("❌ **Format salah!**\nContoh: `/addslot +62812345678` ")
    
    phone_number = message.command[1].replace(" ", "")
    wait_msg = await message.reply(f"⏳ `Menghubungkan ke Telegram Server untuk nomor {phone_number}...` ")
    temp_client = Client("temp_login", api_id=API_ID, api_hash=API_HASH, in_memory=True)
    
    try:
        await temp_client.connect()
        code_hash = await temp_client.send_code(phone_number)
        login_steps[message.from_user.id] = {
            "client": temp_client, "phone": phone_number, "hash": code_hash.phone_code_hash, "step": "wait_otp"
        }
        await wait_msg.edit(f"📩 **Kode OTP telah dikirim oleh Telegram!**\n\n📱 Nomor: `{phone_number}`\n👉 Silahkan **REPLY** pesan ini dengan kode OTP-nya.")
    except Exception as e:
        await wait_msg.edit(f"❌ **Gagal Request OTP:** `{str(e)}`")
        if temp_client.is_connected: await temp_client.disconnect()

@bot.on_message(filters.reply & filters.text)
async def login_input_handler(client, message):
    user_id = message.from_user.id
    if user_id not in login_steps: return
    user_data = login_steps[user_id]
    temp_client = user_data["client"]
    input_text = message.text.strip()

    if user_data["step"] == "wait_otp":
        wait_msg = await message.reply("⏳ `Memverifikasi kode OTP...` ")
        try:
            await temp_client.sign_in(phone_number=user_data["phone"], phone_code_hash=user_data["hash"], phone_code=input_text)
            string_session = await temp_client.export_session_string()
            await temp_client.disconnect()
            login_steps.pop(user_id, None)
            return await wait_msg.edit(f"🎉 **SUKSES LOGIN!**\n\n⬇️ **STRING SESSION LU:**\n`{string_session}`\n\n🛠 **Langkah Terakhir:**\nCopas kode panjang di atas ke Tab **Variables Railway** dengan nama slot kosong (Contoh: `SESSION_3`). Bot otomatis reload!")
        except SessionPasswordNeeded:
            login_steps[user_id]["step"] = "wait_password"
            await wait_msg.edit("🔒 **Akun ini menggunakan 2FA Password!**\n👉 Silahkan **REPLY** pesan ini dengan password akun tersebut.")
        except (PhoneCodeInvalid, PhoneCodeExpired):
            await wait_msg.edit("❌ Kodenya salah/expired, Bro. Silahkan panggil `/addslot` lagi.")
            await temp_client.disconnect()
            login_steps.pop(user_id, None)
        except Exception as e:
            await wait_msg.edit(f"❌ Error: `{str(e)}`")
            await temp_client.disconnect()
            login_steps.pop(user_id, None)

    elif user_data["step"] == "wait_password":
        wait_msg = await message.reply("⏳ `Memverifikasi Password 2FA...` ")
        try:
            await temp_client.check_password(password=input_text)
            string_session = await temp_client.export_session_string()
            await temp_client.disconnect()
            login_steps.pop(user_id, None)
            await wait_msg.edit(f"🎉 **SUKSES LOGIN DENGAN 2FA!**\n\n⬇️ **STRING SESSION LU:**\n`{string_session}`\n\n🛠 Paste ke Variable Railway dengan slot kosong, gass! 🔥")
        except Exception as e:
            await wait_msg.edit(f"❌ Password salah atau Error: `{str(e)}`. Proses dibatalkan.")
            await temp_client.disconnect()
            login_steps.pop(user_id, None)

# ===============================================================
# 🤖 MODUL 9: ASISTEN PANDUAN UTUH (HELP MENU PERINTAH LENGKAP)
# ===============================================================
@bot.on_message(filters.command("help"))
async def bot_help(_, message):
    help_text = (
        "👑 **USERBOT ULTIMATE V4 CONTROL CENTER** 👑\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "Prefix Perintah: Gunakan titik `.` di depan kode untuk semua Ubot.\n\n"
        
        "📦 **1. GRUP & MANAJEMEN INJECT**\n"
        "• `.scrape @grup` : Ambil data member target grup lain ➡️ txt.\n"
        "• `.suntikmassal` : 25 Akun serentak menyuntik data dari txt.\n"
        "• `.suntik @user` : Memasukkan 1 target spesifik ke dalam grup.\n\n"
        
        "📢 **2. JARINGAN GLOBAL & PRIVASI**\n"
        "• `.gcast [teks]` : Broadcast chat ke seluruh grup via ubot.\n"
        "• `.gban` (Reply) : Banned user tersebut dari seluruh grup lu sekaligus.\n"
        "• `.block` (Reply/Username) : Blokir PM/Kontak target instan.\n"
        "• `.unblock` (Reply/Username) : Buka blokir kontak target.\n\n"
        
        "📡 **3. INTEL, ADM & SYSTEM PRODUCTIVITY**\n"
        "• `.ping` : Menguji kecepatan latency respon server (ms).\n"
        "• `.uptime` : Melihat lama bot berjalan aktif di Railway.\n"
        "• `.info` (Reply) : Mengintip detail profil, id, & status premium user.\n"
        "• `.ocr` (Reply Foto) : Mengonversi text gambar menjadi text chat.\n"
        "• `.kick` / `.ban` / `.mute` : Alat admin instan (Wajib reply target).\n\n"
        
        "🎬 **4. MEDIA DOWNLOADER & CONVERTER**\n"
        "• `.dl [link]` : Download otomatis video sosmed tanpa watermark.\n"
        "• `.stiker` (Reply Foto) : Mengonversi gambar menjadi stiker Telegram.\n"
        "• `.togif` (Reply Video) : Mengubah file video pendek menjadi format GIF.\n\n"
        
        "🎭 **5. ANIMASI, FUN EFFECTS & MAP**\n"
        "• `.anim [teks]` : Efek ketikan teks berjalan keren (*typing effect*).\n"
        "• `.em` : Animasi pengiriman paket kurir instan.\n"
        "• `.sg` (Reply) : Cek histori perubahan username via SangMata.\n"
        "• `.lokasi [nama]` : Mengirim maps koordinat via pencarian nama.\n"
        "• `.fakeloc [lat] [lon]` : Mengirim maps via titik koordinat palsu.\n\n"
        
        "🎰 **6. GAME INTERNAL & AUTOMATION**\n"
        "• `.dadu` / `.slot` / `.basket` / `.bola` / `.panah` : Main game emo.\n"
        "• `.fake typing/playing/recording` : Manipulasi status aktif chat.\n"
        "• `.fake off` : Mematikan manipulasi status chat.\n"
        "• `.set balasan | kata` : Membuat auto-respond bot jika dipicu kata.\n"
        "• `.reset` : Menghapus semua database kata kunci auto reply.\n"
        "• `.welcome on/off` : Mengaktifkan sambutan otomatis member baru.\n\n"
        
        "🤖 **7. OPERASI INTERNAL BOT ASISTEN**\n"
        "• `/addslot [no_hp]` : Login akun kloningan langsung lewat HP.\n"
        "• `/id` : Membaca ID User Anda dan ID Group Chat saat ini.\n"
        "• `/tanya [prompt]` : Bertanya kecerdasan buatan AI GPT-4."
    )
    await message.reply(help_text)

@bot.on_message(filters.command("id"))
async def bot_id(_, message):
    await message.reply(f"🆔 ID Anda: `{message.from_user.id}`\n📍 Chat ID: `{message.chat.id}`")

@bot.on_message(filters.command("tanya"))
async def bot_ai(_, message):
    if len(message.command) < 2: return await message.reply("Contoh: `/tanya halo` ")
    prompt = message.text.split(None, 1)[1]
    wait = await message.reply("🔍 `Asisten sedang mencari jawaban...` ")
    try:
        res = requests.get(f"https://api.sandipbaruwal.com/gpt4?query={prompt}").json()
        await wait.edit(f"🤖 **Jawaban AI:**\n\n{res['answer']}")
    except: await wait.edit("❌ Gagal terhubung ke AI.")

# ===============================================================
# 🤖 LAUNCH SYSTEM (FIX ENGINE SHUTDOWN & PERSISTENCE)
# ===============================================================
async def main():
    print("⚡ Memulai sinkronisasi Multi-Account...")
    await bot.start()
    print("✅ Asisten Bot Telah Aktif!")
    
    started_ubots = []
    for ubot in active_ubots:
        try:
            await ubot.start()
            print(f"✅ Userbot [{ubot.name}] Berhasil Online!")
            started_ubots.append(ubot)
        except Exception as e:
            print(f"❌ Gagal menyalakan slot [{ubot.name}]: {e}")
            
    print(f"🔥 TOTAL {len(started_ubots)} AKAN USERBOT STANDBY DI VPS!")
    await idle()
    
    print("👋 Mematikan seluruh sistem koneksi...")
    await bot.stop()
    for ubot in started_ubots:
        try: await ubot.stop()
        except: pass

if __name__ == "__main__":
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("🛑 Bot dihentikan secara manual.")
