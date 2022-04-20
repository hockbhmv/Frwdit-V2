import os
import sys
import asyncio 
import logging 
from database import db 
from config import Config
from translation import Translation
from pyrogram import Client, filters 
from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid

FILTER = Config.FILTER_TYPE
IS_CANCELLED = False
lock = {}
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TEXT = '<b><u>FORWARD STATUS</b></u>\n{}\n<b>🔘 Feched messages count:</b> <code>{}</code>\n<b>🔘 Deleted messages:</b> <code>{}</code>\n<b>🔘 Succefully forwarded file count:</b> <code>{}</code> files</code>\n<b>🔘 Skipped messages:</b> <code>{}</code>\n<b>🔘 Status:</b> <code>{}</code>\n<b>🔘 percentage:</b> <code>{}</code> %'

@Client.on_callback_query(filters.regex(r'^start_public$'))
async def pub_(bot, message):
    global files_count, IS_CANCELLED
    await message.answer()
    user = message.from_user.id
    await message.message.delete()
    from plugins.public import FORWARD
    if lock.get(user) and str(lock.get(user))=="True":
        return await message.answer("__please wait until previous task complete__", show_alert=True)
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
              FORWARD = FORWARD.get(user)
              if not FORWARD:
                 return await message.answer("your are clicking on my old button")
              skip = int(FORWARD['SKIP'])
              total = int(FORWARD['LIMIT'])
              reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Cancel🚫', 'terminate_frwd')]])
              async for message in client.iter_messages(chat_id=FORWARD['FROM'], limit=total, offset=skip):
                    if IS_CANCELLED:
                       IS_CANCELLED = False 
                       await client.send_message(user, text="Forwarding cancelled")
                       await client.stop()
                       break
                    if message.empty or message.service:
                       deleted+=1
                       continue 
                    if message.video:
                       file_name = message.video.file_name
                    elif message.document:
                       file_name = message.document.file_name
                    elif message.audio:
                       file_name = message.audio.file_name
                    else:
                       file_name = None 
                    pling += 1
                    if pling %10 == 0: 
                       await edit(m, TEXT.format('', fetched, deleted, total_files, skip, "Fetching", "{:.0f}".format(float(deleted + total_files + skip)*100/float(total))), reply_markup)
                    if not configs['forward_tag']:
                       MSG.append({"msg_id": message.message_id, "file_name": file_name})
                    else:
                       MSG.append(message.message_id)
                    fetched+=1 
                    if len(MSG) >= 200:
                      if configs['forward_tag']:
                         await client.forward_messages(
                             chat_id=FORWARD['TO'],
                             from_chat_id=FORWARD['FROM'],
                             message_ids=MSG 
                         )
                      else:
                        for msgs in MSG:
                          if IS_CANCELLED:
                            IS_CANCELLED = False 
                            await client.send_message(user, text="Forwarding cancelled")
                            await client.stop()
                            break
                          pling += 1
                          if pling % 10 == 0: 
                            await edit(m, TEXT.format('', fetched, deleted, total_files, skip, "Forwarding", "{:.0f}".format(float(deleted + total_files + skip)*100/float(total))), reply_markup)
                          try:
                            await client.copy_message(
                               chat_id=FORWARD['TO'],
                               from_chat_id=FORWARD['FROM'],
                               parse_mode="md",       
                               caption=Translation.CAPTION.format(msgs.get("file_name")),
                               message_id= msgs.get("msg_id")
                            )
                            total_files += 1
                            await asyncio.sleep(1.7)
                          except FloodWait as e:
                            await edit(m, TEXT.format('', fetched, deleted, total_files, skip, f"Sleeping {e.x} s", "{:.0f}".format(float(deleted + total_files + skip)*100/float(total))), reply_markup)
                            await asyncio.sleep(e.x)
                            await edit(m, TEXT.format('', fetched, deleted, total_files, skip, "Forwarding", "{:.0f}".format(float(deleted + total_files + skip)*100/float(total))), reply_markup)
                            await client.copy_message(
                               chat_id=FORWARD['TO'],
                               from_chat_id=FORWARD['FROM'],
                               parse_mode="md",       
                               caption=Translation.CAPTION.format(msgs.get("file_name")),
                               message_id=msgs.get("msg_id")
                            )
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
                await edit(m, TEXT.format('FORWARDING SUCCESSFULLY COMPLETED', fetched, deleted, total_files, skip, "completed", "{:.0f}".format(float(deleted + total_files + skip)*100/float(total))), reply_markup)
                   
async def edit(msg, text, button):
   try:
     await msg.edit_text(text=text, reply_markup=button)
   except MessageNotModified:
     pass 
   return

@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def terminate_frwding(bot, update):
    global IS_CANCELLED
    IS_CANCELLED = True
    
@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def close(bot, update):
    await update.answer()
    await update.message.delete()
