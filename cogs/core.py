import discord
from discord.ext import commands
import random

class Core(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name="whisper", description="Tries to call 'Whisper'.")
    async def whisper(self, ctx):
        responses = [
            "I don't know where 'Whisper' is, but **I** am here! 🐱✨",
            "Wait... did you mean *Whisker*? Because 'Whisper' must be sleeping in another server. 😴",
            "Uh, where's 'Whisper'? Ah, he doesn't exist! I'm **Whisker**, your only auto-friend! 🤖",
            "'Whisper'? Never heard of him. But **Whisker** (me) is ready to help! 🐾",
            "Oops! You typed it wrong? The name is **Whisker**. 'Whisper' is just a myth. 👻"
        ]

        await ctx.response.send_message(random.choice(responses), ephemeral=False)


    @commands.slash_command(name="help", description="List of available commands.")
    async def help_cmd(self, ctx):
        embed = discord.Embed(
            title="🐾 Whisker Commands", 
            description="Here is what I can do for you:", 
            color=discord.Color.blue()
        )
        embed.add_field(name="/whisper", value="Try to confuse me. Go ahead!", inline=False)
        embed.add_field(name="/greeting", value="A friendly greeting.", inline=False)
        embed.add_field(name="/xp view", value="Check your activity level.", inline=False)
        embed.add_field(name="/xp rank", value="See the top 10 XP leaderboard.", inline=False)
        embed.add_field(name="/xp leaderboard", value="Alias for /xp rank.", inline=False)
        embed.add_field(name="/xp transfer [amount] [user]", value="Transfer XP to another user.", inline=False)
        embed.add_field(name="/balance", value="Check your coin balance.", inline=False)
        embed.add_field(name="/pay [amount] [user]", value="Transfer coins to another user.", inline=False)
        embed.add_field(name="/daily", value="Claim your daily coins.", inline=False)
        embed.add_field(name="/shop view", value="View the shop and available items.", inline=False)
        embed.add_field(name="/shop buy [item_name]", value="Purchase an item from the shop.", inline=False)
        embed.add_field(name="/shop sell [item_name]", value="Sell an item from your inventory.", inline=False)
        embed.add_field(name="/inventory", value="Check your owned items.", inline=False)
        embed.add_field(name="/use [item_name]", value="Use an item from your inventory.", inline=False)

        if ctx.user.id == self.bot.owner_id:
            embed.add_field(name="/reload [cog_name]", value="Reload a cog (owner only).", inline=False)
            
        await ctx.response.send_message(embed=embed, ephemeral=True)


    @commands.slash_command(name="greeting", description="A friendly greeting.")
    async def greeting(self, ctx):
        await ctx.response.send_message(f"Hello, **{ctx.user.name}**! Whisker sends greetings! 🐱💬")


def setup(bot):
    bot.add_cog(Core(bot))