import os
import re 
import sys
import asyncio 
import logging 
from database import db 
from config import Config
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.errors import FloodWait
from config import Config
from translation import Translation
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@Client.on_message(filters.private & filters.command('add'))
async def token(bot, m):
  msg = await bot.ask(chat_id=m.from_user.id, text="1) create a bot using @BotFather\n2) Then you will get a message with bot token\n3) Forward that message to me")
  if not msg.forward_date:
     return await msg.reply_text("This is not a forward message")
  if str(msg.forward_from.id) != "93372553":
     return await msg.reply_text("This message was not forward from bot father")
  token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', msg.text, re.IGNORECASE)
  if not token and token == []:
     return await msg.reply_text("There is no bot token in that message")
  await update_configs(m.from_user.id, "bot_token", token[0])
  await msg.reply_text(f"bot token successfully added to db")
  return

@Client.on_message(filters.private & filters.command('forward_tag'))
async def forward_tag(bot, m):
   configs = await db.get_configs(m.from_user.id)
   forward_tag = configs.get('forward_tag')
   if not forward_tag:
      forward_tag = True 
   if forward_tag != "True":
       await update_configs(m.from_user.id, "forward_tag", True)
   else:
       await update_configs(m.from_user.id, "forward_tag", False)
   await m.reply("Now Forward messages without tag" if forward_tag=="True" else "Now Forward messages with tag")
  
async def get_configs(user_id):
  configs = Config.CONFIGS.get(user_id)
  if not configs:
     configs = await db.get_configs(user_id)
     Config.CONFIGS[user_id] = configs 
  return configs
                          
async def update_configs(user_id, key, value):
  current = await db.get_configs(user_id)
  current[key] = value 
  await db.update_configs(user_id, current)
        
