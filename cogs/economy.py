import discord
from discord.ext import commands
from datetime import datetime, timedelta
from config import DAILY_COINS, shop_items
from database import get_db_connection

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    shop_group = discord.SlashCommandGroup("shop", "Commands related to the item shop.")


    @shop_group.command(name="view", description="View the item shop.")
    async def shop_view(self, ctx):
        embed = discord.Embed(title="🛒 Whisker Shop", color=discord.Color.purple())
        embed.description = "Buy exclusive items with your coins!"
        
        for item in shop_items:
            embed.add_field(name=f"{item['name']} [{item['tag']}]", value=f"💰 {item['cost']} coins\n{item['description']}", inline=False)
        
        embed.set_footer(text="Use `/shop buy [item]` to buy items!")

        await ctx.response.send_message(embed=embed)


    @shop_group.command(name="buy", description="Buy an item.")
    async def shop_buy(self, ctx, item_name: str):
        user_id = ctx.user.id
        guild_id = ctx.guild.id
        
        item_key = item_name.lower()
        item = next((x for x in shop_items if x["tag"] == item_key), None)

        if item is None:
            return await ctx.response.send_message("❌ Item not found in the shop. Use `/shop` to view the list.", ephemeral=True)
        
        cost = item["cost"]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT coins FROM economy WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))

        row = cursor.fetchone()

        if not row or row[0] < cost:
            conn.close()

            return await ctx.response.send_message(f"❌ You don't have enough coins! Cost: {cost}", ephemeral=True)
        
        new_coins = row[0] - cost

        cursor.execute("UPDATE economy SET coins = ? WHERE user_id = ? AND guild_id = ?", (new_coins, user_id, guild_id))
        cursor.execute("INSERT OR REPLACE INTO inventory (user_id, guild_id, item) VALUES (?, ?, ?)", (user_id, guild_id, item_key))
        
        conn.commit()
        conn.close()
        
        await ctx.response.send_message(f"✅ You bought **{item_name}**! 🎉")


    @commands.slash_command(name="daily", description="Claim your daily coins.")
    async def daily(self, ctx):
        user_id = ctx.user.id
        guild_id = ctx.guild.id
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT last_daily_claim FROM economy WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        row = cursor.fetchone()
        
        if row and row[0]:
            last_daily = datetime.fromisoformat(row[0])

            if datetime.now() - last_daily < timedelta(hours=24):
                time_left = (last_daily + timedelta(hours=24)) - datetime.now()
                
                return await ctx.response.send_message(f"⏰ You've already claimed your daily coins today! Come back in {time_left} for the next reward.", ephemeral=True)
        
        cursor.execute("SELECT coins FROM economy WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        row = cursor.fetchone()
        current_coins = row[0] if row else 0
        new_coins = current_coins + DAILY_COINS
        
        cursor.execute("UPDATE economy SET coins = ?, last_daily_claim = ? WHERE user_id = ? AND guild_id = ?",
            (new_coins, datetime.now().isoformat(), user_id, guild_id))
        
        if not row:
            cursor.execute("INSERT INTO economy (user_id, guild_id, coins, last_daily_claim) VALUES (?, ?, ?, ?)",
                (user_id, guild_id, DAILY_COINS, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        await ctx.response.send_message(f"🎉 **{ctx.user.name}**, you received **{DAILY_COINS} coins**!")


    @commands.slash_command(name="balance", description="Check your coin balance.")
    async def balance(self, ctx):
        user_id = ctx.user.id
        guild_id = ctx.guild.id
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT coins FROM economy WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
        row = cursor.fetchone()
        conn.close()
        
        coins = row[0] if row else 0

        embed = discord.Embed(
            title=f"💰 **{ctx.user.name}**'s Balance",
            color=discord.Color.gold()
        )

        embed.add_field(name="Coins", value=f"🪙 **{coins}**", inline=False)

        await ctx.response.send_message(embed=embed)


    @commands.slash_command(name="pay", description="Transfer coins to another user.")
    async def pay(self, ctx, amount: int, user: discord.User):
        if amount <= 0:
            return await ctx.response.send_message("❌ Invalid amount.", ephemeral=True)
        
        sender_id = ctx.user.id
        receiver_id = user.id
        guild_id = ctx.guild.id
        
        if sender_id == receiver_id:
            return await ctx.response.send_message("❌ You cannot transfer to yourself.", ephemeral=True)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT coins FROM economy WHERE user_id = ? AND guild_id = ?", (sender_id, guild_id))
        sender_row = cursor.fetchone()
        
        if not sender_row or sender_row[0] < amount:
            conn.close()
            return await ctx.response.send_message(f"❌ You don't have enough coins! (Balance: {sender_row[0] if sender_row else 0})", ephemeral=True)
        
        cursor.execute("SELECT coins FROM economy WHERE user_id = ? AND guild_id = ?", (receiver_id, guild_id))
        receiver_row = cursor.fetchone()
        receiver_coins = receiver_row[0] if receiver_row else 0
        
        new_sender = sender_row[0] - amount
        new_receiver = receiver_coins + amount
        
        if sender_row:
            cursor.execute("UPDATE economy SET coins = ? WHERE user_id = ? AND guild_id = ?", (new_sender, sender_id, guild_id))
        else:
            cursor.execute("INSERT INTO economy (user_id, guild_id, coins) VALUES (?, ?, ?)", (sender_id, guild_id, new_sender))
            
        if receiver_row:
            cursor.execute("UPDATE economy SET coins = ? WHERE user_id = ? AND guild_id = ?", (new_receiver, receiver_id, guild_id))
        else:
            cursor.execute("INSERT INTO economy (user_id, guild_id, coins) VALUES (?, ?, ?)", (receiver_id, guild_id, new_receiver))
            
        conn.commit()
        conn.close()
        
        await ctx.response.send_message(f"✅ Transfer complete! You sent **{amount} coins** to **{user.name}**.", ephemeral=True)


    @commands.slash_command(name="inventory", description="View your items.")
    async def inventory(self, ctx):
        user_id = ctx.user.id
        guild_id = ctx.guild.id
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT item FROM inventory WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))

        items = cursor.fetchall()

        conn.close()
        
        if not items:
            return await ctx.response.send_message("📦 You don't have any items in your inventory yet! Buy some at `/shop`.", ephemeral=True)
        
        embed = discord.Embed(title="🎒 Your Inventory", color=discord.Color.blue())
        item_list = "\n".join([f"• {row[0]}" for row in items])

        embed.add_field(name="Items", value=item_list, inline=False)

        await ctx.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(Economy(bot))