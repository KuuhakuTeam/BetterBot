# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

import time
import requests

from datetime import date
from bs4 import BeautifulSoup
from feedparser import parse

from pyrogram.enums import ChatType

from better import Better, start_time
from better.config import GP_LOGS
from better.helpers import db


animes = db["CHATS"]


async def find_chat(id: int):
    """verify chat in db"""
    if await animes.find_one({"chat_id": id}):
        return True


async def verify(id: int):
    """verify notification"""
    if await find_chat(id):
        x = await animes.find_one({"chat_id": id})
        if x["notification"] == "on":
            return True
        else:
            return False
    else:
        return False


async def turn(id: int, typ: str):
    """turn on/off notifications"""
    await animes.update_one({"chat_id": id}, {"$set": {"notification": typ}}, upsert=True)


async def add_to_db(m):
    """add chat to db"""
    if m.chat.type == ChatType.PRIVATE:
        user = await Better.get_users(m.from_user.id)
        msg = f"#Better #New_User\n\n<b>User:</b> {user.mention}\n<b>ID:</b> {user.id}"
        if user.username:
            msg += f"\n<b>Username:</b> @{user.username}"
        type = "user"
    elif m.chat.type == ChatType.SUPERGROUP or ChatType.GROUP:
        gp = await Better.get_chat(m.chat.id)
        msg = f"#Better #New_Group\n\n<b>Group</b>: {gp.title}\n<b>ID:</b> {gp.id}"
        if gp.username:
            msg += f"\n<b>Username:</b> @{gp.username}"
        type = "group"
    await animes.update_one({"chat_id": m.chat.id}, {"$set": {"type": type, "notification": "on"}}, upsert=True)
    await Better.send_message(GP_LOGS, msg)


async def find_ep(id: int, string: str):
    """verify episode in chat db"""
    x = await animes.find_one({"chat_id": id})
    if x:
        try:
            st = x["string"]
            if st == string:
                return True
            return False
        except (Exception, KeyError):
            return False
    return False


async def add_ep(id: int, string: str):
    """add ep to chat db"""
    await animes.update_one(
        {"chat_id": id}, {"$set": {"string": string}}, upsert=True
    )


async def rm_chat(id: int):
    """remove chat to db"""
    await animes.delete_one({"chat_id": id})


def get_img(link):
    """get image from anime"""
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
    """get latest anime"""
    req = parse("https://betteranime.net/lancamentos-rss")
    title = req["entries"][0]["title"]
    link = req["entries"][0]["link"]
    return link, title


def parse_latest():
    """get latest 20 animes"""
    req = parse("https://betteranime.net/lancamentos-rss")
    all_entry = req["entries"]
    msg = "<b>Ultimos animes adicionados:</b>\n\n"
    for anim in all_entry:
        title = anim["title"]
        link = anim["link"]
        msg += f'• <i><a href="{link}">{title}</a></i>\n'
    return msg


def get_info(url: str):
    template = """
<b>{}</b>

<b>Gêneros:</b> {}
<code>{}</code>
    """
    req = requests.get(url).content
    page = BeautifulSoup(req, "html.parser").find("main", class_="container d-flex my-5")
    title = page.find("h2", class_="pt-5").text
    sinopse = page.find("div", class_="anime-description").text
    genres = " ".join(map(str, page.find("div", class_="anime-genres").text.split()))
    if len(sinopse) > 800:
        sinopse = sinopse[:800] + " ..."
    img = "https:" + page.find("img")["src"]
    return template.format(title, genres, sinopse), img


def day_week():
    data = date.today().weekday()
    week_class = ("v-pills-seg-tab", "v-pills-ter-tab", "v-pills-qua-tab", "v-pills-qui-tab", "v-pills-sex-tab", "v-pills-sáb-tab", "v-pills-dom-tab")
    return {week_class[data]}


def parse_anime_day():
    req = requests.get("https://betteranime.net/").content
    bs = BeautifulSoup(req, "html.parser")
    x = bs.find("div", {"aria-labelledby": day_week()})
    parser = x.find_all("div", class_="d-flex mb-4 pb-3")
    msg = "<b>Animes em lançamento hoje:</b>\n\n"
    for text in parser:
        msg += f'• <b><a href="{text.find("a")["href"]}">{" ".join(text.find("div", class_="calendar-title").text.replace("Episódio Novo", "").split())}</a></b>\n- <i>{" ".join(text.find("div", class_="d-flex align-items-center calendar-hours").text.replace("Aprox.", "Aproximadamente").split())}</i>\n\n'
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
    """bot uptime"""
    return time_formatter(time.time() - start_time)


