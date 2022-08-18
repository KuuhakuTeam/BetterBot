# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in 
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from better import Better
from better.config import VERSION
from better.database.data import find_chat, add_to_db, rm_chat, parse_latest


@Better.on_message(filters.command("latest"))
async def latest_animes(_, message):
    msg = parse_latest()
    await message.reply(msg)


@Better.on_message(filters.command(["start", "help"]))
async def start_(_, message):
    if not await find_chat(message.chat.id):
        await add_to_db(message)
    me = await Better.get_users("me")
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Adicionar a um Grupo", url=f"https://t.me/{me.username}?startgroup=new",
                ),
            ],
        ]
    )
    if message.chat.type == ChatType.PRIVATE:
        await message.reply("Olá, sou apenas um bot que notifica quando um episodio é adicionado ao site BetterAnime.net. Eu te avisarei aqui quando novos animes forem adicionados e você tambem pode me adicionar á um grupo se desejar.", reply_markup=keyboard)
    else:
        return


@Better.on_message(filters.command(["about", "repo"]))
async def about_(_, message):
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Repositorio", url="https://github.com/KuuhakuTeam/BetterBot",
                ),
            ],
        ]
    )
    if message.chat.type == ChatType.PRIVATE:
        await message.reply_photo(photo="https://telegra.ph/file/a6b8f14854ada59ad1e8e.jpg", caption=f"<b>Versão: {VERSION}</b>", reply_markup=keyboard)
    else:
        return


@Better.on_message(filters.new_chat_members)
async def thanks_for(c: Better, m: Message):
    gid = m.chat.id
    if c.me.id in [x.id for x in m.new_chat_members]:
        if await find_chat(gid):
            return
        else:
            await add_to_db(m)


@Better.on_message(filters.left_chat_member)
async def left_chat_(c: Better, m: Message):
    gid = m.chat.id
    if c.me.id == m.left_chat_member.id:
        if await find_chat(gid):
            await rm_chat(gid)
        else:
            return


@Better.on_message()
async def thanks_for(_, m: Message):
    if m.chat.type == ChatType.GROUP or ChatType.SUPERGROUP or ChatType.PRIVATE:
        if not await find_chat(m.chat.id):
            await add_to_db(m)
