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
from better.database.data import find_gp, add_gp, rm_gp


@Better.on_message(filters.command(["start", "help"]))
async def spam(_, message):
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
        await message.reply("Olá, sou apenas um bot que notifica quando um episodio é adicionado ao site BetterAnime.net. Me adicione á um grupo e eu enviarei os novos animes.", reply_markup=keyboard)
    else:
        return


@Better.on_message(filters.new_chat_members)
async def thanks_for(c: Better, m: Message):
    gid = m.chat.id
    if c.me.id in [x.id for x in m.new_chat_members]:
        if await find_gp(gid):
            return
        else:
            await add_gp(m)


@Better.on_message(filters.left_chat_member)
async def left_chat_(c: Better, m: Message):
    gid = m.chat.id
    if c.me.id == m.left_chat_member.id:
        if await find_gp(gid):
            await rm_gp(gid)
        else:
            return


@Better.on_message()
async def thanks_for(_, m: Message):
    if not m.chat.type == ChatType.GROUP or ChatType.SUPERGROUP:
        return
    if not await find_gp(m.chat.id):
        await add_gp(m)