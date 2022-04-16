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
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BOT_TOKEN = {} 

@Client.on_message(filters.private & filters.command('add'))
async def token(bot, m):
  msg = await bot.ask(chat_id=m.from_user.id, text="1) create a bot using @BotFather\n2) Then you will get a message with bot token\n3) Forward that message to me")
  if not msg.forward_date and msg.forward_from.id=="93372553":
     return await msg.reply_text("**This is not a Forward message or this message was not forward from bot father**")
  copy = await bot.get_messages(msg.forward_from.id, msg.forward_from_message_id)
  token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', copy.text, re.IGNORECASE)
  if token is None:
     await msg.reply_text("There is no bot token in that message")
  BOT_TOKEN[m.from_user.id] = copy.text
  await msg.reply_text(f"your bot with  token <code>{token}</code> successfully added")
  return
