import os
import sys 
import math
import time
import asyncio 
import logging
from database import db 
from .test import CLIENT 
from config import Config, temp
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.file_id import unpack_new_file_id
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 

STATUS = {}
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
    frwd_id = message.data.split("_")[2]
    if temp.lock.get(user) and str(temp.lock.get(user))=="True":
      return await message.answer("please wait until previous task complete", show_alert=True)
    details = temp.FORWARD.get(frwd_id)
    if not details:
      await message.answer("your are clicking on my old button", show_alert=True)
      return await message.message.delete()
    m = await message.message.edit_text("<b>verifying your data's, please wait.</b>")
    _bot = await db.get_bot(user)
    if not _bot:
      return await m.edit("<b>You didn't added any bot. Please add a bot using /settings !</b>")
    configs = await db.get_configs(user)
    try:
      client = await bot.start_clone_bot(CLIENT(_bot['token']).bot)
    except Exception as e:  
      return await m.edit(e)
    try:
      k = await client.send_message(details['TO'], "Testing")
      await k.delete()
    except:
      return await m.edit(f"**Please Make Your [Bot](t.me/{_bot['username']}) Admin In Target Channel With Full Permissions**", parse_mode="combined")
    temp.forwardings += 1
    test = await client.send_message(user, text="<b>🧡 Forwarding Started</b>")
    if test:
        await m.edit("<b>processing</b>") 
        start = time.time()
        temp.lock[user] = locked = True
        if locked:
            try:
              MSG = []
              pling=0
              skip = int(details['SKIP'])
              total = int(details['LIMIT'])
              fetched = skip
              STATUS[frwd_id] = {'skip': skip, 'total': total, 'fetched': skip, 'start': start,
                                 'deleted': 0, 'filtered': 0, 'duplicate': 0, 'total_files': 0}
              reply_markup = None
              async for message in client.iter_messages(chat_id=details['FROM'], limit=total, offset=skip, skip_duplicate=True):
                    if temp.CANCEL.get(user)==True:
                       await edit(m, '\n♥️ FORWARDING CANCELLED\n', "cancelled", forward_id)
                       await client.send_message(user, text="<b>❌ Forwarding Cancelled</b>")
                       temp.forwardings -= 1
                       await client.stop()
                       return 
                    pling += 1
                    add(frwd_id, 'fetched')
                    if pling %10 == 0: 
                       await edit(m, '', 'Fetching', frwd_id, reply_markup)
                    if message == "DUPLICATE":
                       add(frwd_id, 'duplicate')
                       continue
                    if message.empty or message.service:
                       add(frwd_id, 'deleted')
                       continue 
                    filter = check_filters(configs, message)
                    if filter:
                       add(frwd_id, 'filtered')
                       continue 
                    if not configs['forward_tag']:
                       caption = custom_caption(message, configs)
                       MSG.append({"msg_id": message.message_id, "media": media(message), "caption": caption})
                    else:
                       MSG.append(message.message_id)
                    notcompleted = len(MSG)
                    completed = get(frwd_id,'total') - get(frwd_id, 'fetched')
                    if ( notcompleted >= 100 
                         or completed <= 100
                    ):
                      if configs['forward_tag']:
                        await forward(client, details, MSG, m, frwd_id, reply_markup)
                        add(frwd_id, 'total_files', notcompleted)
                        await asyncio.sleep(10)
                      else:
                        for msgs in MSG:
                          if temp.CANCEL.get(user)==True:
                            await edit(m, '\n♥️ FORWARDING CANCELLED\n', "cancelled", forward_id)
                            await client.send_message(user, text="<b>❌ Forwarding Cancelled</b>")
                            temp.forwardings -= 1
                            await client.stop()
                            return
                          pling += 1
                          if pling % 10 == 0: 
                            await edit(m, '' , "Forwarding", frwd_id)
                          try:
                            await copy(client, details, msgs, m, frwd_id)
                            add(frwd_id, 'total_files')
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
                return
            temp.forwardings -= 1
            temp.lock[user] = False
            try:
              await client.stop()
            except:
              pass 
            await edit(m, '\n♥️ FORWARDING SUCCESSFULLY COMPLETED\n', "completed", forward_id)

