# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

import time
import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pymongo.errors import ConnectionFailure
from logging.handlers import RotatingFileHandler


from better import Better, db_core
from better.config import *
from better.helpers.scheduler import scheduling_anime, scheduling_day_animes

from pyrogram import idle


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("better.log", maxBytes=20480, backupCount=10),
        logging.StreamHandler(),
    ],
)


logging.getLogger("apscheduler.executors.default").disabled

logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pyrogram.parser.html").setLevel(logging.ERROR)
logging.getLogger("pyrogram.session.session").setLevel(logging.ERROR)


scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
start_time = time.time()


async def db_connect():
    """Check Mongo Client"""
    try:
        logging.info("Conectando ao MongoDB")
        await db_core.server_info()
        logging.info("Database conectada")
    except (BaseException, ConnectionFailure) as e:
        logging.error("Falha ao conectar a database, saindo....")
        logging.error(str(e))
        quit(1)


async def run_better():
    """Start Bot"""
    try:
        await Better.start()
    except Exception as e:
        logging.error(e)
    await Better.send_message(
        chat_id=GP_LOGS, text=f"[ Better Schedule ] Bot iniciado com sucesso ...\nVersion: <code>{VERSION}</code>"
    )
    logging.info("[ Better Schedule ] Bot iniciado com sucesso ...\n")


async def main():
    await db_connect()
    await run_better()
    scheduler.add_job(scheduling_day_animes, "cron", hour=11, id="beter_anime_day")
    scheduler.add_job(scheduling_anime, "interval", minutes=1, id="better_scheduller")
    scheduler.start()
    await idle()


if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())
