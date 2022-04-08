import os
import re 
import sys
import asyncio 
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.errors import FloodWait
from config import Config
from translation import Translation


@Client.on_message(filters.private & filters.command('add'))
async def token(bot, m):
  msg = await bot.ask(chat_id=m.from_user.id, text="Forward the message from bot father")
 # if not msg.forward_date:#filters forward message
    # return await msg.reply_text("This not a Forward message")
  copy = await msg.copy(m.from_user.id)
  regex = re.compile(r'\d{9}:[0-9A-Za-z_-]{35}')
  token = regex.search(copy.text)
  if not token:
     await msg.reply_text("invalid bot token")
  if token is None:
    for match in regex.finditer(copy.text):
        tokens = match 
    else: 
        await msg.reply_text(f"error on find bottoken")
  await msg.reply_text(f"your token :- \n{token}\nilter :- {tokens}")
  return
    
