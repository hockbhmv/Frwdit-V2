import os
import sys
import asyncio 
import logging
from database import db 
from config import Config 
from plugins.public import FORWARD
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid

lock = {}
IS_CANCELLED = False
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TEXT = '<b><u>FORWARD STATUS</b></u>\n{}\n<b>🔘 Feched messages count:</b> <code>{}</code>\n<b>🔘 Deleted messages:</b> <code>{}</code>\n<b>🔘 Succefully forwarded file count:</b> <code>{}</code> files</code>\n<b>🔘 Skipped messages:</b> <code>{}</code>\n<b>🔘 Filtered messages:</b> <code>{}</code>\n<b>🔘 Status:</b> <code>{}</code>\n<b>🔘 percentage:</b> <code>{}</code> %'

@Client.on_callback_query(filters.regex(r'^start_public$'))
async def pub_(bot, message):
    global IS_CANCELLED, FORWARD
    user = message.from_user.id
    FORWARD = FORWARD.get(user)
    if not FORWARD:
        await message.answer("your are clicking on my old button")
        return await message.message.delete()
    if lock.get(user) and str(lock.get(user))=="True":
        return await message.answer("__please wait until previous task complete__", show_alert=True)
    #await message.answer("verifying your data's, please wait.", show_alert=True)
    configs = await db.get_configs(user)
    bot_token = configs["bot_token"]
    if not bot_token:
        return await message.message.reply_text("please add your bot using /settings !")
    try:
      client = Client(f":memory:", Config.API_ID, Config.API_HASH, bot_token=bot_token)
      await client.start()
    except (AccessTokenExpired, AccessTokenInvalid):
      return await message.message.reply_text("The given bot token is invalid")
    except Exception as e:
      return await message.message.reply_text(f"Bot Error:- {e}")
    try:
      k = await client.send_message(FORWARD['TO'], "Testing")
      await k.delete()
    except:
      return await message.answer("Please Make Your Bot Admin In Target Channel With Full Permissions", show_alert=True)
    await message.message.delete()
    test = await client.send_message(user, text="Forwarding started")
    if test:
        m = await message.message.reply_text("<i>processing</i>")
        total_files=0
        lock[user] = locked = True
        if locked:
            try:
              MSG = []
              pling=0
              fetched = 0
              deleted = 0 
              filtered = 0
              skip = int(FORWARD['SKIP'])
              total = int(FORWARD['LIMIT'])
              reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Cancel🚫', 'terminate_frwd')]])
              async for message in client.iter_messages(chat_id=FORWARD['FROM'], limit=total, offset=skip):
                    if IS_CANCELLED:
                       IS_CANCELLED = False 
                       await client.send_message(user, text="Forwarding cancelled")
                       await client.stop()
                       break 
                    pling += 1
                    if pling %10 == 0: 
                       await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, "Fetching", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                    fetched+=1 
                    if message.empty or message.service:
                       deleted+=1
                       continue 
                    filter = check_filters(configs, message)
                    if filter:
                       filtered+=1
                       continue 
                    file_name = filename(message)
                    if not configs['forward_tag']:
                       MSG.append({"msg_id": message.message_id, "file_name": file_name})
                    else:
                       MSG.append(message.message_id)
                    if len(MSG) >= 100:
                      if configs['forward_tag']:
                        try:
                          await forward(client, FORWARD, MSG)
                        except FloodWait as e:
                          await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, f"Sleeping {e.x} s", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                          await asyncio.sleep(e.x)
                          await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, "Forwarding", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                          await forward(client, FORWARD, MSG)
                        total_files+=100
                      else:
                        for msgs in MSG:
                          if IS_CANCELLED:
                            IS_CANCELLED = False 
                            await client.send_message(user, text="Forwarding cancelled")
                            await client.stop()
                            break
                          pling += 1
                          if pling % 10 == 0: 
                            await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, "Forwarding", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                          try:
                            await copy(client, FORWARD, msgs)
                            await asyncio.sleep(1.7)
                            total_files += 1
                          except FloodWait as e:
                            await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, f"Sleeping {e.x} s", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                            await asyncio.sleep(e.x)
                            await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, "Forwarding", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                            await copy(client, FORWARD, msgs)
                            total_files += 1
                            await asyncio.sleep(1.7)
                          except Exception as e:
                            print(e)
                            pass
                      MSG = []
            except Exception as e:
                print(e) 
                lock[user] = False
                await m.edit_text(f'Error: {e}')
                try:
                  await client.stop()
                except:
                  pass
            else:
                lock[user] = False
                try:
                  await client.stop()
                except:
                  pass
                buttons = [[
                    InlineKeyboardButton('📜 Support Group', url='https://t.me/venombotsupport')
                    ],[
                    InlineKeyboardButton('📡 Update Channel', url='https://t.me/venombotupdates')
                ]]
                reply_markup = InlineKeyboardMarkup(buttons)
                await edit(m, TEXT.format('\n♥️ FORWARDING SUCCESSFULLY COMPLETED\n', fetched, deleted, total_files, skip, filtered, "completed", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)

async def copy(bot, chat, msg):
   await bot.copy_message(
      chat_id=chat['TO'],
      from_chat_id=chat['FROM'],
      parse_mode="md",       
      caption=Translation.CAPTION.format(msg.get("file_name")),
      message_id=msg.get("msg_id"))

async def forward(bot, chat, msg):
   await bot.forward_messages(
      chat_id=chat['TO'],
      from_chat_id=chat['FROM'],
      message_ids=msg)
                          
async def edit(msg, text, button):
   try:
     await msg.edit_text(text=text, reply_markup=button)
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

def filename(msg, file_name=None):
   if msg.video:
     file_name = msg.video.file_name
   elif msg.document:
     file_name = msg.document.file_name
   elif msg.audio:
     file_name = msg.audio.file_name
   return file_name
                            
@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def terminate_frwding(bot, update):
    global IS_CANCELLED
    IS_CANCELLED = True
    
@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def close(bot, update):
    await update.answer()
    await update.message.delete()
