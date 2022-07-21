import pyromod.listen
from database import db
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config, LOGGER 

class Bot(Client):
    
    def __init__(self):
        super().__init__(
            Config.BOT_SESSION,
            api_hash=Config.API_HASH,
            api_id=Config.API_ID,
            plugins={
                "root": "plugins"
            },
            workers=30,
            bot_token=Config.BOT_TOKEN
        )
        self.LOGGER = LOGGER

    async def start(self):
        await super().start()
        me = await self.get_me()
        print(f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on @{me.username}.")
        self.id = me.id
        self.username = me.username
        self.first_name = me.first_name
        self.set_parse_mode("combined")
        text = f"**๏[-ิ_•ิ]๏ bot restarted !**}"
        success = failed = 0
        users = await get_all_frwd()
        async for user in users:
           chat_id = user['user_id']
           try:
              await self.send_message(chat_id, text)
              success += 1
           except FloodAwait as e:
              await self.send_message(chat_id, text)
              success += 1
           except Exception:
              failed += 1
        if (success + failed) != 0:
           await db.rmv_frwd(all=True)
           print(f"Restart message status"
                 f"success: {success}"
                 f"failed: {failed}")

    async def stop(self, *args):
        msg = f"@{self.username} stopped. Bye."
        await super().stop()
        print(msg)
