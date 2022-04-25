import os
import sys
import asyncio 
import logging
from database import db 
from config import Config, temp
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TEXT = Translation.TEXT
buttons = [[
          InlineKeyboardButton('📜 Support Group', url='https://t.me/venombotsupport')
          ],[
          InlineKeyboardButton('📡 Update Channel', url='https://t.me/venombotupdates')
          ]]

@Client.on_callback_query(filters.regex(r'^start_public'))
async def pub_(bot, message):
    user = message.from_user.id
    temp.CANCEL[user] = False
    forward_id = message.data.split("_")[2]
    if temp.lock.get(user) and str(temp.lock.get(user))=="True":
      return await message.answer("please wait until previous task complete", show_alert=True)
    details = temp.FORWARD.get(forward_id)
    if not details:
      await message.answer("your are clicking on my old button", show_alert=True)
      return await message.message.delete()
    m = await message.message.edit_text("<b>verifying your data's, please wait.</b>")
    _bot = await db.get_bot(user)
    if not _bot:
      return await m.edit("<b>You didn't added any bot. Please add a bot using /settings !</b>")
    configs = await db.get_configs(user)
    try:
      client = Client(f":memory:", Config.API_ID, Config.API_HASH, bot_token=_bot['token'])
      await client.start()
    except (AccessTokenExpired, AccessTokenInvalid):
      return await m.edit("<b>The given bot token is expired or invalid. please change it !</b>")
    except Exception as e:
      return await m.edit(f"<b>Bot Error:-</b>\n\n<code>{e}</code>")
    try:
      k = await client.send_message(details['TO'], "Testing")
      await k.delete()
    except:
      return await m.edit(f"**Please Make Your [Bot](t.me/{_bot['username']}) Admin In Target Channel With Full Permissions**", parse_mode="combined")
    temp.forwardings += 1
    test = await client.send_message(user, text="<b>🧡 Forwarding Started</b>")
    if test:
        await m.edit("<i>processing</i>") 
        total_files=0
        temp.lock[user] = locked = True
        if locked:
            try:
              MSG = []
              skip = int(details['SKIP'])
              total = int(details['LIMIT'])
              fetched = skip
              pling=0
              deleted = 0 
              filtered = 0
              reply_markup = [[InlineKeyboardButton('Cancel🚫', 'terminate_frwd')]]
              async for message in client.iter_messages(chat_id=details['FROM'], limit=total, offset=skip):
                    if temp.CANCEL.get(user)==True:
                       await edit(m, TEXT.format('\n♥️ FORWARDING CANCELLED\n', fetched, total_files, deleted, skip, filtered, "cancelled", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), buttons)
                       await client.send_message(user, text="<b>❌ Forwarding Cancelled</b>")
                       temp.forwardings -= 1
                       await client.stop()
                       return 
                    pling += 1
                    if pling %10 == 0: 
                       await edit(m, TEXT.format('', fetched, total_files, deleted, skip, filtered, "Fetching", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                    fetched+=1 
                    if message.empty or message.service:
                       deleted+=1
                       continue 
                    filter = check_filters(configs, message)
                    if filter:
                       filtered+=1
                       continue 
                    if not configs['forward_tag']:
                       caption = custom_caption(message, configs)
                       MSG.append({"msg_id": message.message_id, "media": media(message), "caption": caption})
                    else:
                       MSG.append(message.message_id)
                    notcompleted = len(MSG)
                    completed = total - fetched
                    if ( notcompleted >= 100 
                         or completed <= 100
                    ):
                      if configs['forward_tag']:
                        try:
                          await forward(client, details, MSG)
                        except FloodWait as e:
                          await edit(m, TEXT.format('', fetched, total_files, deleted, skip, filtered, f"Sleeping {e.x} s", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                          await asyncio.sleep(e.x)
                          await edit(m, TEXT.format('', fetched, total_files, deleted, skip, filtered, "Forwarding", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                          await forward(client, details, MSG)
                        total_files+=notcompleted 
                        await asyncio.sleep(10)
                      else:
                        for msgs in MSG:
                          if temp.CANCEL.get(user)==True:
                            await edit(m, TEXT.format('\n♥️ FORWARDING CANCELLED\n', fetched, total_files, deleted, skip, filtered, "cancelled", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), buttons)
                            await client.send_message(user, text="<b>❌ Forwarding Cancelled</b>")
                            temp.forwardings -= 1
                            await client.stop()
                            return
                          pling += 1
                          if pling % 10 == 0: 
                            await edit(m, TEXT.format('', fetched, total_files, deleted, skip, filtered, "Forwarding", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                          try:
                            await copy(client, details, msgs)
                            await asyncio.sleep(1.7)
                            total_files += 1
                          except FloodWait as e:
                            await edit(m, TEXT.format('', fetched, total_files, deleted, skip, filtered, f"Sleeping {e.x} s", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                            await asyncio.sleep(e.x)
                            await edit(m, TEXT.format('', fetched, total_files, deleted, skip, filtered, "Forwarding", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                            await copy(client, details, msgs)
                            total_files += 1
                            await asyncio.sleep(1.7)
                          except Exception as e:
                            print(e)
                            pass
                      MSG = []
            except Exception as e:
                print(e) 
                temp.forwardings -= 1
                temp.lock[user] = False
                await m.edit_text(f'<b>Error:</b>\n\n<code>{e}</code>')
                try:
                  await client.stop()
                except:
                  pass
            temp.forwardings -= 1
            temp.lock[user] = False
            try:
              await client.stop()
            except:
              pass
            await edit(m, TEXT.format('\n♥️ FORWARDING SUCCESSFULLY COMPLETED\n', fetched, total_files, deleted, skip, filtered, "completed", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), buttons)

async def copy(bot, chat, msg):
   if msg.get("media"):
     await bot.send_cached_media(
        chat_id=chat['TO'],
        file_id=msg.get("msg_id"),
        caption=msg.get("caption"))
   else:
     await bot.copy_message(
        chat_id=chat['TO'],
        from_chat_id=chat['FROM'],
        parse_mode="combined",       
        caption=msg.get("caption"),
        message_id=msg.get("msg_id"))

async def forward(bot, chat, msg):
   await bot.forward_messages(
      chat_id=chat['TO'],
      from_chat_id=chat['FROM'],
      message_ids=msg)
                          
async def edit(msg, text, button):
   try:
     await msg.edit_text(text=text, reply_markup=InlineKeyboardMarkup(button))
   except MessageNotModified:
     pass 
   return

def check_filters(data, msg):
   if not data['texts'] and msg.text:
      return True
   elif not data['photos'] and msg.photo:
      return True
   elif not data['videos'] and msg.video:
      return True 
   elif not data['documents'] and msg.document:
      return True 
   elif not data['audios'] and (msg.audio or msg.voice):
      return True
   elif not data['animations'] and (msg.animation or msg.sticker):
      return True 
   return False 

def custom_caption(msg, get):
  if not (msg.media 
     and get['caption']):
     return None
  if (msg.video or msg.document or msg.audio):
     media = getattr(msg, msg.media)
     file_name = getattr(media, 'file_name', '')
     file_size = getattr(media, 'file_size', '')
     caption = getattr(media, 'caption', file_name)
     return get['caption'].format(filename=file_name, size=get_size(file_size), caption=caption)
  else:
     return None

def get_size(size):
  units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
  size = float(size)
  i = 0
  while size >= 1024.0 and i < len(units):
     i += 1
     size /= 1024.0
  return "%.2f %s" % (size, units[i]) 

def media(msg):
  media = msg.media
  if media in ["video", "audio", "photo", "document"]:
     media = getattr(msg, media, None)
     if not media:
       return None 
     return media.file_id
  return None 
 
@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def terminate_frwding(bot, m):
    user_id = m.from_user.id 
    temp.lock[user_id] = False
    temp.CANCEL[user_id] = True 
    await m.answer("Forwarding cancelled !", show_alert=True)
    
@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def close(bot, update):
    await update.answer()
    await update.message.delete()
