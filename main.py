import os
import asyncio
import requests
from telethon import TelegramClient, events, functions, types
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from googletrans import Translator

# --- KONFIGURASI DASAR ---
load_dotenv()
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
STRING_SESSION = os.getenv("STRING_SESSION")

client = TelegramClient(STRING_SESSION, API_ID, API_HASH)
geolocator = Nominatim(user_agent="my_userbot_2026")
translator = Translator()

# Variabel Global
afk_reason = None
gban_list = []

# ================= 1. FITUR INFORMASI & SELF =================

@client.on(events.NewMessage(pattern=r'\.ping', outgoing=True))
async def ping(event):
    start = asyncio.get_event_loop().time()
    await event.edit("🚀 `Pinging...` ")
    end = asyncio.get_event_loop().time()
    ms = round((end - start) * 1000, 2)
    await event.edit(f"🚀 **Userbot Online!**\nLatency: `{ms}ms` 🟢")

@client.on(events.NewMessage(pattern=r'\.cek', outgoing=True))
async def cek_riwayat(event):
    if not event.is_reply:
        return await event.edit("❌ **Balas ke pesan target.**")
    reply = await event.get_reply_message()
    await event.edit("🔍 **Mencari riwayat nama...**")
    async with client.conversation("@SangMata_BOT") as conv:
        await conv.send_message(f"/search_id {reply.sender_id}")
        response = await conv.get_response()
        await conv.mark_read()
        await event.edit(f"📝 **Hasil Riwayat Nama:**\n\n{response.text}")

# ================= 2. FITUR ADMIN & PRIVASI (UNCAST) =================

@client.on(events.NewMessage(pattern=r'\.uncast', outgoing=True))
async def uncast_handler(event):
    await event.edit("🧹 `Uncasting...` Menghapus jejak Anda.")
    async for msg in client.iter_messages(event.chat_id, from_user="me"):
        await msg.delete()
    await event.respond("✅ **Uncast Selesai.**", delete_after=5)

@client.on(events.NewMessage(pattern=r'\.purge', outgoing=True))
async def purge_handler(event):
    reply = await event.get_reply_message()
    if not reply: return await event.edit("❌ Reply pesan awal.")
    msgs = []
    async for msg in client.iter_messages(event.chat_id, min_id=reply.id - 1):
        msgs.append(msg)
    await client.delete_messages(event.chat_id, msgs)

# ================= 3. FITUR LOKASI =================

@client.on(events.NewMessage(pattern=r'\.lokasi (.*)', outgoing=True))
async def send_custom_location(event):
    place_name = event.pattern_match.group(1)
    await event.edit(f"🔍 **Mencari:** `{place_name}`...")
    try:
        location = geolocator.geocode(place_name)
        if location:
            await event.delete()
            await client(functions.messages.SendMediaRequest(
                peer=event.chat_id,
                media=types.InputMediaGeoPoint(geo_point=types.InputGeoPoint(lat=float(location.latitude), long=float(location.longitude))),
                message=f"📍 **Lokasi:** `{location.address}`"
            ))
    except: await event.edit("❌ Gagal mencari lokasi.")

# ================= 4. FITUR FAKE STATUS & GAME =================

@client.on(events.NewMessage(pattern=r'\.fake (.*)', outgoing=True))
async def fake_action(event):
    input_str = event.pattern_match.group(1).lower()
    actions = {"typing": functions.messages.SetTypingRequest.TYPING, "playing": functions.messages.SetTypingRequest.PLAYING, "recording": functions.messages.SetTypingRequest.RECORD_AUDIO}
    if input_str in actions:
        await event.delete()
        for _ in range(5):
            await client(functions.messages.SetTypingRequest(peer=event.chat_id, action=actions[input_str]))
            await asyncio.sleep(5)

@client.on(events.NewMessage(pattern=r'\.(dadu|slot|bola)', outgoing=True))
async def game_stiker(event):
    game_map = {"dadu": "🎲", "slot": "🎰", "bola": "⚽"}
    await event.delete()
    await client(functions.messages.SendDiceRequest(peer=event.chat_id, emoji=game_map[event.pattern_match.group(1)]))

# ================= 5. FITUR CERDAS (AI & TRANSLATE) =================

@client.on(events.NewMessage(pattern=r'\.tr (.*)', outgoing=True))
async def translate_handler(event):
    dest_lang = event.pattern_match.group(1)
    reply = await event.get_reply_message()
    if reply and reply.message:
        await event.edit("🔄 `Translating...`")
        result = translator.translate(reply.message, dest=dest_lang)
        await event.edit(f"**Terjemahan ({result.dest}):**\n\n{result.text}")

@client.on(events.NewMessage(pattern=r'\.ai (.*)', outgoing=True))
async def ai_handler(event):
    prompt = event.pattern_match.group(1)
    await event.edit("🤖 `AI Thinking...`")
    try:
        res = requests.get(f"https://api.simsimi.net/v2/?text={prompt}&lc=id").json()
        await event.edit(f"🤖 **AI:**\n\n{res['success']}")
    except: await event.edit("❌ Gagal terhubung ke AI.")

print("✅ ULTIMATE USERBOT 2026 READY!")
client.start()
client.run_until_disconnected()
