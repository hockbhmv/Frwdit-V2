import os
import sys
import asyncio 
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message 
from pyrogram.errors.exceptions.bad_request_400 import AccessTokenExpired, AccessTokenInvalid
from pyrogram.errors import FloodWait, MessageNotModified
from config import Config
from translation import Translation

BOT_NO = 0
FILTER = Config.FILTER_TYPE
IS_CANCELLED = False
block = {}
lock = asyncio.Lock()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
TEXT = '<b><u>FORWARD STATUS</b></u>\n\n<b>🔘 Feched messages count:</b> <code>{}</code>\n<b>🔘 Deleted messages:</b> <code>{}</code>\n<b>🔘 Succefully forwarded file count:</b> <code>{}</code> files</code>\n<b>🔘 Skipped messages:</b> <code>{}</code>\n<b>🔘 Status:</b> <code>{}</code>'

@Client.on_callback_query(filters.regex(r'^start_public$'))
async def pub_(bot, message):
    global files_count, IS_CANCELLED, BOT_NO
    await message.answer()
    user = message.from_user.id
    await message.message.delete()
    from .test import get_configs, update_configs
    from plugins.public import FROM, TO, SKIP, LIMIT 
    if block.get(user) and str(block.get(user))=="True":
        return await message.message.reply_text("__please wait until previous task complete__", parse_mode="md")
    configs = await get_configs(user)
    session_name = configs.get('session_name')
    if session_name is None:
       session_name = message.from_user.first_name
       await update_configs(user, 'session_name', session_name)
    try:
      client = Client(f"{session_name}-forward-bot", Config.API_ID, Config.API_HASH, bot_token = configs.get('bot_token'))
      await client.start()
      BOT_NO+=1
    except (AccessTokenExpired, AccessTokenInvalid):
        return await message.message.reply_text("The given bot token is invalid")
    except Exception as e:
        return await message.message.reply_text(f"Bot Error:- {e}")
    await client.send_message(user, text="Forwarding started")
    async with lock:
        m = await message.message.reply_text("<i>processing</i>")
        total_files=0
        block[user] = locked = True
        if locked:
            try:
              MSG = []
              pling=0
              fetched = 0
              deleted = 0
              skip = int(SKIP)
              reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Cancel🚫', 'terminate_frwd')]])
              async for last_msg in bot.USER.iter_history(FROM, limit=1):
                limit = last_msg.message_id
              async for message in client.iter_messages(chat_id=FROM, limit=int(limit), offset=skip):
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
                       await edit(m, TEXT.format(fetched, deleted, total_files, skip, "Fetching"),reply_markup)
                    MSG.append({"msg_id": message.message_id, "file_name": file_name})
                    fetched+=1 
                    if len(MSG) >= 200:
                      for msgs in MSG:
                        pling += 1
                        if pling % 10 == 0: 
                           await edit(m, TEXT.format(fetched, deleted, total_files, skip, "Forwarding"),reply_markup)
                        try:
                          await client.copy_message(
                            chat_id=TO,
                            from_chat_id=FROM,
                            parse_mode="md",       
                            caption=Translation.CAPTION.format(msgs.get("file_name")),
                            message_id= msgs.get("msg_id")
                          )
                          total_files += 1
                          await asyncio.sleep(1.7)
                        except FloodWait as e:
                          await edit(m, TEXT.format(fetched, deleted, total_files, skip, f"Sleeping {e.x} s"),reply_markup)
                          await asyncio.sleep(e.x)
                          await edit(m, TEXT.format(fetched, deleted, total_files, skip, "Forwarding"),reply_markup)
                          await client.copy_message(
                            chat_id=TO,
                            from_chat_id=FROM,
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
                block[user] = False
                await m.edit_text(f'Error: {e}')
                try:
                  await client.stop()
                except:
                  pass
            else:
                block[user] = False
                try:
                  await client.stop()
                except:
                  pass
                buttons = [[
                    InlineKeyboardButton('📜 Support Group', url='https://t.me/DxHelpDesk')
                    ],[
                    InlineKeyboardButton('📡 Update Channel', url='https://t.me/DX_Botz')
                ]]
                reply_markup = InlineKeyboardMarkup(buttons)
                await m.edit_text(
                    text=f"<u><i>Successfully Forwarded</i></u>\n\n<b>Total Forwarded Files:-</b> <code>{total_files}</code> <b>Files</b>\n<b>Thanks For Using Me❤️</b>",
                    reply_markup=reply_markup,
                    parse_mode="html")
      
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
