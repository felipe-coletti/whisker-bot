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

DAILY_COINS = 100
LEVEL_COINS = 500

shop_items = [
    {
        "name": "Rat",
        "emoji": "🐀",
        "description": "A cute little rat",
        "tag": "rat",
        "cost": 50,
        "type": "pet",
        "effects": {
            "daily": 5,
        },
    },
    {
        "name": "Coin Booster",
        "emoji": "🪙",
        "description": "Double your coins for 1 hour",
        "tag": "coin_booster",
        "cost": 500,
        "type": "booster",
        "duration": 3600,
        "effects": {
            "coins": 2,
        },
    },
    {
        "name": "Mega Coin Booster",
        "emoji": "🪙",
        "description": "Triple your coins for 2 hours",
        "tag": "mega_coin_booster",
        "cost": 1500,
        "type": "booster",
        "duration": 7200,
        "effects": {
            "coins": 3,
        },
    },
    {
        "name": "XP Booster",
        "emoji": "✨",
        "description": "Double your XP for 1 hour",
        "tag": "xp_booster",
        "cost": 500,
        "type": "booster",
        "duration": 3600,
        "effects": {
            "xp": 2,
        },
    },
    {
        "name": "Mega XP Booster",
        "emoji": "✨",
        "description": "Triple your XP for 2 hours",
        "tag": "mega_xp_booster",
        "cost": 1500,
        "type": "booster",
        "duration": 7200,
        "effects": {
            "xp": 3,
        },
    },
    {
        "name": "Ultimate Booster",
        "emoji": "💎",
        "description": "Triple your coins and XP for 24 hours",
        "tag": "ultimate_booster",
        "cost": 5000,
        "type": "booster",
        "duration": 86400,
        "effects": {
            "coins": 3,
            "xp": 3,
        },
    },
]