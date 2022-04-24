import re
import asyncio 
from database import db
from config import temp 
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.errors import FloodWait 
from pyrogram.errors.exceptions.bad_request_400 import ChannelInvalid, ChatAdminRequired, UsernameInvalid, UsernameNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
 
#===================Run Function===================#

@Client.on_message(filters.private & filters.command(["forward"]))
async def run(bot, message):
    buttons = []
    btn_data = {}
    user_id = message.from_user.id
    channels = await db.get_user_channels(user_id)
    async for channel in channels:
       buttons.append([KeyboardButton(f"{channel['title']}")])
       btn_data[channel['title']] = channel['chat_id']
    if not buttons:
       return await message.reply_text("please set a to channel in /settings before forwarding")
    buttons.append([KeyboardButton("cancel")])
    _toid = await bot.ask(message.chat.id, Translation.TO_MSG, reply_markup=ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True))
    if _toid.text.startswith(('/', 'cancel')):
        await message.reply_text(Translation.CANCEL, reply_markup=ReplyKeyboardRemove())
        return
    toid = btn_data.get(_toid.text)
    if not toid:
       return await message.reply_text("wrong channel choosen !", reply_markup=ReplyKeyboardRemove())
    fromid = await bot.ask(message.chat.id, Translation.FROM_MSG, reply_markup=ReplyKeyboardRemove())
    if fromid.text and fromid.text.startswith('/'):
        await message.reply(Translation.CANCEL)
        return 
    if fromid.text:
        regex = re.compile("(https://)?(t\.me/|telegram\.me/|telegram\.dog/)(c/)?(\d+|[a-zA-Z_0-9]+)/(\d+)$")
        match = regex.match(fromid.text)
        if not match:
            return await message.reply('Invalid link')
        chat_id = match.group(4)
        last_msg_id = int(match.group(5))
        if chat_id.isnumeric():
            chat_id  = int(("-100" + chat_id))
    elif fromid.forward_from_chat.type == 'channel':
        last_msg_id = fromid.forward_from_message_id
        chat_id = fromid.forward_from_chat.username or fromid.forward_from_chat.id
    else:
        return 
    try:
        chat = await bot.get_chat(chat_id)
    except ChannelInvalid:
        return await message.reply('This may be a private channel / group. Make me an admin over there to forward messages.')
    except (UsernameInvalid, UsernameNotModified):
        return await message.reply('Invalid Link specified.')
    except Exception as e:
        return await message.reply(f'Errors - {e}')
    try:
        k = await bot.get_messages(chat_id, last_msg_id)
    except:
        return await message.reply('This may be a private channel / group. Make me an admin over there')
    if k.empty:
        return await message.reply('This may be group and iam not a admin of the group.')
    skipno = await bot.ask(message.chat.id, Translation.SKIP_MSG)
    if skipno.text.startswith('/'):
        await message.reply(Translation.CANCEL)
        return
    bot = await db.get_bot(user_id)
    forward_id = f"{user_id}-{skipno.message_id}"
    buttons = [[
        InlineKeyboardButton('Yes', callback_data=f"start_public_{forward_id}"),
        InlineKeyboardButton('No', callback_data="close_btn")
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await message.reply_text(
        text=Translation.DOUBLE_CHECK.format(f"[{bot['name']}](t.me/{bot['username']})", chat.title, _toid.text, skipno.text, bot['username']),
        parse_mode="combined",
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )
    temp.FORWARD[forward_id] = {
        'TO': toid,
        'FROM': chat_id,
        'SKIP': skipno.text,
        'LIMIT': last_msg_id
    }
