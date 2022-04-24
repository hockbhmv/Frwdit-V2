import os
from config import Config

class Translation(object):
  START_TXT = """<b>Hai {}!!</b>
<i>I'm Simple Auto file Forward Bot V2
This Bot forward all files to One Public channel to Your Personal channel
More details /help</i>"""
  HELP_TXT = """<b>Follow These Steps!!
• User Join From channel Must(No need Admin permission)
• Then give admin permission in your personal telegram channel
• Then use /run command in your bot</b>

<b><u>Available Command</b></u>

* /start - <i>Bot Alive</i>
* /help - <i>more help</i>
* /run - <i>start forward</i>
* /about - <i>About Me</i>
* /restart - <i>Server Restart</i>"""
  ABOUT_TXT = """<b><u>My Info</b></u>

<b>Name :</b> <code>Auto Forward Bot</code>
<b>Credit :</b> <code>Dark Angel</code>
<b>Language :</b> <code>Python3</code>
<b>Lybrary :</b> <code>Pyrogram v1.2.9</code>
<b>Server :</b> <code>Heroku</code>
<b>Build :</b> <code>V2.0</code>"""
  FROM_MSG = "<b><u>SET FROM CHANNEL</b></u>\n\n<b>Forward the last message of From channel OR Send the last message link of From channel.</b>\n<code>Note: Your bot must be admin in From channel if the channel is private</code>\n/cancel <code>- Cancel this process</code>"
  TO_MSG = "<b><u>CHOOSE TO CHANNEL</b></u>\n\n<b>Choose your **To channel** from the given list.</b>\n<b>`Note: </b>`[{}](t.me/{}) `must be admin in there before forwarding`\n/cancel <code>- Cancel this process</code>"
  SKIP_MSG = "<b><u>SET MESSAGE SKIPING NUMBER</b></u>\n<b>Skip the message as much as you enter the number and the rest of the message will be forwarded\nDefault Skip Number =</b> <code>0</code>\n<code>eg: You enter 0 = 0 file skiped\n You enter 5 = 5 file skiped</code>\n/cancel <code>- Cancel this process</code>"
  CANCEL = "<b>Process Cancelled Succefully !</b>"
  USERNAME = "<b>Send Username with @</b>\n<code>eg: @Username</code>\n<b>Enter /run Again</b>"
  INVALID_CHANNELID = "<b>Send channel id with -100</b>\n<code>eg: -100xxxxxxxxxx</code>\n<b>Enter /run Again</b>"
  TEXT = """<b><u>FORWARD STATUS</b></u>
{}
<b>🔲 Feched messages:</b> <code>{}</code>\n
<b>🔲 Succefully forwarded:</b> <code>{}</code>\n
<b>🔲 Deleted messages:</b> <code>{}</code>\n
<b>🔲 Skipped messages:</b> <code>{}</code>\n
<b>🔲 Filtered messages:</b> <code>{}</code>\n
<b>🔲 Current status:</b> <code>{}</code>\n
<b>🔲 Percentage:</b> <code>{}</code> %"""
  DOUBLE_CHECK = """<b><u>DOUBLE CHECKING ⚠️</b></u>
<code>Before forwarding the messages Click the Yes button only after checking the following</code>

<b>★ YOUR BOT:</b> [{botname}](t.me/{botuname})
<b>★ FROM CHANNEL:</b> `{from_chat}`
<b>★ TO CHANNEL:</b> `{to_chat}`
<b>★ SKIP MESSAGES:</b> `{skip}`

<i>° [{botname}](t.me/{botuname}) must be admin in **To Channel**</i> (`{to_chat}`)
<i>° If the **From Channel** is private your bot must be admin in there also</b></i>

<b>If the above is checked then the yes button can be clicked</b>"""
