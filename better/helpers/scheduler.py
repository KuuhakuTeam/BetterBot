# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

import asyncio

from feedparser import parse

from pyrogram.errors import (
    ChatIdInvalid,
    ChatWriteForbidden,
    ChannelInvalid,
    UserIsBlocked,
)
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from .data import *


async def scheduling_anime():
    """send new animes in chats"""
    glist = animes.find()
    async for chats in glist:
        if chats == None:
            return
        else:
            id = chats["chat_id"]
            if await verify(id):
                try:
                    req = parse("https://betteranime.net/lancamentos-rss")
                    string = req["entries"][0]["title"]
                    link = req["entries"][0]["link"]
                    if await find_ep(id, string):
                        pass
                    else:
                        await add_ep(id, string)
                        img = get_img(link)
                        try:
                            keyboard = InlineKeyboardMarkup(
                                [
                                    [InlineKeyboardButton(text="Assistir", url=link)],
                                ]
                            )
                            msg = f"<b>Novos episodios adicionados:</b>\n\n<i>✨ {string}</i>"
                            await Better.send_photo(
                                chat_id=id,
                                photo=img,
                                caption=msg,
                                reply_markup=keyboard,
                            )
                        except (ChatIdInvalid, ChannelInvalid, UserIsBlocked):
                            await rm_chat(id)
                            pass
                        except (Exception, ChatWriteForbidden):
                            pass
                except IndexError or AttributeError:
                    break
            else:
                pass


async def scheduling_day_animes():
    """send anime schedule of the day"""
    glist = animes.find()
    async for chats in glist:
        if chats == None:
            return
        else:
            id = chats["chat_id"]
            if await verify(id):
                msg = "<b>Ohayou minna san ✨</b>\n" + parse_anime_day()
                try:
                    await Better.send_message(
                        chat_id=id, text=msg, disable_web_page_preview=True
                    )
                except (ChatIdInvalid, ChannelInvalid, UserIsBlocked):
                    await rm_chat(id)
                    pass
                except (Exception, ChatWriteForbidden):
                    pass
            else:
                pass
