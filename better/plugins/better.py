# BetterAnime Scheduling Bot
# Copyright (C) 2022 KuuhakuTeam
#
# This file is a part of < https://github.com/KuuhakuTeam/BetterBot/ >
# PLease read the GNU v3.0 License Agreement in
# <https://www.github.com/KuuhakuTeam/BetterBot/blob/master/LICENSE/>.

import asyncio

from datetime import datetime
from feedparser import parse

from pyrogram import filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message

from better import Better
from better.config import DEV, TRIGGER
from better.helpers.data import *


@Better.on_message(filters.command("anime", TRIGGER))
async def anime_search(_, message):
    query = " ".join(message.text.split()[1:])
    if not query:
        return await message.reply("<i>Você precisa inserir o nome de algum anime</i>")
    url = f'https://betteranime.net/pesquisa?titulo={query.replace(" ", "+")}&searchTerm={query.replace(" ", "+")}'
    req = requests.get(url).content
    try:
        soup = BeautifulSoup(req, "html.parser")
        sp = soup.find("article", class_="col-xl-2 col-lg-3 col-md-3 col-sm-4 col-6")
        link = sp.find("a")["href"]
        msg, img = get_info(link)
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Ver no site",
                        url=link,
                    ),
                ],
                [
                    InlineKeyboardButton(
                        text="Mais Resultados",
                        url=url,
                    ),
                ],
            ]
        )
        await message.reply_photo(photo=img, caption=msg, reply_markup=keyboard)
    except AttributeError:
        await message.reply(
            f"<i>Não consegui encontrar nenhum anime com esse nome.</i>"
        )


@Better.on_message(filters.command("stats", TRIGGER))
async def count_users(_, message):
    glist = animes.find()
    groups, users = 0, 0
    async for i in glist:
        if i.get("type") == "user":
            users = users + 1
        else:
            groups = groups + 1
    await message.reply(
        f"<i>Oni-san, atualmente eu notifico {users} Usuarios e {groups} Grupos.</i>"
    )


@Better.on_message(filters.command("on", TRIGGER))
async def on_(_, message):
    if message.chat.type == ChatType.SUPERGROUP or ChatType.GROUP:
        if not await check_rights(message.chat.id, message.from_user.id):
            return await message.reply(
                "<i>Você precisa ser administrador para fazer isso.</i>"
            )
        if not await find_chat(message.chat.id):
            await add_to_db(message)
            await asyncio.sleep(1)
        if not await verify(message.chat.id):
            await turn(message.chat.id, "on")
            return await message.reply(
                "<i>Pronto, agora quando novos animes forem lançados eu notificarei vocês.</i>"
            )
        await message.reply(
            "<i>Oni-san, este grupo já está em minha lista de notificações.</i>"
        )
    elif message.chat.type == ChatType.PRIVATE:
        if not await find_chat(message.chat.id):
            await add_to_db(message)
            await asyncio.sleep(1)
        if not await verify(message.chat.id):
            await turn(message.chat.id, "on")
            return await message.reply(
                "<i>Pronto, agora quando novos animes forem lançados eu notificarei você.</i>"
            )
        await message.reply(
            "<i>Oni-san, você já está em minha lista de notificações.</i>"
        )
    else:
        return


@Better.on_message(filters.command("off", TRIGGER))
async def stoping(_, message):
    if message.chat.type == ChatType.SUPERGROUP or ChatType.GROUP:
        if not await check_rights(message.chat.id, message.from_user.id):
            return await message.reply(
                "<i>Você precisa ser administrador para fazer isso.</i>"
            )
        if not await find_chat(message.chat.id):
            await add_to_db(message)
            await asyncio.sleep(1)
        if await verify(message.chat.id):
            await turn(message.chat.id, "off")
            await message.reply("<i>Ok, não vou mais enviar animes aqui.</i>")
        else:
            await message.reply(
                "<i>Oni-san, este grupo não está em minha lista de notificações. Para ativar digite /on .</i>"
            )
    elif message.chat.type == ChatType.PRIVATE:
        if not await find_chat(message.chat.id):
            await add_to_db(message)
            await asyncio.sleep(1)
        if await verify(message.chat.id):
            await turn(message.chat.id, "off")
            await message.reply("<i>Ok, não vou mais enviar animes aqui.</i>")
        else:
            await message.reply(
                "<i>Oni-san, você não está em minha lista de notificações. Para ativar digite /on .</i>"
            )
    else:
        return


@Better.on_message(filters.command("agenda", TRIGGER))
async def agenda_(_, message):
    msg = parse_anime_day()
    await message.reply(text=msg, disable_web_page_preview=True)


@Better.on_message(filters.command("random", TRIGGER))
async def about_(_, message):
    try:
        rand_anime = requests.get("https://betteranime.net/random").url
        msg, img = get_info(rand_anime)
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Ver no site",
                        url=rand_anime,
                    ),
                ],
            ]
        )
        await message.reply_photo(photo=img, caption=msg, reply_markup=keyboard)
    except AttributeError:
        await message.reply(
            f"<i>Não consegui encontrar nenhum anime com esse nome.</i>"
        )


@Better.on_message(filters.command("ping", TRIGGER))
async def ping_(_, message):
    start = datetime.now()
    replied = await message.reply("pong!")
    end = datetime.now()
    m_s = (end - start).microseconds / 1000
    await replied.edit(f"ping: `{m_s}𝚖𝚜`\nuptime: `{uptime()}`")


@Better.on_message(filters.command("latest", TRIGGER))
async def latest_animes(_, message):
    """get latest 20 animes"""
    req = parse("https://betteranime.net/lancamentos-rss")
    all_entry = req["entries"]
    msg = "<b>Ultimos animes adicionados:</b>\n\n"
    for anim in all_entry:
        title = anim["title"]
        link = anim["link"]
        msg += f'• <i><a href="{link}">{title}</a></i>\n'
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
                    text="Adicionar a um Grupo",
                    url=f"https://t.me/{me.username}?startgroup=new",
                ),
            ],
        ]
    )
    if message.chat.type == ChatType.PRIVATE:
        await message.reply(
            "<i>Olá, sou apenas um bot que notifica quando um episodio é adicionado ao site BetterAnime.net. Eu te avisarei aqui quando novos animes forem adicionados e você tambem pode me adicionar á um grupo se desejar.</i>",
            reply_markup=keyboard,
        )
    else:
        return


@Better.on_message(filters.command(["about", "repo"], TRIGGER))
async def about_(_, message):
    if message.chat.type == ChatType.PRIVATE:
        await message.reply(
            '<i><a href="https://github.com/KuuhakuTeam/BetterBot">Repositorio</a></i>'
        )
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
        else:
            pass


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
