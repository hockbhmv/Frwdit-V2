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
  if not msg.forward_date:#filters forward message
     return await msg.reply_text("This not a Forward message")
  regex = re.compile("/^[0-9]{8,10}:[a-zA-Z0-9_-]{35}$/")
  token = regex.match(msg.text)
  await msg.reply_text(token)
  return
    
