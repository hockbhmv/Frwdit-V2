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
BOT_TOKEN_TEXT = "1) create a bot using @BotFather\n2) Then you will get a message with bot token\n3) Forward that message to me"
SESSION_STRING_SIZE = 351

class CLIENT: 
  def __init__(self):
     self.api_id = Config.API_ID
     self.api_hash = Config.API_HASH
    
  def client(self, data, user=None):
     if user == None and data.get('is_bot') == False:
        return Client(data.get('session'), self.api_id, self.api_hash)
     elif user == True:
        return Client(data, self.api_id, self.api_hash)
     elif user != False:
        data = data.get('token')
     return Client(":memory:", self.api_id, self.api_hash, bot_token=data)
  
  async def add_bot(self, bot, message):
     user_id = message.from_user.id
     msg = await bot.ask(chat_id=user_id, text=BOT_TOKEN_TEXT)
     if msg.text=='/cancel':
        return await msg.reply('<b>process cancelled !')
     elif not msg.forward_date:
       return await msg.reply_text("This is not a forward message")
     elif str(msg.forward_from.id) != "93372553":
       return await msg.reply_text("This message was not forward from bot father")
     bot_token = re.findall(r'\d[0-9]{8,10}:[0-9A-Za-z_-]{35}', msg.text, re.IGNORECASE)
     bot_token = bot_token[0] if bot_token else None
     if not bot_token:
       return await msg.reply_text("<b>There is no bot token in that message</b>")
     try:
       _client = await bot.start_clone_bot(self.client(bot_token, False), True)
     except Exception as e:
       await msg.reply_text(f"<b>BOT ERROR:</b> `{e}`")
     _bot = _client.details
     details = {
       'id': _bot.id,
       'is_bot': True,
       'name': _bot.first_name,
       'token': bot_token,
       'username': _bot.username
     }
     await update_configs(user_id, 'bot', details)
     return True
    
  async def add_session(self, bot, message):
     user_id = message.from_user.id
     text = "send your session string get it from None"
     msg = await bot.ask(chat_id=user_id, text=text)
     if msg.text=='/cancel':
        return await msg.reply('<b>process cancelled !</b>')
     elif len(msg.text) < SESSION_STRING_SIZE:
        return await msg.reply('<b>invalid session sring</b>')
     try:
       client = await bot.start_clone_bot(self.client(msg.text, True), True)
     except Exception as e:
       await msg.reply_text(f"<b>USER BOT ERROR:</b> `{e}`")
     user = client.details
     details = {
       'id': user.id,
       'is_bot': False,
       'name': user.first_name,
       'session': msg.text,
       'username': user.username
     }
     await update_configs(user_id, 'bot', details)
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
  current.update({key: value})
 # temp.CONFIGS[user_id] = value
  await db.update_configs(user_id, current)
        
