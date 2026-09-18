import discord
from discord.ext import commands
from datetime import datetime, timedelta

from config import DAILY_COINS, shop_items
from database import get_booster_multiplier, get_db_connection, get_equipped_pet


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # =========================
    # SHOP
    # =========================

    shop = discord.SlashCommandGroup("shop", "Shop commands")

    @shop.command(name="view", description="View the shop")
    async def shop_view(self, ctx):
        embed = discord.Embed(
            title="🛒 Shop",
            description="Buy items with your coins.",
            color=discord.Color.gold()
        )

        for item in shop_items:
            embed.add_field(
                name=f'{item["emoji"]} {item["name"]} — {item["cost"]} coins',
                value=f'`{item["tag"]}`\n{item["description"]}',
                inline=False
            )

        await ctx.respond(embed=embed)

    @shop.command(name="buy", description="Buy an item from the shop")
    async def shop_buy(self, ctx, item: str):
        item_data = next(
            (shop_item for shop_item in shop_items if shop_item["tag"] == item),
            None
        )

        if item_data is None:
            await ctx.respond("❌ Item not found.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Make sure the user exists in the economy table.
        cursor.execute(
            """
            INSERT OR IGNORE INTO economy (user_id, guild_id, coins)
            VALUES (?, ?, 0)
            """,
            (ctx.author.id, ctx.guild.id)
        )

        cursor.execute(
            """
            SELECT coins
            FROM economy
            WHERE user_id = ? AND guild_id = ?
            """,
            (ctx.author.id, ctx.guild.id)
        )

        user = cursor.fetchone()

        if user["coins"] < item_data["cost"]:
            conn.close()

            await ctx.respond(
                f'❌ You need {item_data["cost"]} coins to buy '
                f'{item_data["name"]}.'
            )
            return

        # =========================
        # PET
        # =========================

        if item_data["type"] == "pet":
            # A user can own multiple different pets,
            # but cannot own the same pet twice.
            cursor.execute(
                """
                SELECT 1
                FROM pets
                WHERE user_id = ?
                  AND guild_id = ?
                  AND pet = ?
                """,
                (
                    ctx.author.id,
                    ctx.guild.id,
                    item_data["tag"]
                )
            )

            if cursor.fetchone() is not None:
                conn.close()

                await ctx.respond(
                    f'❌ You already own the {item_data["name"]}.'
                )
                return

            # If this is the user's first pet, equip it automatically.
            cursor.execute(
                """
                SELECT COUNT(*)
                FROM pets
                WHERE user_id = ? AND guild_id = ?
                """,
                (ctx.author.id, ctx.guild.id)
            )

            pet_count = cursor.fetchone()[0]
            equipped = 1 if pet_count == 0 else 0

            cursor.execute(
                """
                INSERT INTO pets (
                    user_id,
                    guild_id,
                    pet,
                    equipped
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    ctx.author.id,
                    ctx.guild.id,
                    item_data["tag"],
                    equipped
                )
            )

        # =========================
        # NORMAL ITEM
        # =========================

        else:
            cursor.execute(
                """
                INSERT INTO inventory (
                    user_id,
                    guild_id,
                    item,
                    quantity
                )
                VALUES (?, ?, ?, 1)
                ON CONFLICT(user_id, guild_id, item)
                DO UPDATE SET quantity = quantity + 1
                """,
                (
                    ctx.author.id,
                    ctx.guild.id,
                    item_data["tag"]
                )
            )

        # Remove the coins after the purchase.
        cursor.execute(
            """
            UPDATE economy
            SET coins = coins - ?
            WHERE user_id = ? AND guild_id = ?
            """,
            (
                item_data["cost"],
                ctx.author.id,
                ctx.guild.id
            )
        )

        conn.commit()
        conn.close()

        await ctx.respond(
            f'✅ You bought **{item_data["name"]}** for '
            f'**{item_data["cost"]} coins**!'
        )

    # =========================
    # DAILY
    # =========================

    @discord.slash_command(
        name="daily",
        description="Claim your daily coins"
    )
    async def daily(self, ctx):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT OR IGNORE INTO economy (
                user_id,
                guild_id,
                coins
            )
            VALUES (?, ?, 0)
            """,
            (ctx.author.id, ctx.guild.id)
        )

        cursor.execute(
            """
            SELECT coins, last_daily_claim
            FROM economy
            WHERE user_id = ? AND guild_id = ?
            """,
            (ctx.author.id, ctx.guild.id)
        )

        user = cursor.fetchone()

        now = datetime.now()

        if user["last_daily_claim"]:
            last_claim = datetime.fromisoformat(
                user["last_daily_claim"]
            )

            elapsed = now - last_claim

            if elapsed < timedelta(days=1):
                remaining = timedelta(days=1) - elapsed

                hours = remaining.seconds // 3600
                minutes = (remaining.seconds % 3600) // 60

                conn.close()

                await ctx.respond(
                    f"⏳ You already claimed your daily reward.\n"
                    f"Come back in **{hours}h {minutes}m**."
                )
                return

        pet_bonus = 0

        equipped_pet = get_equipped_pet(
            ctx.author.id,
            ctx.guild.id
        )

        if equipped_pet:
            pet_data = next(
                (
                    shop_item
                    for shop_item in shop_items
                    if shop_item["tag"] == equipped_pet
                ),
                None
            )

            if pet_data:
                pet_bonus = pet_data.get(
                    "effects",
                    {}
                ).get("daily", 0)

        multiplier = get_booster_multiplier(
            ctx.author.id,
            ctx.guild.id,
            "coins"
        )

        reward = (DAILY_COINS + pet_bonus) * multiplier

        cursor.execute(
            """
            UPDATE economy
            SET coins = coins + ?,
                last_daily_claim = ?
            WHERE user_id = ? AND guild_id = ?
            """,
            (
                reward,
                now.isoformat(),
                ctx.author.id,
                ctx.guild.id
            )
        )

        conn.commit()
        conn.close()

        await ctx.respond(
            f"💰 You received **{reward} coins**!"
        )

    # =========================
    # BALANCE
    # =========================

    @discord.slash_command(
        name="balance",
        description="Check your coin balance"
    )
    async def balance(self, ctx):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT coins
            FROM economy
            WHERE user_id = ? AND guild_id = ?
            """,
            (ctx.author.id, ctx.guild.id)
        )

        user = cursor.fetchone()
        conn.close()

        coins = user["coins"] if user else 0

        await ctx.respond(
            f"💰 You have **{coins} coins**."
        )

    # =========================
    # PAY
    # =========================

    @discord.slash_command(
        name="pay",
        description="Give coins to another user"
    )
    async def pay(
        self,
        ctx,
        member: discord.Member,
        amount: int
    ):
        if amount <= 0:
            await ctx.respond(
                "❌ The amount must be greater than zero."
            )
            return

        if member.id == ctx.author.id:
            await ctx.respond(
                "❌ You cannot pay yourself."
            )
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Make sure both users exist.
        cursor.execute(
            """
            INSERT OR IGNORE INTO economy (
                user_id,
                guild_id,
                coins
            )
            VALUES (?, ?, 0)
            """,
            (ctx.author.id, ctx.guild.id)
        )

        cursor.execute(
            """
            INSERT OR IGNORE INTO economy (
                user_id,
                guild_id,
                coins
            )
            VALUES (?, ?, 0)
            """,
            (member.id, ctx.guild.id)
        )

        cursor.execute(
            """
            SELECT coins
            FROM economy
            WHERE user_id = ? AND guild_id = ?
            """,
            (ctx.author.id, ctx.guild.id)
        )

        sender = cursor.fetchone()

        if sender["coins"] < amount:
            conn.close()

            await ctx.respond(
                "❌ You don't have enough coins."
            )
            return

        cursor.execute(
            """
            UPDATE economy
            SET coins = coins - ?
            WHERE user_id = ? AND guild_id = ?
            """,
            (
                amount,
                ctx.author.id,
                ctx.guild.id
            )
        )

        cursor.execute(
            """
            UPDATE economy
            SET coins = coins + ?
            WHERE user_id = ? AND guild_id = ?
            """,
            (
                amount,
                member.id,
                ctx.guild.id
            )
        )

        conn.commit()
        conn.close()

        await ctx.respond(
            f"💸 {ctx.author.mention} paid "
            f"**{amount} coins** to {member.mention}."
        )

    # =========================
    # INVENTORY
    # =========================

    @discord.slash_command(
        name="inventory",
        description="View your inventory"
    )
    async def inventory(self, ctx):
        conn = get_db_connection()
        cursor = conn.cursor()

        # Normal items
        cursor.execute(
            """
            SELECT item, quantity
            FROM inventory
            WHERE user_id = ? AND guild_id = ?
            ORDER BY item
            """,
            (ctx.author.id, ctx.guild.id)
        )

        inventory_items = cursor.fetchall()

        # Pets
        cursor.execute(
            """
            SELECT pet, equipped
            FROM pets
            WHERE user_id = ? AND guild_id = ?
            ORDER BY pet
            """,
            (ctx.author.id, ctx.guild.id)
        )

        pets = cursor.fetchall()

        conn.close()

        embed = discord.Embed(
            title=f"🎒 {ctx.author.display_name}'s Inventory",
            color=discord.Color.blurple()
        )

        # =========================
        # PETS
        # =========================

        if pets:
            pet_lines = []

            for pet in pets:
                item_data = next(
                    (
                        shop_item
                        for shop_item in shop_items
                        if shop_item["tag"] == pet["pet"]
                    ),
                    None
                )

                if item_data is None:
                    pet_name = pet["pet"]
                    emoji = "🐾"
                else:
                    pet_name = item_data["name"]
                    emoji = item_data["emoji"]

                equipped = " — Equipped" if pet["equipped"] else ""

                pet_lines.append(
                    f"{emoji} **{pet_name}**{equipped}"
                )

            embed.add_field(
                name="🐾 Pets",
                value="\n".join(pet_lines),
                inline=False
            )

        # =========================
        # ITEMS
        # =========================

        if inventory_items:
            item_lines = []

            for inventory_item in inventory_items:
                item_data = next(
                    (
                        shop_item
                        for shop_item in shop_items
                        if shop_item["tag"] == inventory_item["item"]
                    ),
                    None
                )

                if item_data is None:
                    name = inventory_item["item"]
                    emoji = "📦"
                else:
                    name = item_data["name"]
                    emoji = item_data["emoji"]

                item_lines.append(
                    f"{emoji} **{name}** ×{inventory_item['quantity']}"
                )

            embed.add_field(
                name="📦 Items",
                value="\n".join(item_lines),
                inline=False
            )

        if not pets and not inventory_items:
            embed.description = "Your inventory is empty."

        await ctx.respond(embed=embed)

    # =========================
    # USE ITEM
    # =========================

    @discord.slash_command(
        name="use",
        description="Use an item from your inventory"
    )
    async def use(self, ctx, item: str):
        item_data = next(
            (
                shop_item
                for shop_item in shop_items
                if shop_item["tag"] == item
            ),
            None
        )

        if item_data is None:
            await ctx.respond("❌ Item not found.")
            return

        if item_data["type"] != "booster":
            await ctx.respond(
                f'❌ **{item_data["name"]}** cannot be used.'
            )
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check inventory quantity.
        cursor.execute(
            """
            SELECT quantity
            FROM inventory
            WHERE user_id = ?
              AND guild_id = ?
              AND item = ?
            """,
            (
                ctx.author.id,
                ctx.guild.id,
                item_data["tag"]
            )
        )

        inventory_item = cursor.fetchone()

        if inventory_item is None or inventory_item["quantity"] <= 0:
            conn.close()

            await ctx.respond(
                f'❌ You do not have **{item_data["name"]}**.'
            )
            return

        # Consume one item.
        if inventory_item["quantity"] == 1:
            cursor.execute(
                """
                DELETE FROM inventory
                WHERE user_id = ?
                  AND guild_id = ?
                  AND item = ?
                """,
                (
                    ctx.author.id,
                    ctx.guild.id,
                    item_data["tag"]
                )
            )
        else:
            cursor.execute(
                """
                UPDATE inventory
                SET quantity = quantity - 1
                WHERE user_id = ?
                  AND guild_id = ?
                  AND item = ?
                """,
                (
                    ctx.author.id,
                    ctx.guild.id,
                    item_data["tag"]
                )
            )

        now = datetime.now()

        # =========================
        # APPLY EACH EFFECT
        # =========================

        for effect, new_multiplier in item_data["effects"].items():
            new_duration = item_data["duration"]

            cursor.execute(
                """
                SELECT multiplier, expires_at
                FROM active_boosters
                WHERE user_id = ?
                  AND guild_id = ?
                  AND effect = ?
                """,
                (
                    ctx.author.id,
                    ctx.guild.id,
                    effect
                )
            )

            active_booster = cursor.fetchone()

            if active_booster:
                expires_at = datetime.fromisoformat(
                    active_booster["expires_at"]
                )

                # If the old booster expired, its remaining
                # duration is zero.
                remaining = max(
                    timedelta(0),
                    expires_at - now
                )

                total_duration = remaining + timedelta(
                    seconds=new_duration
                )

                multiplier = max(
                    active_booster["multiplier"],
                    new_multiplier
                )

                new_expires_at = now + total_duration

                cursor.execute(
                    """
                    UPDATE active_boosters
                    SET multiplier = ?,
                        expires_at = ?
                    WHERE user_id = ?
                      AND guild_id = ?
                      AND effect = ?
                    """,
                    (
                        multiplier,
                        new_expires_at.isoformat(),
                        ctx.author.id,
                        ctx.guild.id,
                        effect
                    )
                )

            else:
                expires_at = now + timedelta(
                    seconds=new_duration
                )

                cursor.execute(
                    """
                    INSERT INTO active_boosters (
                        user_id,
                        guild_id,
                        effect,
                        multiplier,
                        expires_at
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        ctx.author.id,
                        ctx.guild.id,
                        effect,
                        new_multiplier,
                        expires_at.isoformat()
                    )
                )

        conn.commit()
        conn.close()

        await ctx.respond(
            f'⚡ You activated **{item_data["name"]}**!'
        )


def setup(bot):
    bot.add_cog(Economy(bot))