import asyncio 
from database import db
from pyrogram import Client, filters
from .test import get_configs, update_configs 
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

@Client.on_message(filters.command('settings'))
async def settings(client, message):
   await message.reply_text(
     "change your settings as your wish",
     reply_markup=main_buttons()
     )
    
@Client.on_callback_query(filters.regex(r'^settings'))
async def settings_query(bot, query):
  i, type = query.data.split("#")
  buttons = [[InlineKeyboardButton('back', callback_data="settings#main")]]
  
  if type=="main":
     await query.message.edit_text(
       "change your settings as your wish",
       reply_markup=main_buttons())
       
  elif type=="bots":
     buttons = [[InlineKeyboardButton('➕ Add bot ➕', 
                         callback_data="settings#addbot")
                ],[
                InlineKeyboardButton('back', 
                         callback_data="settings#main")]]
     await query.message.edit_text(
       "<b><u>My Bots</b></u>\n\nyou can manage your bots in here",
       reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="channels":
     buttons = []
     data = await db.get_configs(query.from_user.id)
     channels = data['channels"]
     if channels is not None:
        chat = await bot.get_chat(channels) 
        buttons.append([InlineKeyboardButton(f'- {chat.title}',
                         callback_data="settings#editchannels")])
     buttons.append([InlineKeyboardButton('➕ Add bot ➕', 
                      callback_data="settings#addchannel")])
     buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#main")])
     await query.message.edit_text( 
       "<b><u>My Channels</b></u>\n\nyou can manage your channels in here",
       reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="addchannel":  
     chat_id = await bot.ask(chat_id=query.message.chat.id, text="Forward a message from To channel or give me your To channel id")
     if chat_id is int:
        chat_id = int(chat_id)
     else:
        chat_id = chat_id.forward_from_chat.id
     await update_configs(query.from_user.id, "channels", chat_id)
     await query.message.edit_text(
        "Successfully updated",
        reply_markup=InlineKeyboardMarkup(buttons))
      
def main_buttons():
  buttons = [[
       InlineKeyboardButton('BOTS 🤖',
                    callback_data=f'settings#bots')
       ],
       [
       InlineKeyboardButton('CHANNELS 📌',
                    callback_data=f'settings#channels')
       ],
       [
       InlineKeyboardButton('CAPTION 🖋️',
                    callback_data=f'settings#caption')
       ],
       [
       InlineKeyboardButton('FILTERS 🔵',
                    callback_data=f'settings#filters')
       ]]
  return InlineKeyboardMarkup(buttons)
       
