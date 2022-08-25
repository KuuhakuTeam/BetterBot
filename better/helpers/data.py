# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

import time
import requests

from bs4 import BeautifulSoup
from datetime import date

from pyrogram.enums import ChatType

from better import Better, start_time
from better.config import GP_LOGS
from better.helpers import db


animes = db["CHATS"]


async def find_chat(gid: int):
    """verify chat in db"""
    if await animes.find_one({"chat_id": gid}):
        return True


async def add_to_db(m):
    """add chat to db"""
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
    """verify episode in chat db"""
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
    """add ep to chat db"""
    await animes.update_one(
        {"chat_id": gid}, {"$set": {"string": string}}, upsert=True
    )


async def rm_chat(gid: int):
    """remove chat to db"""
    await animes.delete_one({"chat_id": gid})


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
    req = requests.get("https://betteranime.net/lancamentos-rss")
    sp = BeautifulSoup(req.content, "html.parser")
    x = sp.find("entry")
    title = x.find("summary")
    link = x.find("link")["href"]
    return link, title.contents[1]


def parse_latest():
    """get latest 15 animes"""
    req = requests.get("https://betteranime.net/lancamentos-rss")
    sp = BeautifulSoup(req.content, "html.parser")
    x = sp.find_all("entry", limit=15)
    msg = "<b>Ultimos animes adicionados:</b>\n\n"
    for anim in x:
        title = anim.find("summary")
        link = anim.find("link")["href"]
        msg += f'• <i><a href="{link}">{title.contents[1]}</a></i>\n'
    return msg


def parse_random():
    """random anime"""
    template = """
<b>{}</b>

<b>Gêneros:</b> {}
<code>{}</code>
    """
    rand_anime = requests.get("https://betteranime.net/random").url
    req = requests.get(rand_anime).content
    page = BeautifulSoup(req, "html.parser").find("main", class_="container d-flex my-5")
    title = page.find("h2", class_="pt-5").text
    sinopse = page.find("div", class_="anime-description").text
    genres = " ".join(map(str, page.find("div", class_="anime-genres").text.split()))
    if len(sinopse) > 800:
        sinopse = sinopse[:800] + " ..."
    img = "https:" + page.find("img")["src"]
    return rand_anime, template.format(title, genres, sinopse), img


def day_week():
    data = date.today().weekday()
    week_class = ("v-pills-seg-tab", "v-pills-ter-tab", "v-pills-qua-tab", "v-pills-qui-tab", "v-pills-sex-tab", "v-pills-sab-tab", "v-pills-dom-tab")
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

