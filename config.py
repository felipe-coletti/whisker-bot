import discord
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DB_NAME = os.getenv("DB_NAME")

PREFIX = "/"
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.members = True
INTENTS.guilds = True
INTENTS.presences = True

STATUSES = [
    "Bam!",
    "Bang!",
    "Blam",
    "Boom!",
    "Ka-Boom!",
    "Kaboom!",
    "Kapow!",
    "Meow",
    "Mwah!",
    "Pew!",
    "Pow!",
    "Rawr!"
]

DAILY_COINS = 500
LEVEL_REWARD = 100

shop_items = [
    {"name": "🐀 Rat", "description": "A cute little rat", "tag": "rat", "cost": 50, "type": "pet"},
    {"name": "Coin Booster", "description": "Double your XP for 1 hour", "tag": "coin_booster", "cost": 500, "type": "booster"},
    {"name": "XP Booster", "description": "Double your coins for 1 hour", "tag": "xp_booster", "cost": 500, "type": "booster"},
    {"name": "Ultimate Booster", "description": "Double your coins and XP for 24 hours", "tag": "ultimate_booster", "cost": 3000, "type": "booster"},
]