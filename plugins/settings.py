import asyncio 
from database import db
from pyrogram import Client, filters
from .test import get_configs, update_configs, CLIENT
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
        buttons.append([InlineKeyboardButton('✚ Add bot ✚', 
                         callback_data="settings#addbot")])
        buttons.append([InlineKeyboardButton('✚ Add User bot ✚', 
                         callback_data="settings#adduserbot")])
     buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#main")])
     await query.message.edit_text(
       "<b><u>My Bots</b></u>\n\n<b>You can manage your bots in here</b>",
       reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="addbot":
     await query.message.delete()
     bot = CLIENT().add_bot(bot, query)
     if bot != True: return
     await query.message.reply_text(
        "<b>bot token successfully added to db</b>",
        reply_markup=InlineKeyboardMarkup(buttons))
  
  elif type=="adduserbot":
     await query.message.delete()
     user = CLIENT().add_session(bot, query)
     if user != True: return
     await query.message.reply_text(
        "<b>session successfully added to db</b>",
        reply_markup=InlineKeyboardMarkup(buttons))
      
  elif type=="channels":
     buttons = []
     channels = await db.get_user_channels(user_id)
     async for channel in channels:
        buttons.append([InlineKeyboardButton(f"{channel['title']}",
                         callback_data=f"settings#editchannels_{channel['chat_id']}")])
     buttons.append([InlineKeyboardButton('✚ Add Channel ✚', 
                      callback_data="settings#addchannel")])
     buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#main")])
     await query.message.edit_text( 
       "<b><u>My Channels</b></u>\n\n<b>you can manage your channels in here</b>",
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
               [InlineKeyboardButton('back', callback_data="settings#bots")]]
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
        buttons.append([InlineKeyboardButton('✚ Add Caption ✚', 
                      callback_data="settings#addcaption")])
     else:
        buttons.append([InlineKeyboardButton('See Caption', 
                      callback_data="settings#seecaption")])
        buttons.append([InlineKeyboardButton('🗑️ Delete Caption', 
                      callback_data="settings#deletecaption")])
     buttons.append([InlineKeyboardButton('back', 
                      callback_data="settings#main")])
     await query.message.edit_text(
        "<b><u>CUSTOM CAPTION</b></u>\n\n<b>You can set a custom caption to videos and documents. Normaly use its default caption</b>\n\n<b><u>AVAILABLE FILLINGS:</b></u>\n- <code>{filename}</code> : Filename\n- <code>{size}</code> : File size\n- <code>{caption}</code> : default caption",
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
   
  elif type.startswith("file_size"):
    settings = await get_configs(user_id)
    size = settings.get('file_size', 0)
    await query.message.edit_text(
       f'<b><u>SIZE LIMIT</b></u>\n\nyou can set file size limit to forward\n\n<b>current</b>: <code>{size} MB</code>',
       reply_markup=size_button(size))
      
  elif type.startswith("update_size"):
    size = int(query.data.split('-')[1])
    if 0 < size > 2000:
      return
    await update_configs(user_id, 'file_size', size)
    await query.message.edit_text(
       f'<b><u>SIZE LIMIT</b></u>\n\nyou can set file size limit to forward\n\n<b>current</b>: <code>{size} MB</code>',
       reply_markup=size_button(size))
  
  elif type == "add_extenstion":
    ext = await bot.ask(user_id, text="send your extensions")
    if ex.text == '/cancel':
       return await ext.reply_text(
                  "<b>process canceled</b>",
                  reply_markup=InlineKeyboardMarkup(buttons))
    extensions = ext.text.split()
    extension = await get_configs(user_id).get('extension', None)
    if extension:
        for extn in extensions:
            extension.append(extn)
    else:
        extension = extensions
    await update_configs(user_id, 'extension', extension)
  
  elif type == "get_extension":
    i = 0
    btn = []
    extensions = (await get_configs(user_id)).get('extension', None)
    if extensions:
      for extn in extensions:
        if i >= 5:
            i = 0
        if i == 0:
           btn.append([InlineKeyboardButton(extn, f'settings#extn_{extn}')])
           i += 1
           continue
        elif i > 0:
           btn[-1].append(InlineKeyboardButton(extn, f'settings#extn_{extn}'))
           i += 1
    btn.append([InlineKeyboardButton('✚ ADD ✚', 'settings#add_extension')])
    btn.append([InlineKeyboardButton('Remove all', 'settings#rmve_all_extension')])
    btn.append([InlineKeyboardButton('back', 'settings#main')])
    await query.message.edit_text(
        text='your skipping extensions using file_name',
        reply_markup=InlineKeyboardMarkup(btn))
  
  elif type == "rmve_all_extension":
      await update_configs(user_id, 'extension', None)
      await query.message.reply_text(text="successfully deleted",
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

def size_button(size):
  buttons = [[
       InlineKeyboardButton('+5',
                    callback_data=f'settings#update_size-{size + 5}'),
       InlineKeyboardButton('+10',
                    callback_data=f'settings#update_size-{size + 10}'),
       InlineKeyboardButton('+50',
                    callback_data=f'settings#update_size-{size + 50}'),
       InlineKeyboardButton('+100',
                    callback_data=f'settings#update_size-{size + 100}'),
       InlineKeyboardButton('-5',
                    callback_data=f'settings#update_size-{size - 5}'),
       InlineKeyboardButton('-10',
                    callback_data=f'settings#update_size-{size - 10}'),
       InlineKeyboardButton('-50',
                    callback_data=f'settings#update_size-{size - 50}'),
       InlineKeyboardButton('-100',
                    callback_data=f'settings#update_size-{size - 100}')
       ],[
       InlineKeyboardButton('back',
                    callback_data="settings#main")
     ]]
  return InlineKeyboardMarkup(buttons)
       
async def filters_buttons(user_id):
  filters = await get_configs(user_id)
  buttons = [[
       InlineKeyboardButton('🏷️ Forward tag',
                    callback_data=f'settings_#updatefilter-forward_tag-{filters["forward_tag"]}'),
       InlineKeyboardButton('☑' if filters['forward_tag'] else '☒',
                    callback_data=f'settings#updatefilter-forward_tag-{filters["forward_tag"]}')
       ],[
       InlineKeyboardButton('🖍️ Texts',
                    callback_data=f'settings_#updatefilter-texts-{filters["texts"]}'),
       InlineKeyboardButton('☑' if filters['texts'] else '☒',
                    callback_data=f'settings#updatefilter-texts-{filters["texts"]}')
       ],[
       InlineKeyboardButton('📁 Documents',
                    callback_data=f'settings_#updatefilter-documents-{filters["documents"]}'),
       InlineKeyboardButton('☑' if filters['documents'] else '☒',
                    callback_data=f'settings#updatefilter-documents-{filters["documents"]}')
       ],[
       InlineKeyboardButton('🎞️ Videos',
                    callback_data=f'settings_#updatefilter-videos-{filters["videos"]}'),
       InlineKeyboardButton('☑' if filters['videos'] else '☒',
                    callback_data=f'settings#updatefilter-videos-{filters["videos"]}')
       ],[
       InlineKeyboardButton('📷 Photos',
                    callback_data=f'settings_#updatefilter-photos-{filters["photos"]}'),
       InlineKeyboardButton('☑' if filters['photos'] else '☒',
                    callback_data=f'settings#updatefilter-photos-{filters["photos"]}')
       ],[
       InlineKeyboardButton('🎧 Audios',
                    callback_data=f'settings_#updatefilter-audios-{filters["audios"]}'),
       InlineKeyboardButton('☑' if filters['audios'] else '☒',
                    callback_data=f'settings#updatefilter-audios-{filters["audios"]}')
       ],[
       InlineKeyboardButton('🎭 Animations',
                    callback_data=f'settings_#updatefilter-animations-{filters["animations"]}'),
       InlineKeyboardButton('☑' if filters['animations'] else '☒',
                    callback_data=f'settings#updatefilter-animations-{filters["animations"]}')
       ],[
       InlineKeyboardButton('▶️ Skip duplicate files',
                    callback_data='commingsoon'),
       InlineKeyboardButton('comming soon',
                    callback_data='commingsoon')
       ],[
       InlineKeyboardButton('size limit',
                    callback_data='settings#file_size'),
       InlineKeyboardButton('extension',
                    callback_data='settings#get_extension')
       ],[
       InlineKeyboardButton('back',
                    callback_data="settings#main")
       ]]
  return InlineKeyboardMarkup(buttons) 
