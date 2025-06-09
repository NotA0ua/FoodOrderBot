from dotenv import load_dotenv
from os import getenv
from json import loads

load_dotenv()

BOT_TOKEN = getenv("BOT_TOKEN")
DATABASE_URL = getenv("DATABASE_URL")
DEFAULT_ADMIN_IDS = loads(getenv("DEFAULT_ADMIN_IDS"))
