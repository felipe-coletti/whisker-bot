import discord
from discord.ext import commands
from config import LEVEL_REWARD
from database import get_user_xp, get_top_users, calculate_level_and_progress, add_xp, add_reward

class XP(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    xp_group = discord.SlashCommandGroup("xp", "XP and leveling commands")


    @xp_group.command(name="view", description="Check your XP level and progress.")
    async def xp_view(self, ctx):
        user_id = ctx.user.id
        guild_id = ctx.guild.id
        xp = get_user_xp(user_id, guild_id)
        
        level, progress, xp_needed = calculate_level_and_progress(xp)
        
        bar_length = 10
        filled = int(bar_length * progress / 100)
        bar = "🟩" * filled + "⬜" * (bar_length - filled)
        
        embed = discord.Embed(
            title=f"📊 **{ctx.user.name}**'s Stats",
            description="Your progress in Whisker:",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Level", value=f"⭐ **{level}**", inline=True)
        embed.add_field(name="Total XP", value=f"💎 **{xp}**", inline=True)
        embed.add_field(name="Next Level", value=f"🚀 **{xp_needed} XP** needed", inline=True)
        
        embed.add_field(name="Progress", value=f"{bar} {progress:.0f}%", inline=False)
        
        embed.set_footer(text="Keep chatting to level up! 🐾")
        
        await ctx.response.send_message(embed=embed)


    @xp_group.command(name="rank", description="Top 10 most active users by XP.")
    async def xp_rank(self, ctx):
        guild_id = ctx.guild.id
        top_10 = get_top_users(guild_id, 10)
        
        if not top_10:
            await ctx.response.send_message("📭 No XP data registered yet in this server. Be the first to participate!", ephemeral=True)
            return

        embed = discord.Embed(
            title="🏆 Top 10 Most Active",
            description=f"Users with the most XP in **{ctx.guild.name}**!",
            color=discord.Color.gold()
        )
        
        leaderboard_text = ""
        first_user_id = None
        
        for index, (user_id, xp) in enumerate(top_10, start=1):
            member = self.bot.get_user(user_id)
            user_name = member.name if member else f"User {user_id}"
            
            level, _, _ = calculate_level_and_progress(xp)
            leaderboard_text += f"**{index}** {user_name} - Level {level} ({xp} XP)\n"
            
            if index == 1:
                first_user_id = user_id

        embed.add_field(name="📜 Leaderboard", value=leaderboard_text, inline=False)
        
        if first_user_id:
            member = self.bot.get_user(first_user_id)
            if member:
                embed.set_thumbnail(url=member.display_avatar.url)

        await ctx.response.send_message(embed=embed)


    @xp_group.command(name="leaderboard", description="Top 10 most active users by XP (alias for rank).")
    async def xp_leaderboard(self, ctx):
        await self.xp_rank(ctx)


    @xp_group.command(name="transfer", description="Transfer XP to another user.")
    async def xp_transfer(self, ctx, amount: int, user: discord.User):
        if amount <= 0:
            return await ctx.response.send_message("❌ Invalid amount.", ephemeral=True)
        
        sender_id = ctx.user.id
        receiver_id = user.id
        guild_id = ctx.guild.id
        
        if sender_id == receiver_id:
            return await ctx.response.send_message("❌ You cannot transfer to yourself.", ephemeral=True)
        
        from database import get_db_connection
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT xp FROM xp WHERE user_id = ? AND guild_id = ?", (sender_id, guild_id))
        sender_row = cursor.fetchone()
        
        if not sender_row or sender_row[0] < amount:
            conn.close()
            return await ctx.response.send_message(f"❌ You don't have enough XP! (Balance: {sender_row[0] if sender_row else 0})", ephemeral=True)
        
        cursor.execute("SELECT xp FROM xp WHERE user_id = ? AND guild_id = ?", (receiver_id, guild_id))
        receiver_row = cursor.fetchone()
        receiver_xp = receiver_row[0] if receiver_row else 0
        
        new_sender = sender_row[0] - amount
        new_receiver = receiver_xp + amount
        
        if sender_row:
            cursor.execute("UPDATE xp SET xp = ? WHERE user_id = ? AND guild_id = ?", (new_sender, sender_id, guild_id))
        else:
            cursor.execute("INSERT INTO xp (user_id, guild_id, xp) VALUES (?, ?, ?)", (sender_id, guild_id, new_sender))
            
        if receiver_row:
            cursor.execute("UPDATE xp SET xp = ? WHERE user_id = ? AND guild_id = ?", (new_receiver, receiver_id, guild_id))
        else:
            cursor.execute("INSERT INTO xp (user_id, guild_id, xp) VALUES (?, ?, ?)", (receiver_id, guild_id, new_receiver))
            
        conn.commit()
        conn.close()
        
        await ctx.response.send_message(f"✅ Transfer complete! You sent **{amount} XP** to **{user.name}**.", ephemeral=True)


    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        
        guild_id = message.guild.id if message.guild else 0
        if guild_id == 0:
            return
        
        user_id = message.author.id
        
        old_xp = get_user_xp(user_id, guild_id)
        
        add_xp(user_id, guild_id, 1)
        
        new_xp = get_user_xp(user_id, guild_id)
        
        old_level, _, _ = calculate_level_and_progress(old_xp)
        new_level, _, _ = calculate_level_and_progress(new_xp)
        
        if new_level > old_level:
            add_reward(user_id, guild_id, LEVEL_REWARD)

            await message.channel.send(f"🎉 **{message.author.name}** leveled up to **Level {new_level}**! Earned **{LEVEL_REWARD} coins**! 💰")


def setup(bot):
    bot.add_cog(XP(bot))