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
TEXT = '<b><u>FORWARD STATUS</b></u>\n{}\n<b>🔘 Feched messages count:</b> <code>{}</code>\n<b>🔘 Deleted messages:</b> <code>{}</code>\n<b>🔘 Succefully forwarded file count:</b> <code>{}</code> files</code>\n<b>🔘 Skipped messages:</b> <code>{}</code>\n<b>🔘 Filtered messages:</b> <code>{}</code>\n<b>🔘 Status:</b> <code>{}</code>\n<b>🔘 percentage:</b> <code>{}</code> %'
buttons = [[
          InlineKeyboardButton('📜 Support Group', url='https://t.me/venombotsupport')
          ],[
          InlineKeyboardButton('📡 Update Channel', url='https://t.me/venombotupdates')
          ]]

@Client.on_callback_query(filters.regex(r'^start_public'))
async def pub_(bot, message):
    user = message.from_user.id
    temp.CANCEL[user] = True
    forward_id = message.data.split("_")[2]
    if temp.lock.get(user) and str(temp.lock.get(user))=="True":
        return await message.answer("__please wait until previous task complete__", show_alert=True)
    details = temp.FORWARD.get(forward_id)
    if not details:
        await message.answer("your are clicking on my old button", show_alert=True)
        return await message.message.delete()
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
      k = await client.send_message(details['TO'], "Testing")
      await k.delete()
    except:
      return await message.answer("Please Make Your Bot Admin In Target Channel With Full Permissions", show_alert=True)
    await message.message.delete()
    test = await client.send_message(user, text="Forwarding started")
    if test:
        m = await message.message.reply_text("<i>processing</i>")
        total_files=0
        temp.lock[user] = locked = True
        if locked:
            try:
              MSG = []
              pling=0
              fetched = 0
              deleted = 0 
              filtered = 0
              skip = int(details['SKIP'])
              total = int(details['LIMIT'])
              reply_markup = [[InlineKeyboardButton('Cancel🚫', 'terminate_frwd')]]
              async for message in client.iter_messages(chat_id=details['FROM'], limit=total, offset=skip):
                    if temp.CANCEL.get(user)==True:
                       temp.CANCEL[user] = False
                       await edit(m, TEXT.format('\n♥️ FORWARDING CANCELLED\n', fetched, deleted, total_files, skip, filtered, "cancelled", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), buttons)
                       await client.send_message(user, text="Forwarding cancelled")
                       await client.stop()
                       return 
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
                          await forward(client, details, MSG)
                        except FloodWait as e:
                          await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, f"Sleeping {e.x} s", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                          await asyncio.sleep(e.x)
                          await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, "Forwarding", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                          await forward(client, details, MSG)
                        total_files+=100
                      else:
                        for msgs in MSG:
                          if temp.CANCEL.get(user)==True:
                            temp.CANCEL[user] = False
                            await edit(m, TEXT.format('\n♥️ FORWARDING CANCELLED\n', fetched, deleted, total_files, skip, filtered, "cancelled", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), buttons)
                            await client.send_message(user, text="Forwarding cancelled")
                            await client.stop()
                            return
                          pling += 1
                          if pling % 10 == 0: 
                            await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, "Forwarding", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                          try:
                            await copy(client, details, msgs)
                            await asyncio.sleep(1.7)
                            total_files += 1
                          except FloodWait as e:
                            await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, f"Sleeping {e.x} s", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                            await asyncio.sleep(e.x)
                            await edit(m, TEXT.format('', fetched, deleted, total_files, skip, filtered, "Forwarding", "{:.0f}".format(float(deleted + total_files + filtered + skip)*100/float(total))), reply_markup)
                            await copy(client, details, msgs)
                            total_files += 1
                            await asyncio.sleep(1.7)
                          except Exception as e:
                            print(e)
                            pass
                      MSG = []
            except Exception as e:
                print(e) 
                temp.lock[user] = False
                await m.edit_text(f'Error: {e}')
                try:
                  await client.stop()
                except:
                  pass
            else:
                temp.lock[user] = False
                try:
                  await client.stop()
                except:
                  pass
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

def filename(msg, file_name=None):
   if msg.video:
     file_name = msg.video.file_name
   elif msg.document:
     file_name = msg.document.file_name
   elif msg.audio:
     file_name = msg.audio.file_name
   return file_name
                            
@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def terminate_frwding(bot, m):
    user_id = m.from_user.id 
    temp.lock[user_id] = False
    temp.CANCEL[user_id] = True 
    
@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def close(bot, update):
    await update.answer()
    await update.message.delete()
