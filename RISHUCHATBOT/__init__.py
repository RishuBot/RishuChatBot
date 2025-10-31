import logging
import asyncio
import uvloop

# ✅ Fix for Python 3.12 + uvloop + Abg crash
try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# Use default asyncio loop for Python 3.12 (safe mode)
asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
# ⚡ If you want uvloop’s performance, you can switch later by uncommenting:
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

import time
from pymongo import MongoClient
from Abg import patch
from RISHUCHATBOT.userbot.userbot import Userbot
from motor.motor_asyncio import AsyncIOMotorClient as MongoCli
from pyrogram import Client
from pyrogram.enums import ParseMode
import config

ID_CHATBOT = None
CLONE_OWNERS = {}

# Logging setup
logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

boot = time.time()
mongodb = MongoCli(config.MONGO_URL)
db = mongodb.Anonymous
mongo = MongoClient(config.MONGO_URL)
OWNER = config.OWNER_ID
_boot_ = time.time()

clonedb = None
def dbb():
    global db
    global clonedb
    clonedb = {}
    db = {}

cloneownerdb = db.clone_owners


# -------------------- Clone Owner Management --------------------

async def load_clone_owners():
    async for entry in cloneownerdb.find():
        bot_id = entry["bot_id"]
        user_id = entry["user_id"]
        CLONE_OWNERS[bot_id] = user_id

async def save_clonebot_owner(bot_id, user_id):
    await cloneownerdb.update_one(
        {"bot_id": bot_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

async def get_clone_owner(bot_id):
    data = await cloneownerdb.find_one({"bot_id": bot_id})
    if data:
        return data["user_id"]
    return None

async def delete_clone_owner(bot_id):
    await cloneownerdb.delete_one({"bot_id": bot_id})
    CLONE_OWNERS.pop(bot_id, None)

async def save_idclonebot_owner(clone_id, user_id):
    await cloneownerdb.update_one(
        {"clone_id": clone_id},
        {"$set": {"user_id": user_id}},
        upsert=True
    )

async def get_idclone_owner(clone_id):
    data = await cloneownerdb.find_one({"clone_id": clone_id})
    if data:
        return data["user_id"]
    return None


# -------------------- Main Bot Class --------------------

class RISHUCHATBOT(Client):
    def __init__(self):
        super().__init__(
            name="RISHUCHATBOT",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.DEFAULT,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

    async def stop(self):
        await super().stop()


# -------------------- Helper Function --------------------

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        if count < 3:
            remainder, result = divmod(seconds, 60)
        else:
            remainder, result = divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    for i in range(len(time_list)):
        time_list[i] = str(time_list[i]) + time_suffix_list[i]
    if len(time_list) == 4:
        ping_time += time_list.pop() + ", "
    time_list.reverse()
    ping_time += ":".join(time_list)
    return ping_time


# -------------------- Initialize Main Bot and Userbot --------------------

RISHUCHATBOT = RISHUCHATBOT()
userbot = Userbot()