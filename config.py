import discord
from dotenv import load_dotenv
import os

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

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
    "Peaw!",
    "Pow!"
]