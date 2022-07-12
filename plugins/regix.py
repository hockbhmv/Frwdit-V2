import os
import sys 
import math
import time
import asyncio 
import logging
from .utils import STS
from database import db 
from .test import CLIENT 
from config import Config, temp
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.file_id import unpack_new_file_id
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TEXT = Translation.TEXT

@Client.on_callback_query(filters.regex(r'^start_public'))
async def pub_(bot, message):
    user = message.from_user.id
    temp.CANCEL[user] = False
    frwd_id = message.data.split("_")[2]
    if temp.lock.get(user) and str(temp.lock.get(user))=="True":
      return await message.answer("please wait until previous task complete", show_alert=True)
    sts = STS(frwd_id)
    if not sts.verify():
      await message.answer("your are clicking on my old button", show_alert=True)
      return await message.message.delete()
    i = sts.get(full=True)
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
      k = await client.send_message(i.TO, "Testing")
      await k.delete()
    except:
      return await m.edit(f"**Please Make Your [Bot](t.me/{_bot['username']}) Admin In Target Channel With Full Permissions**", parse_mode="combined")
    temp.forwardings += 1
    test = await client.send_message(user, text="<b>🧡 ғᴏʀᴡᴀʀᴅɪɴɢ sᴛᴀʀᴛᴇᴅ</b>")
    if test:
        sts.add('start',time=True)
        await m.edit("<b>processing</b>") 
        temp.lock[user] = locked = True
        if locked:
            try:
              MSG = []
              pling=0
              async for message in client.iter_messages(chat_id=sts.get('FROM'), limit=i.limit, offset=i.skip, skip_duplicate=True):
                    if not await is_cancelled(client, user, m, sts):
                       return
                    pling += 1
                    sts.add('fetched')
                    if pling %10 == 0: 
                       await edit(m, 'ᴘʀᴏɢʀᴇssɪɴɢ', 'Fetching', sts)
                    if message == "DUPLICATE":
                       sts.add('duplicate')
                       continue
                    if message.empty or message.service:
                       sts.add('deleted')
                       continue 
                    filter = check_filters(configs, message)
                    if filter:
                       sts.add('filtered')
                       continue 
                    if not configs['forward_tag']:
                       caption = custom_caption(message, configs)
                       MSG.append({"msg_id": message.message_id, "media": media(message), "caption": caption})
                    else:
                       MSG.append(message.message_id)
                    notcompleted = len(MSG)
                    completed = sts.get('total') - sts.get('fetched')
                    if ( notcompleted >= 100 
                         or completed <= 100
                    ):
                      if configs['forward_tag']:
                        await forward(client, MSG, m, sts)
                        sts.add('total_files', notcompleted)
                        await asyncio.sleep(10)
                      else:
                        for msgs in MSG:
                          if not await is_cancelled(client, user, m, sts):
                             return
                          pling += 1
                          if pling % 10 == 0: 
                            await edit(m, 'ᴘʀᴏɢʀᴇssɪɴɢ' , "Forwarding", sts)
                          try:
                            await copy(client, msgs, m, sts)
                            sts.add('total_files')
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
                await stop(client)
                return
            temp.forwardings -= 1
            temp.lock[user] = False
            await client.send_message(user, text="<b>🎉 ғᴏʀᴡᴀᴅɪɴɢ ᴄᴏᴍᴘʟᴇᴛᴇᴅ</b>")
            await stop(client)
            await edit(m, 'ᴄᴏᴍᴘʟᴇᴛᴇᴅ', "completed", sts)

async def copy(bot, msg, m, sts):
   try:                                  
     if msg.get("media"):
        await bot.send_cached_media(
              chat_id=sts.get('TO'),
              file_id=msg.get("media"),
              caption=msg.get("caption"))
     else:
        await bot.copy_message(
              chat_id=sts.get('TO'),
              from_chat_id=sts.get('FROM'),
              parse_mode="combined",       
              caption=msg.get("caption"),
              message_id=msg.get("msg_id"))
   except FloodWait as e:
     await edit(m, 'ᴘʀᴏɢʀᴇssɪɴɢ', f"Sleeping {e.x} s", sts)
     await asyncio.sleep(e.x)
     await edit(m, 'ᴘʀᴏɢʀᴇssɪɴɢ', "Forwarding", sts)
     await copy(bot, msg, m, sts)

