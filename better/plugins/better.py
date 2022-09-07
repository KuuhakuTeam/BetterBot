# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in 
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

from datetime import datetime

from pyrogram import filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from better import Better
from better.config import DEV, TRIGGER, VERSION
from better.helpers.data import *


@Better.on_message(filters.command("on", TRIGGER))
async def on_(_, message):
    if message.chat.type == ChatType.SUPERGROUP or ChatType.GROUP:
        if not await check_rights(message.chat.id, message.from_user.id):
            return await message.reply("<i>Você precisa ser administrador para fazer isso.</i>")
        if not await verify(message.chat.id):
            await turn(message.chat.id, "on")
            return await message.reply("<i>Pronto, agora quando novos animes forem lançados eu notificarei vocês.</i>")
        await message.reply("<i>Oni-san, este grupo já está em minha lista de notificações.</i>")
    elif message.chat.type == ChatType.PRIVATE:
        if not await verify(message.chat.id):
            await turn(message.chat.id, "on")
            return await message.reply("<i>Pronto, agora quando novos animes forem lançados eu notificarei você.</i>")
        await message.reply("<i>Oni-san, você já está em minha lista de notificações.</i>")
    else:
        return


@Better.on_message(filters.command("off", TRIGGER))
async def stoping(_, message):
    if message.chat.type == ChatType.SUPERGROUP or ChatType.GROUP:
        if not await check_rights(message.chat.id, message.from_user.id):
            return await message.reply("<i>Você precisa ser administrador para fazer isso.</i>")
        if await verify(message.chat.id):
            await turn(message.chat.id, "off")
            await message.reply("<i>Ok, não vou mais enviar animes aqui.</i>")
        else:
            await message.reply("<i>Oni-san, este grupo não está em minha lista de notificações. Para ativar digite /on .</i>")
    elif message.chat.type == ChatType.PRIVATE:
        if await verify(message.chat.id):
            await turn(message.chat.id, "off")
            await message.reply("<i>Ok, não vou mais enviar animes aqui.</i>")
        else:
            await message.reply("<i>Oni-san, você não está em minha lista de notificações. Para ativar digite /on .</i>")
    else:
        return


@Better.on_message(filters.command("agenda", TRIGGER))
async def agenda_(_, message):
    msg = parse_anime_day()
    await message.reply(text=msg, disable_web_page_preview=True)


@Better.on_message(filters.command("random", TRIGGER))
async def about_(_, message):
    link, msg, img = parse_random()
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Ver no site", url=link,
                ),
            ],
        ]
    )
    await message.reply_photo(photo=img, caption=msg, reply_markup=keyboard)


@Better.on_message(filters.command("ping", TRIGGER))
async def ping_(_, message):
    start = datetime.now()
    replied = await message.reply("pong!")
    end = datetime.now()
    m_s = (end - start).microseconds / 1000
    await replied.edit(f"ping: `{m_s}𝚖𝚜`\nuptime: `{uptime()}`")


@Better.on_message(filters.command("latest", TRIGGER))
async def latest_animes(_, message):
    msg = parse_latest()
    await message.reply(msg)


@Better.on_message(filters.command(["start", "help"], TRIGGER))
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


@Better.on_message(filters.command(["about", "repo"], TRIGGER))
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


async def check_rights(chat_id: int, user_id: int) -> bool:
    """check admin"""
    user = await Better.get_chat_member(chat_id, user_id)
    if user_id in DEV:
        return True
    if user.status == ChatMemberStatus.MEMBER:
        return False
    elif user.status == ChatMemberStatus.OWNER or ChatMemberStatus.ADMINISTRATOR:
        return True
    else:
        return False