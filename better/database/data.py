# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

import asyncio
import requests

from bs4 import BeautifulSoup

from pyrogram.errors import ChatIdInvalid, ChatWriteForbidden, ChannelInvalid
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from better import Better
from better.config import GP_LOGS
from better.database import db


animes = db["ANIMES"]


async def find_gp(gid: int):
    if await animes.find_one({"chat_id": gid}):
        return True


async def add_gp(m):
    user = f"<a href='tg://user?id={m.from_user.id}'>{m.from_user.first_name}</a>"
    user_start = f"#Better #New_Group\n\n<b>Group</b>: {m.chat.title}\n<b>ID:</b> {m.chat.id}\n<b>User:</b> {user}"
    await Better.send_message(GP_LOGS, user_start)
    await animes.insert_one({"chat_id": m.chat.id})


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


async def rm_gp(gid: int):
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
                except (ChatIdInvalid, ChatWriteForbidden, ChannelInvalid):
                    await rm_gp(gid)
                    pass
                except Exception:
                    pass
                await asyncio.sleep(1)
