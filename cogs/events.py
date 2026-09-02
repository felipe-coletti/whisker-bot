import discord
from discord.ext import commands, tasks
import random
from config import STATUSES

class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print(f'✅ Whisker is online as {self.bot.user.name}!')
        print(f'📡 Connected to {len(self.bot.guilds)} servers.')

        self.update_status.start()


    @tasks.loop(seconds=60)
    async def update_status(self):
        status_text = random.choice(STATUSES)

        await self.bot.change_presence(
            activity=discord.CustomActivity(name=status_text)
        )


    @update_status.before_loop
    async def before_update_status(self):
        await self.bot.wait_until_ready()


    @commands.Cog.listener()
    async def on_member_join(self, member):
        if member.bot:
            return
        
        channel = member.guild.system_channel

        if not channel:
            return
        
        welcome_message = f"👋 Welcome, **{member.name}**!"

        await channel.send(welcome_message)


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return
        
        channel = member.guild.system_channel

        if not channel:
            return
        
        goodbye_message = f"👋 Bye, **{member.name}**! See you soon."

        await channel.send(goodbye_message)


def setup(bot):
    bot.add_cog(Events(bot))