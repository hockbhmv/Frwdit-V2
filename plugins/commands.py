import os
import sys
import asyncio 
from database import db
from config import Config
from translation import Translation
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaDocument

main_buttons = [[
        InlineKeyboardButton('❗️Help', callback_data='help') 
        ],[
        InlineKeyboardButton('📜 Support Group', url='https://t.me/venombotupdates'),
        InlineKeyboardButton('📢 Update Channel ', url='https://t.me/venombotsupport')
]]

#===================Start Function===================#

@Client.on_message(filters.private & filters.command(['start']))
async def start(client, message):
    user = message.from_user
    if not await db.is_user_exist(user.id):
      await db.add_user(user.id, user.first_name)
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await client.send_message(
        chat_id=message.chat.id,
        reply_markup=reply_markup,
        text=Translation.START_TXT.format(
                message.from_user.first_name),
        parse_mode="combined")

#==================Restart Function==================#

@Client.on_message(filters.private & filters.command(['restart']))
async def restart(client, message):
    msg = await message.reply_text(
        text="<i>Trying to restarting.....</i>"
    )
    await asyncio.sleep(5)
    await msg.edit("<i>Server restarted successfully ✅</i>")
    os.execl(sys.executable, sys.executable, *sys.argv)
    
#==================Callback Functions==================#

@Client.on_callback_query(filters.regex(r'^help'))
async def helpcb(bot, query):
    buttons = [[
            InlineKeyboardButton('About', callback_data='about'),
            InlineKeyboardButton('Status', callback_data='status'),
            InlineKeyboardButton('back', callback_data='back')
    ]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Translation.HELP_TXT,
        reply_markup=reply_markup,
        parse_mode="combined")

@Client.on_callback_query(filters.regex(r'^back'))
async def back(bot, query):
    reply_markup = InlineKeyboardMarkup(main_buttons)
    await query.message.edit_text(
       reply_markup=reply_markup,
       text=Translation.START_TXT.format(
                query.from_user.first_name),
       parse_mode="combined")

@Client.on_callback_query(filters.regex(r'^about'))
async def about(bot, query):
    buttons = [[InlineKeyboardButton('back', callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Translation.ABOUT_TXT,
        reply_markup=reply_markup
        disable_web_page_preview=True,
        parse_mode="combined"
    )

@Client.on_callback_query(filters.regex(r'^status'))
async def status(bot, query):
    buttons = [[InlineKeyboardButton('back', callback_data='help')]]
    reply_markup = InlineKeyboardMarkup(buttons)
    await query.message.edit_text(
        text=Translation.STATUS_TXT,
        reply_markup=reply_markup
        disable_web_page_preview=True,
        parse_mode="combined"
    )
