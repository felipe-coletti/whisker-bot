from discord.ext import commands
import os
import asyncio
from config import DISCORD_TOKEN, INTENTS, PREFIX
from database import init_db

init_db()

bot = commands.Bot(
    command_prefix=PREFIX, 
    intents=INTENTS, 
    help_command=None,
    case_insensitive=True
)


def load_cogs():
    cogs_path = 'cogs'

    for filename in os.listdir(cogs_path):
        if filename.endswith('.py') and filename != '__init__.py':
            ext_name = filename[:-3]
            full_module_name = f'cogs.{ext_name}'

            try:
                print(f"Attempting to load: {full_module_name}...")
                bot.load_extension(full_module_name)
                print(f'✅ Loaded: {full_module_name}')
            except Exception as e:
                print(f'❌ Error loading {full_module_name}: {e}')


async def main():
    if not DISCORD_TOKEN:
        print("❌ Error: Token not found. Create a .env file with DISCORD_TOKEN=your_token")
        return
    
    load_cogs()
    
    await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())