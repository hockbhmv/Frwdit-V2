import os
import re 
import sys
import asyncio 
import logging 
from database import db 
from config import temp
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from pyrogram.errors import FloodWait
from config import Config
from translation import Translation
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@Client.on_message(filters.private & filters.command('add'))
async def bot_token(bot, m):
  msg = await bot.ask(chat_id=m.from_user.id, text="1) create a bot using @BotFather\n2) Then you will get a message with bot token\n3) Forward that message to me")
  if not msg.forward_date:
     await msg.reply_text("This is not a forward message")
     return False
  if str(msg.forward_from.id) != "93372553":
     await msg.reply_text("This message was not forward from bot father")
     return False
  bot_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', msg.text, re.IGNORECASE)
  if not token and token == []:
     await msg.reply_text("There is no bot token in that message")
     return False
  try:
    client = Client(f":memory:", Config.API_ID, Config.API_HASH, bot_token=bot_token[0])
    await client.start()
    _bot = await client.get_me()
  except (AccessTokenExpired, AccessTokenInvalid):
    await msg.reply_text("The given bot token is invalid")
    return False
  except Exception as e:
    await msg.reply_text(f"Bot Error:- {e}")
    return False
  details = {
    'id': _bot.id,
    'name': _bot.first_name,
    'token': bot_token[0],
    'username': _bot.username
  }
  await update_configs(m.from_user.id, 'bot', details)
  try:
    await client.stop()
  except:
    pass
  return True

@Client.on_message(filters.private & filters.command('reset'))
async def forward_tag(bot, m):
   default = await db.get_configs("01")
   temp.CONFIGS[m.from_user.id] = default
   await db.update_configs(m.from_user.id, default)
   await m.reply("successfully settings reseted ✔️")
    
async def get_configs(user_id):
  #configs = temp.CONFIGS.get(user_id)
  #if not configs:
  configs = await db.get_configs(user_id)
  #temp.CONFIGS[user_id] = configs 
  return configs
                          
async def update_configs(user_id, key, value):
  current = await db.get_configs(user_id)
  current[key] = value 
 # temp.CONFIGS[user_id] = value
  await db.update_configs(user_id, current)
        
