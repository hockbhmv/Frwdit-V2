import os
from config import Config

class Translation(object):
  START_TXT = """<b>Hi {}</b>
<i>I'm a Advanced Auto Forward Bot
I can forward all message from one channel to another channel</i>
**Click help button to know More about me**"""
  HELP_TXT = """<b><u>🔆 HELP</b></u>

<u>**📚 Available commands:**</u>
**>** __/start - check I'm alive__ 
**>** __/forward - forward messages__
**>** __/settings - configure your settings__
**>** __/reset - reset your settings__

<b><u>⚠️ Before Forwarding:</b></u>
**•** __add a bot__
**•** __add atleast one to channel__ `(your bot must be admin in there)`
**•** __You can add above mentioned by using /settings__
**•** __if the **From Channel** is private your bot must need admin permission in there also__
**•** __Then use /forward to forward messages__

<b><u>💢 Features:</b></u>
**-** __Forward message from public channel to your channel without admin permission. if the channel is private need admin permission__
**-** __custom caption__
**-** __support restricted channels__
**-** __skip duplicate files__`(comming soon)`
**-** __filter type of messages__

"""
  ABOUT_TXT = """
╔════❰ ғᴏʀᴡᴀʀᴅ ʙᴏᴛ ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼📃ʙᴏᴛ : [ғᴏʀᴡᴀʀᴅ ʙᴏᴛ](https://t.me/mdforwardbot)
║┣⪼👦ᴄʀᴇᴀᴛᴏʀ : [ᴍᴅᴀᴅᴍɪɴ](https://t.me/mdadmin2)
║┣⪼📡ʜᴏsᴛᴇᴅ ᴏɴ : ʜᴇʀᴏᴋᴜ
║┣⪼🗣️ʟᴀɴɢᴜᴀɢᴇ : ᴘʏᴛʜᴏɴ3
║┣⪼📚ʟɪʙʀᴀʀʏ : ᴘʏʀᴏɢʀᴀᴍ ᴀsʏɴᴄɪᴏ 2.0.0 
║┣⪼🗒️ᴠᴇʀsɪᴏɴ : 0.0.1
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪
"""
  STATUS_TXT = """
╔════❰ ʙᴏᴛ sᴛᴀᴛᴜs  ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼**👱 ᴛᴏᴛᴀʟ ᴜsᴇʀs:** `{}`
║┃
║┣⪼**🤖 ᴛᴏᴛᴀʟ ʙᴏᴛ:** `{}`
║┃
║┣⪼**🔃 ғᴏʀᴡᴀʀᴅɪɴɢs:** `{}`
║┃
║╰━━━━━━━━━━━━━━━➣
╚══════════════════❍⊱❁۪۪
"""
  FROM_MSG = "<b><u>SET FROM CHANNEL</b></u>\n\n<b>Forward the last message of From channel OR Send the last message link of From channel.</b>\n<code>Note: Your bot must be admin in From channel if the channel is private</code>\n/cancel <code>- Cancel this process</code>"
  TO_MSG = "<b><u>CHOOSE TO CHANNEL</b></u>\n\n<b>Choose your **To channel** from the given list.</b>\n<b>`Note: </b>`[{}](t.me/{}) `must be admin in there before forwarding`\n/cancel <code>- Cancel this process</code>"
  SKIP_MSG = "<b><u>SET MESSAGE SKIPING NUMBER</b></u>\n<b>Skip the message as much as you enter the number and the rest of the message will be forwarded\nDefault Skip Number =</b> <code>0</code>\n<code>eg: You enter 0 = 0 file skiped\n You enter 5 = 5 file skiped</code>\n/cancel <code>- Cancel this process</code>"
  CANCEL = "<b>Process Cancelled Succefully !</b>"
  USERNAME = "<b>Send Username with @</b>\n<code>eg: @Username</code>\n<b>Enter /run Again</b>"
  INVALID_CHANNELID = "<b>Send channel id with -100</b>\n<code>eg: -100xxxxxxxxxx</code>\n<b>Enter /run Again</b>"
  BOT_DETAILS = f"<b><u>📄 BOT DETAILS</b></u>\n\n<b>➣ NAME:</b> <code>{}</code>\n<b>➣ BOT ID:</b> <code>{}</code>\n<b>➣ USERNAME:</b> @{}"
  USER_DETAILS = f"<b><u>📄 USERBOT DETAILS</b></u>\n\n<b>➣ NAME:</b> <code>{}</code>\n<b>➣ USER ID:</b> <code>{}</code>\n<b>➣ USERNAME:</b> @{}"  
         
  TEXT = """
╔════❰ ғᴏʀᴡᴀʀᴅ sᴛᴀᴛᴜs  ❱═❍⊱❁۪۪
║╭━━━━━━━━━━━━━━━➣
║┣⪼<b>𖨠 ғᴇᴄʜᴇᴅ ᴍᴇssᴀɢᴇs:</b> <code>{}</code>
║┃
║┣⪼<b>𖨠 sᴜᴄᴄᴇғᴜʟʟʏ ғᴏʀᴡᴀʀᴅᴇᴅ:</b> <code>{}</code>
║┃
║┣⪼<b>𖨠 ᴅᴜᴘʟɪᴄᴀᴛᴇ ᴍᴇssᴀɢᴇs:</b> <code>{}</code>
║┃
║┣⪼<b>𖨠 ᴅᴇʟᴇᴛᴇᴅ ᴍᴇssᴀɢᴇs:</b> <code>{}</code>
║┃
║┣⪼<b>𖨠 sᴋɪᴘᴘᴇᴅ ᴍᴇssᴀɢᴇs:</b> <code>{}</code>
║┃
║┣⪼<b>𖨠 ғɪʟᴛᴇʀᴇᴅ ᴍᴇssᴀɢᴇs:</b> <code>{}</code>
║┃
║┣⪼<b>𖨠 ᴄᴜʀʀᴇɴᴛ sᴛᴀᴛᴜs:</b> <code>{}</code>
║┃
║┣⪼<b>𖨠 ᴘᴇʀᴄᴇɴᴛᴀɢᴇ:</b> <code>{}</code> %
║╰━━━━━━━━━━━━━━━➣ 
╚════❰ {} ❱══❍⊱❁۪۪
"""
  DOUBLE_CHECK = """<b><u>DOUBLE CHECKING ⚠️</b></u>
<code>Before forwarding the messages Click the Yes button only after checking the following</code>

<b>★ YOUR BOT:</b> [{botname}](t.me/{botuname})
<b>★ FROM CHANNEL:</b> `{from_chat}`
<b>★ TO CHANNEL:</b> `{to_chat}`
<b>★ SKIP MESSAGES:</b> `{skip}`

<i>° [{botname}](t.me/{botuname}) must be admin in **To Channel**</i> (`{to_chat}`)
<i>° If the **From Channel** is private your bot must be admin in there also</b></i>

<b>If the above is checked then the yes button can be clicked</b>"""
