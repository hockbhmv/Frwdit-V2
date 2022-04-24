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
  user_id = query.from_user.id
  i, type = query.data.split("#")
  buttons = [[InlineKeyboardButton('back', callback_data="settings#main")]]
  
  if type=="main":
     await query.message.edit_text(
       "change your settings as your wish",
       reply_markup=main_buttons())
       
  elif type=="bots":
     buttons = [] 
     _bot = await db.get_bot(user_id)
     if _bot is not None:
        buttons.append([InlineKeyboardButton(_bot['name'],
                         callback_data=f"settings#editbot")])
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
     bot = await bot_token(bot, query)
     if not bot:
        return
     await query.message.reply_text(
        "bot token successfully added to db",
        reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="channels":
     buttons = []
     channels = await db.get_user_channels(user_id)
     async for channel in channels:
        buttons.append([InlineKeyboardButton(f"{channel['title']}",
                         callback_data=f"settings#editchannels_{channel['chat_id']}")])
     buttons.append([InlineKeyboardButton('➕ Add Channel ➕', 
                      callback_data="settings#addchannel")])
     buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#main")])
     await query.message.edit_text( 
       "<b><u>My Channels</b></u>\n\nyou can manage your channels in here",
       reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="addchannel":  
     await query.message.delete()
     chat_ids = await bot.ask(chat_id=query.message.chat.id, text="<b><u>SET TO CHANNELS</b></u>\nForward a message from To channel\n/cancel - <code>cancel this process</code>")
     if chat_ids.text=="/cancel":
        return await chat_ids.reply_text(
                  "process canceled",
                  reply_markup=InlineKeyboardMarkup(buttons))
     elif not chat_ids.forward_date:
        return await chat_ids.reply("This is not a forward message")
     else:
        chat_id = chat_ids.forward_from_chat.id
        title = chat_ids.forward_from_chat.title
        username = chat_ids.forward_from_chat.username
        username = "@" + username if username else "private"
     chat = await db.add_channel(user_id, chat_id, title, username)
     await query.message.reply_text(
        "Successfully updated" if chat else "This channel already added",
        reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="editbot": 
     bot = await db.get_bot(user_id)
     buttons = [[InlineKeyboardButton('❌ Remove ❌', callback_data=f"settings#removebot")
               ],
               [InlineKeyboardButton('back', callback_data="settings#channels")]]
     await query.message.edit_text(
        f"<b><u>📄 BOT DETAILS</b></u>\n\n<b>- NAME:</b> <code>{bot['name']}</code>\n<b>- BOT ID:</b> <code>{bot['id']}</code>\n<b>- USERNAME:</b> @{bot['username']}",
        reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type=="removebot":
     await update_configs(user_id, 'bot', None)
     await query.message.edit_text(
        "successfully updated",
        reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type.startswith("editchannels"): 
     chat_id = type.split('_')[1]
     chat = await db.get_channel_details(user_id, chat_id)
     buttons = [[InlineKeyboardButton('❌ Remove ❌', callback_data=f"settings#removechannel_{chat_id}")
               ],
               [InlineKeyboardButton('back', callback_data="settings#channels")]]
     await query.message.edit_text(
        f"<b><u>📄 CHANNEL DETAILS</b></u>\n\n<b>- TITLE:</b> <code>{chat['title']}</code>\n<b>- CHANNEL ID: </b> <code>{chat['chat_id']}</code>\n<b>- USERNAME:</b> {chat['username']}",
        reply_markup=InlineKeyboardMarkup(buttons))
                                             
  elif type.startswith("removechannel"):
     chat_id = type.split('_')[1]
     await db.remove_channel(user_id, chat_id)
     await query.message.edit_text(
        "successfully updated",
        reply_markup=InlineKeyboardMarkup(buttons))
                               
  elif type=="caption":
     buttons = []
     data = await get_configs(user_id)
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
     data = await get_configs(user_id)
     buttons = [[InlineKeyboardButton('🖋️ Edit Caption', 
                  callback_data="settings#addcaption")
               ],[
               InlineKeyboardButton('back', 
                 callback_data="settings#caption")]]
     await query.message.edit_text(
        f"<b><u>YOUR CUSTOM CAPTION</b></u>\n\n<code>{data['caption']}</code>",
        reply_markup=InlineKeyboardMarkup(buttons))
    
  elif type=="deletecaption":
     await update_configs(user_id, 'caption', None)
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
     await update_configs(user_id, 'caption', caption.text)
     await caption.reply_text(
        "successfully updated",
        reply_markup=InlineKeyboardMarkup(buttons))
   
  elif type=="filters":
     await query.message.edit_text(
        "<b><u>CUSTOM FILTERS</b></u>\n\nconfigure the type of messages which you want forward",
        reply_markup=await filters_buttons(user_id))
  
  elif type.startswith("updatefilter"):
     i, key, value = type.split('-')
     if value=="True":
        await update_configs(user_id, key, False)
     else:
        await update_configs(user_id, key, True)
     await query.message.edit_text(
        "<b><u>CUSTOM FILTERS</b></u>\n\nconfigure the type of messages which you want forward",
        reply_markup=await filters_buttons(user_id))
        
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
       
async def filters_buttons(user_id):
  filters = await get_configs(user_id)
  buttons = [[
       InlineKeyboardButton('🏷️ Forward tag',
                    callback_data=f'settings_#updatefilter-forward_tag-{filters["forward_tag"]}'),
       InlineKeyboardButton('✔️' if filters['forward_tag'] else '❌',
                    callback_data=f'settings#updatefilter-forward_tag-{filters["forward_tag"]}')
       ],[
       InlineKeyboardButton('🖍️ Texts',
                    callback_data=f'settings_#updatefilter-texts-{filters["texts"]}'),
       InlineKeyboardButton('✔️' if filters['texts'] else '❌',
                    callback_data=f'settings#updatefilter-texts-{filters["texts"]}')
       ],[
       InlineKeyboardButton('📁 Documents',
                    callback_data=f'settings_#updatefilter-documents-{filters["documents"]}'),
       InlineKeyboardButton('✔️' if filters['documents'] else '❌',
                    callback_data=f'settings#updatefilter-documents-{filters["documents"]}')
       ],[
       InlineKeyboardButton('🎞️ Videos',
                    callback_data=f'settings_#updatefilter-videos-{filters["videos"]}'),
       InlineKeyboardButton('✔️' if filters['videos'] else '❌',
                    callback_data=f'settings#updatefilter-videos-{filters["videos"]}')
       ],[
       InlineKeyboardButton('📷 Photos',
                    callback_data=f'settings_#updatefilter-photos-{filters["photos"]}'),
       InlineKeyboardButton('✔️' if filters['photos'] else '❌',
                    callback_data=f'settings#updatefilter-photos-{filters["photos"]}')
       ],[
       InlineKeyboardButton('🎧 Audios',
                    callback_data=f'settings_#updatefilter-audios-{filters["audios"]}'),
       InlineKeyboardButton('✔️' if filters['audios'] else '❌',
                    callback_data=f'settings#updatefilter-audios-{filters["audios"]}')
       ],[
       InlineKeyboardButton('🎭 Animations',
                    callback_data=f'settings_#updatefilter-animations-{filters["animations"]}'),
       InlineKeyboardButton('✔️' if filters['animations'] else '❌',
                    callback_data=f'settings#updatefilter-animations-{filters["animations"]}')
       ],[
       InlineKeyboardButton('back',
                    callback_data="settings#main")
       ]]
  return InlineKeyboardMarkup(buttons) 
