# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in 
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

import time

from .config import *
import motor.motor_asyncio

from pyrogram import Client

start_time = time.time()

db_core = motor.motor_asyncio.AsyncIOMotorClient(DATABASE_URL)

Better = Client(
    name="BetterBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=180,
    in_memory=True,
    plugins=dict(root="better.plugins")
)
