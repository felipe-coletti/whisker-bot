import discord
from discord.ext import commands
from database import add_xp, get_top_users, get_user_xp

class Levels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name="level", description="Check your activity level.")
    async def level(self, ctx):
        user_id = ctx.user.id
        xp = get_user_xp(user_id)
        level = xp // 10

        await ctx.response.send_message(f"📊 **{ctx.user.name}**, you are **Level {level}** (XP: {xp}) in Whisker! Keep participating! 🐾")


    @commands.slash_command(name="rank", description="List the top 10 most active users.")
    async def rank(self, ctx):
        top_10 = get_top_users(10)
        
        if not top_10:
            await ctx.response.send_message("📭 No XP data registered yet. Be the first to participate!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🏆 Top 10 Most Active",
            description="Users with the most XP in the server!",
            color=discord.Color.gold()
        )
        
        leaderboard_text = ""
        first_user_id = None
        
        for index, (user_id, xp) in enumerate(top_10, start=1):
            member = self.bot.get_user(user_id)
            if member:
                user_name = member.name
                avatar = member.display_avatar.url
            else:
                user_name = f"User {user_id}"
                avatar = None
            
            level = xp // 10
            leaderboard_text += f"**{index}** {user_name} - Level {level} ({xp} XP)\n"
            
            if index == 1:
                first_user_id = user_id

        embed.add_field(name="📜 Leaderboard", value=leaderboard_text, inline=False)
        
        if first_user_id:
            member = self.bot.get_user(first_user_id)

            if member:
                embed.set_thumbnail(url=member.display_avatar.url)
            else:
                try:
                    member = await self.bot.fetch_user(first_user_id)
                    embed.set_thumbnail(url=member.display_avatar.url)
                except:
                    pass

        await ctx.response.send_message(embed=embed)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        add_xp(message.author.id, 1)


def setup(bot):
    bot.add_cog(Levels(bot))