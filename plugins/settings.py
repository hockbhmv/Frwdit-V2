import asyncio 
from database import db
from pyrogram import Client, filters
from .test import get_configs, update_configs, bot_token
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
                         callback_data=f"settings#editbot_{bot_id}")])
     else:
        buttons.append([InlineKeyboardButton('➕ Add bot ➕', 
                         callback_data="settings#addbot")])
     buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#main")])
     await query.message.edit_text(
       "<b><u>My Bots</b></u>\n\nyou can manage your bots in here",
       reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="addbot":
     await query.message.delete()
     bot = await bot_token(bot, query, True)
     if not bot:
        return
     await query.message.edit_text(
        "bot token successfully added to db",
        reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="channels":
     buttons = []
     data = await db.get_configs(query.from_user.id)
     channels = data['channels']
     if channels is not None:
        chat = await bot.get_chat(channels) 
        buttons.append([InlineKeyboardButton(f'- {chat.title}',
                         callback_data=f"settings#editchannels_{chat.id}")])
     buttons.append([InlineKeyboardButton('➕ Add Channel ➕', 
                      callback_data="settings#addchannel")])
     buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#main")])
     await query.message.edit_text( 
       "<b><u>My Channels</b></u>\n\nyou can manage your channels in here",
       reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="addchannel":  
     await query.message.delete()
     chat_ids = await bot.ask(chat_id=query.message.chat.id, text="<b><u>SET TO CHANNELS</b></u>\nForward a message from To channel or enter To channel id\n/cancel - <code>cancel this process</code>")
     if not chat_ids.forward_from_chat:
        chat_id = int(chat_id)
     elif chat_ids.text=="/cancel":
        return await chat_ids.reply_text(
                  "process canceled",
                  reply_markup=InlineKeyboardMarkup(buttons))
     else:
        chat_id = chat_ids.forward_from_chat.id
     await update_configs(query.from_user.id, "channels", chat_id)
     await bot.delete_messages([chat_ids, chat_ids.reply_to_message])
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
        f"<b><u>📄 BOT DETAILS</b></u>\n\n<b>- NAME:</b> <code>{bot.first_name}</code>\n<b>- BOT ID:</b> <code>{bot.id}</code>\n<b>- USERNAME:</b> @{bot.username}",
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
     username = "@" + chat.username if chat.username else "None"
     buttons = [[InlineKeyboardButton('❌ Remove ❌', callback_data=f"settings#removechannel")
               ],
               [InlineKeyboardButton('back', callback_data="settings#channels")]]
     await query.message.edit_text(
        f"<b><u>📄 CHANNEL DETAILS</b></u>\n\n<b>- TITLE:</b> <code>{chat.title}</code>\n<b>- CHANNEL ID: </b> <code>{chat.id}</code>\n<b>- USERNAME:</b> {username}",
        reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type=="removechannel":
     await update_configs(query.from_user.id, "channels", None)
     await query.message.edit_text(
        "successfully updated",
        reply_markup=InlineKeyboardMarkup(buttons))
                               
  elif type=="caption":
     buttons = []
     data = await get_configs(query.from_user.id)
     caption = data['caption']
     if caption is None:
        buttons.append([InlineKeyboardButton('➕ Add Caption ➕', 
                      callback_data="settings#addcaption")])
     else:
        buttons.append([InlineKeyboardButton('See Caption', 
                      callback_data="settings#seecaption")])
        buttons.append([InlineKeyboardButton('🗑️ Delete Caption', 
                      callback_data="settings#deletecaption")])
     buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#main")])
     await query.message.edit_text(
        "<b><u>CUSTOM CAPTION</b></u>\n\nyou can set a custom caption to videos and documents. normal use its default caption\n\n<b><u>AVAILABLE FILLINGS:</b></u>\n- <code>{filename}</code> : Filename\n- <code>{size}</code> : File size\n- <code>{caption}</code> : default caption",
        reply_markup=InlineKeyboardMarkup(buttons))
                               
  elif type=="seecaption":   
     data = await get_configs(query.from_user.id)
     buttons = [[InlineKeyboardButton('🖋️ Edit Caption', 
                  callback_data="settings#addcaption")
               ],[
               InlineKeyboardButton('back', 
                 callback_data="settings#caption")]]
     await query.message.edit_text(
        f"<b><u>YOUR CUSTOM CAPTION</b></u>\n\n<code>{data['caption']}</code>",
        reply_markup=InlineKeyboardMarkup(buttons))
    
  elif type=="deletecaption":
     await update_configs(query.from_user.id, 'caption', None)
     await query.message.edit_text(
        "successfully updated",
        reply_markup=InlineKeyboardMarkup(buttons))
                              
  elif type=="addcaption":
     await query.message.delete()
     caption = await bot.ask(query.message.chat.id, text="Send your custom caption\n/cancel - <code>cancel this process</code>")
     if caption.text=="/cancel":
        return await caption.reply_text(
                  "process canceled !",
                  reply_markup=InlineKeyboardMarkup(buttons))
     await update_configs(query.from_user.id, "caption", caption.text)
     await caption.reply_text(
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
       
