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
  regex = re.compile("/[0-9]{1,}:\w*/")
  token = regex.match(copy.text)#("/^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$/")
  if token is None:
    for match in regex.finditer(copy.text)
        token = match 
    else: 
        await msg.reply_text(f"error on find bottoken")
  await msg.reply_text(f"your token :- \n{token}")
  return
    
