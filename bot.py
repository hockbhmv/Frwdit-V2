from pyropatch import listen
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from config import Config
from config import LOGGER

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
        
    async def stop(self, *args):
        msg = f"@{self.username} stopped. Bye."
        await super().stop()
        print(msg)