async def copy(bot, chat, msg, sts, frwd_id):
   try:                                  
     if msg.get("media"):
        await bot.send_cached_media(
              chat_id=chat['TO'],
              file_id=msg.get("media"),
              caption=msg.get("caption"))
     else:
        await bot.copy_message(
              chat_id=chat['TO'],
              from_chat_id=chat['FROM'],
              parse_mode="combined",       
              caption=msg.get("caption"),
              message_id=msg.get("msg_id"))
   except FloodWait as e:
     await edit(sts, '', f"Sleeping {e.x} s", frwd_id)
     await asyncio.sleep(e.x)
     await edit(sts, '', "Forwarding", frwd_id)
     await copy(bot, chat, msg, sts, frwd_id)

async def forward(bot, chat, msg, sts, frwd_id):
   try:                             
     await bot.forward_messages(
           chat_id=chat['TO'],
           from_chat_id=chat['FROM'],
           message_ids=msg)
   except FloodWait as e:
     await edit(sts, '', f"Sleeping {e.x} s", frwd_id)
     await asyncio.sleep(e.x)
     await edit(sts, '', "Forwarding", frwd_id)
     await forward(bot, chat, msg, sts, frwd_id)                               
   
PROGRESS = """
📈 Percentage: {0} %
♻️ status: {1}
⏳️ETA: {2}
"""

async def edit(msg, title, status, frwd_id, buttons=None):
   total_files, skip, total, fetched, deleted, filtered, duplicate, start = get(frwd_id, full=True)
   current = deleted + total_files + duplicate + filtered + skip                               
   percentages = "{:.0f}".format(float(current)*100/float(total))
   text = TEXT.format(title, fetched, total_files, duplicate, deleted, skip, filtered, status, percentages)
   #text = "hi"
   if not buttons:
        now = time.time()
        diff = now - start
        percentage = current * 100 / total
        speed = current / diff
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / speed) * 1000
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time = TimeFormatter(milliseconds=elapsed_time)
        estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

        progress = "▰{0}{1}".format(
            ''.join(["▰" for i in range(math.floor(percentage / 5))]),
            ''.join(["▱" for i in range(20 - math.floor(percentage / 5))]))
        estimated_total_time = estimated_total_time if estimated_total_time != '' else '0 s'
        button =  [[
                InlineKeyboardButton(progress, f'fwrdstatus#{status}#{estimated_total_time}#{percentages}')
                ],[
                InlineKeyboardButton('Cancel🚫', 'terminate_frwd')]]
   try:
     await msg.edit_text(text=text, reply_markup=InlineKeyboardMarkup(button))
   except (MessageNotModified, FloodWait):
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
  if (msg.video or msg.document or msg.audio or msg.photo):
     media = getattr(msg, msg.media)
     file_id, file_ref = unpack_new_file_id(media.file_id)
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

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
        ((str(hours) + "h, ") if hours else "") + \
        ((str(minutes) + "m, ") if minutes else "") + \
        ((str(seconds) + "s, ") if seconds else "") + \
        ((str(milliseconds) + "ms, ") if milliseconds else "")
    return tmp[:-2]

def add(_id, key, value=1):
   current = STATUS.get(_id)
   current[key] += value
   STATUS[_id] = current

def get(_id, key=None, full=False):
   get = STATUS.get(_id)
   if not full:
      return get[key]
   return get['total_files'], get['skip'], get["total"], get['fetched'], get['deleted'], get['filtered'], get['duplicate'], get['start']

@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def terminate_frwding(bot, m):
    user_id = m.from_user.id 
    temp.lock[user_id] = False
    temp.CANCEL[user_id] = True 
    await m.answer("Forwarding cancelled !", show_alert=True)
          
@Client.on_callback_query(filters.regex(r'^fwrdstatus'))
async def status(bot, msg):
    _, sts, est_time, percentage = msg.data.split("#")
    return await msg.answer(PROGRESS.format(percentage, sts, est_time), show_alert=True)
                     
@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def close(bot, update):
    await update.answer()
    await update.message.delete()
