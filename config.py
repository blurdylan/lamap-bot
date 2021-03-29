import json
import sys
import os

from dotenv import load_dotenv
from pathlib import Path

local_env_path = Path('.') / '.env.local'
prod_env_path = Path('.') / '.env.prod'

# read the config.json file
with open("config.json",
          "r") as f:
    config = json.loads(f.read())

WORKERS = config.get("WORKERS", 32)
ADMIN_LIST = config.get("ADMIN_LIST", None)
SUPERMOD_LIST = config.get(
    "SUPERMOD_LIST", [223627873, 1077515995, 1227290946])
OPEN_LOBBY = config.get("OPEN_LOBBY", True)
DEFAULT_GAMEMODE = config.get("DEFAULT_GAMEMODE", "classic")
WAITING_TIME = config.get("WAITING_TIME", 100)
MIN_PLAYERS = config.get("MIN_PLAYERS", 2)
MAX_PLAYERS = config.get("MAX_PLAYERS", 6)
TIME_TO_START = config.get("TIME_TO_START", 30)
TIME_TO_PLAY = config.get("TIME_TO_PLAY", 60)
HEROKU_URL = ""
HEROKU_PORT = int(os.environ.get('PORT', 5000))

if sys.argv[1] == "prod":
    load_dotenv(prod_env_path)
    TOKEN = os.getenv("TOKEN")
    DB_URL = os.getenv("DATABASE_URL")
    HEROKU_URL = os.getenv("HEROKU_URL")
    print("prod", TOKEN)
else:
    load_dotenv(local_env_path)
    TOKEN = os.getenv("TOKEN")
    DB_URL = os.getenv("DATABASE_URL")
    print("local", TOKEN)
