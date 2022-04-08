import os
import sys
import asyncio 
import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from pyrogram.errors import FloodWait
from config import Config
from translation import Translation

FILTER = Config.FILTER_TYPE
IS_CANCELLED = False
lock = {}
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@Client.on_callback_query(filters.regex(r'^start_public$'))
async def pub_(bot, message):
    global files_count, IS_CANCELLED
    await message.answer()
    user = message.from_user.id
    await message.message.delete()
    from .test import BOT_TOKEN
    from plugins.public import FROM, TO, SKIP, LIMIT 
    client = Client(":test:", Config.API_ID, Config.API_HASH, bot_token = BOT_TOKEN.get("test"))
    await client.start()
    await client.send_message(user, text="Forwarding started")
    if lock.get(user) and lock.get(user)=="True":
        return await message.message.reply_text("__please wait until previous task complete__")
    else:
        await message.message.reply_text("<i>processing</i>", parse_mode="md")
        total_files=0
        lock[user] = locked = True
        if locked:
            try:
              MSG = []
              pling=0
              fetched = 0
              deleted = 0
              skip = int(SKIP)
              TEXT = '<b><u>FORWARD STATUS</b></u>\n\n<b>🔘 Feched messages count:</b> <code>{}</code>\n<b>🔘 Deleted messages:</b> <code>{}</code>\n<b>🔘 Succefully forwarded file count:</b> <code>{}</code> files</code>\n<b>🔘 Skipped messages:</b> <code>{}</code>\n<b>🔘 Status:</b> <code>{}</code>'
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
                       await m.edit_text(text=TEXT.format(fetched, deleted, total_files, skip, "Fetching messages"), reply_markup=reply_markup)
                    MSG.append({"msg_id": message.message_id, "file_name": file_name})
                    fetched+=1 
                    if len(MSG) >= 200:
                      for msgs in MSG:
                        pling += 1
                        if pling % 10 == 0: 
                           await m.edit_text(text=TEXT.format(fetched, deleted, total_files, skip, "Forwarding"), reply_markup=reply_markup)
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
                          await m.edit_text(text=TEXT.format(fetched, deleted, total_files, skip, f"Sleeping {e.x} s"), reply_markup=reply_markup)
                          await asyncio.sleep(e.x)
                          await m.edit_text(text=TEXT.format(fetched, deleted, total_files, skip, "Forwarding"), reply_markup=reply_markup)
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
                await m.edit_text(f'Error: {e}')
            else:
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
      
@Client.on_callback_query(filters.regex(r'^terminate_frwd$'))
async def terminate_frwding(bot, update):
    global IS_CANCELLED
    IS_CANCELLED = True
    
@Client.on_callback_query(filters.regex(r'^close_btn$'))
async def close(bot, update):
    await update.answer()
    await update.message.delete()
