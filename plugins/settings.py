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
     buttons = [] 
     data = await db.get_configs(query.from_user.id)
     bot_id = data['bot_id']
     if bot_id is not None:
        c_bot = await bot.get_users(bot_id) 
        buttons.append([InlineKeyboardButton(f'- {c_bot.first_name}',
                         callback_data=f"settings#editbot_{bot_id})])
     else:
        buttons.append([InlineKeyboardButton('➕ Add bot ➕', 
                         callback_data="settings#addbot")])
     buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#main")])
     await query.message.edit_text(
       "<b><u>My Bots</b></u>\n\nyou can manage your bots in here",
       reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="channels":
     buttons = []
     data = await db.get_configs(query.from_user.id)
     channels = data['channels']
     if channels is not None:
        chat = await bot.get_chat(channels) 
        buttons.append([InlineKeyboardButton(f'- {chat.title}',
                         callback_data=f"settings#editchannels_{chat.id}")])
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
  
  elif type.startswith("editbot"): 
     bot_id = type.split('_')[1]
     bot = await bot.get_chat(bot_id)
     buttons = [[InlineKeyboardButton('❌ Remove ❌', callback_data=f"settings#removebot")
               ],
               [InlineKeyboardButton('back', callback_data="settings#channels")]]
     await query.message.edit_text(
        f"<b><u>Channel Details</b></u>\n\n<b>Name -</b> {bot.first_name}\n<b>Bot ID -</b> {bot.id}\n<b>Username -</b> @{bot.username}",
        reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type=="removebot":
     await update_configs(query.from_user.id, "bot_id", None)
     await update_configs(query.from_user.id, "bot_token", None)
     await query.message.edit_text(
        "successfully updated",
        reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type.startswith("editchannels"): 
     chat_id = type.split('_')[1]
     chat = await bot.get_chat(chat_id)
     buttons = [[InlineKeyboardButton('❌ Remove ❌', callback_data=f"settings#removechannel")
               ],
               [InlineKeyboardButton('back', callback_data="settings#channels")]]
     await query.message.edit_text(
        f"<b><u>Channel Details</b></u>\n\n<b>Title -</b> {chat.title}\n<b>Channel ID -</b> {chat.id}\n<b>Username -</b> @{chat.username}",
        reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type=="removechannel":
     await update_configs(query.from_user.id, "channels", None)
     await query.message.edit_text(
        "successfully updated",
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
       
