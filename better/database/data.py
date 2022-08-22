# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

import time
import asyncio
import requests

from bs4 import BeautifulSoup

from pyrogram.errors import ChatIdInvalid, ChatWriteForbidden, ChannelInvalid, UserIsBlocked
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatType

from better import Better, start_time
from better.config import GP_LOGS
from better.database import db


animes = db["CHATS"]


async def find_chat(gid: int):
    if await animes.find_one({"chat_id": gid}):
        return True


async def add_to_db(m):
    if m.chat.type == ChatType.PRIVATE:
        user = await Better.get_users(m.from_user.id)
        msg = f"#Better #New_User\n\n<b>User:</b> {user.mention}\n<b>ID:</b> {user.id}"
        if user.username:
            msg += f"\n<b>Username:</b> {user.username}"
        type = "user"
    elif m.chat.type == ChatType.SUPERGROUP or ChatType.GROUP:
        x = await Better.get_chat(m.chat.id)
        msg = f"#Better #New_Group\n\n<b>Group</b>: {x.title}\n<b>ID:</b> {x.id}"
        type = "group"
    await animes.update_one({"chat_id": m.chat.id}, {"$set": {"type": type}}, upsert=True)
    await Better.send_message(GP_LOGS, msg)


async def find_ep(gid: int, string: str):
    x = await animes.find_one({"chat_id": gid})
    if x:
        try:
            st = x["string"]
            if st == string:
                return True
            return False
        except (Exception, KeyError):
            return False
    return False


async def add_ep(gid: int, string: str):
    await animes.update_one(
        {"chat_id": gid}, {"$set": {"string": string}}, upsert=True
    )


async def rm_chat(gid: int):
    await animes.delete_one({"chat_id": gid})


def get_img(link):
    req = requests.get(link)
    sp = BeautifulSoup(req.content, "lxml")
    all_div = sp.find("div", class_="anime-title")
    get_ref = all_div.find("a")
    req2 = requests.get(get_ref["href"])
    sp2 = BeautifulSoup(req2.content, "html.parser")
    all_ = sp2.find("div", class_="infos-img text-center")
    get_img = all_.find("img")
    return str("https:" + get_img["src"])


def parse_str():
    req = requests.get("https://betteranime.net/lancamentos-rss")
    sp = BeautifulSoup(req.content, "html.parser")
    x = sp.find("entry")
    title = x.find("summary")
    link = x.find("link")["href"]
    return link, title.contents[1]


def parse_latest():
    req = requests.get("https://betteranime.net/lancamentos-rss")
    sp = BeautifulSoup(req.content, "html.parser")
    x = sp.find_all("entry", limit=15)
    msg = "<b>Ultimos animes adicionados:</b>\n\n"
    for anim in x:
        title = anim.find("summary")
        link = anim.find("link")["href"]
        msg += f'• <i><a href="{link}">{title.contents[1]}</a></i>\n'
    return msg


def time_formatter(seconds: float) -> str:
    """time formating"""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
    )
    return tmp[:-2]


def uptime():
    return time_formatter(time.time() - start_time)


async def scheduling():
    glist = animes.find()
    async for chats in glist:
        if chats == None:
            return
        else:
            gid = chats["chat_id"]
            link, string = parse_str()
            if await find_ep(gid, string):
                pass
            else:
                await add_ep(gid, string)
                img = get_img(link)
                try:
                    keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    text="Assistir", url=link
                                )
                            ],
                        ]
                    )
                    msg = f"<b>Novos episodios adicionados:</b>\n\n<i>✨ {string}</i>"
                    await Better.send_photo(chat_id=gid, photo=img, caption=msg, reply_markup=keyboard)
                except (ChatIdInvalid, ChatWriteForbidden, ChannelInvalid, UserIsBlocked):
                    await rm_chat(gid)
                    pass
                except Exception:
                    pass
                await asyncio.sleep(1)
