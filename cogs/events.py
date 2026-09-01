import discord
from discord.ext import commands
import random
from config import STATUSES

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'✅ Whisker is online as {self.bot.user.name}!')
        print(f'📡 Connected to {len(self.bot.guilds)} servers.')
        
        status = random.choice(STATUSES)

        await self.bot.change_presence(
            activity=discord.CustomActivity(name=status)
        )


    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = member.guild.system_channel
        if channel:
            welcome_message = (
                f"👋 Welcome, **{member.name}**!\n"
                f"**Whisker** is happy to have you here. 🐾\n"
                f"Use `/help` to see what I can do!"
            )
            await channel.send(welcome_message)


def setup(bot):
    bot.add_cog(Events(bot))