async def forward(bot, msg, m, sts):
   try:                             
     await bot.forward_messages(
           chat_id=sts.get('TO'),
           from_chat_id=sts.get('FROM'),
           message_ids=msg)
   except FloodWait as e:
     await edit(m, 'ᴘʀᴏɢʀᴇssɪɴɢ', f"Sleeping {e.x} s", sts)
     await asyncio.sleep(e.x)
     await edit(m, 'ᴘʀᴏɢʀᴇssɪɴɢ', "Forwarding", sts)
     await forward(bot, msg, m, sts)                               
   
PROGRESS = """
📈 ᴘᴇʀᴄᴇɴᴛᴀɢᴇ: {0} %

♻️ sᴛᴀᴛᴜs: {1}

⏳️ ᴇᴛᴀ: {2}
"""

async def edit(msg, title, status, sts):
   i = sts.get(full=True)
   percentage = "{:.0f}".format(float(i.current)*100/float(i.total))
   text = TEXT.format(i.fetched, i.total_files, i.duplicate, i.deleted, i.skip, i.filtered, status, percentage, title)
   now = time.time()
   diff = int(now - i.start)
   speed = float(i.current) / float(diff))
   elapsed_time = round(diff) * 1000
   time_to_completion = round((int(i.total - i.current)) / int(speed)) * 1000
   estimated_total_time = elapsed_time + time_to_completion

   elapsed_time = TimeFormatter(milliseconds=elapsed_time)
   estimated_total_time = TimeFormatter(milliseconds=estimated_total_time)

   progress = "▰{0}{1}".format(
       ''.join(["▰" for i in range(math.floor(int(percentage) / 5))]),
       ''.join(["▱" for i in range(20 - math.floor(int(percentage) / 5))]))
   estimated_total_time = estimated_total_time if estimated_total_time != '' else '0 s'
   button =  [[InlineKeyboardButton(progress, f'fwrdstatus#{status}#{estimated_total_time}#{percentage}')]]
   if status in ["cancelled", "completed"]:
      button.append([InlineKeyboardButton('💟 sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ 💟', url='https://t.me/venombotsupport')])
      button.append([InlineKeyboardButton('💠 ᴜᴘᴅᴀᴛᴇ ᴄʜᴀɴɴᴇʟ 💠', url='https://t.me/venombotupdates')])
   else:
      button.append([InlineKeyboardButton('• ᴄᴀɴᴄᴇʟ', 'terminate_frwd')])
   try:
     await msg.edit_text(text=text, reply_markup=InlineKeyboardMarkup(button))
   except (MessageNotModified, FloodWait):
     pass 
   return

async def is_cancelled(client, user, msg, sts):
   if temp.CANCEL.get(user)==True:
      await edit(msg, 'ᴄᴀɴᴄᴇʟʟᴇᴅ', "cancelled", sts)
      await client.send_message(user, text="<b>❌ ғᴏʀᴡᴀᴅɪɴɢ ᴄᴀɴᴄᴇʟʟᴇᴅ</b>")
      temp.forwardings -= 1
      await stop(client)
      return False 
   return True 

async def stop(client):
   try:
     await client.stop()
   except:
     pass 

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
   elif msg.media:
      size = data.get('file_size', 1000)
      fsize = getattr(getattr(msg, msg.media), 'file_size', None)
      if fsize and size != 0:
         if fsize <= size:
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
 
@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def terminate_frwding(bot, m):
    user_id = m.from_user.id 
    temp.lock[user_id] = False
    temp.CANCEL[user_id] = True 
    await m.answer("Forwarding cancelled !", show_alert=True)
          
@Client.on_callback_query(filters.regex(r'^fwrdstatus'))
async def status(bot, msg):
    _, sts, est_time, percentage = msg.data.split("#")
    est_time = '0 s' if sts in ['completed', 'cancelled'] else est_time
    return await msg.answer(PROGRESS.format(percentage, sts, est_time), show_alert=True)
                     
@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def close(bot, update):
    await update.answer()
    await update.message.delete()
