# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in 
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from better import Better, db_core
from better.config import *
from better.database.data import scheduling

from pyrogram import idle


scheduler = AsyncIOScheduler()


async def db_connect():
    """Check Mongo Client"""
    try:
        print("Conectando ao MongoDB")
        await db_core.server_info()
    except BaseException as e:
        print("Falha ao conectar a database, saindo....")
        print(str(e))
        quit(1)


async def run_better():
    try:
        await Better.start()
    except Exception as e:
        print(e)
    await Better.send_message(chat_id=GP_LOGS, text="Bot iniciado")
    print("Bot iniciado com suceso ...")
    

async def main():
    await run_better()
    scheduler.add_job(scheduling, "interval", minutes=2, id='betterbot')
    scheduler.start()
    await idle()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
