import os
import logging

class Config:
    API_ID = int(os.environ.get("API_ID", 12345))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "") 
    BOT_SESSION = os.environ.get("BOT_SESSION", "bot") 
    DATABASE_URI = os.environ.get("DATABASE", "")
    DATABASE_NAME = os.environ.get("DATABASE_NAME", "forward-bot")
    
class temp(object): 
    lock = {}
    CANCEL = {}
    CONFIGS = {}
    FORWARD = {}
    forwardings = 0
    BANNED_USERS = []
    
def LOGGER(name: str) -> logging.Logger:
    return logging.getLogger(name)
