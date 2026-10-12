# 🐾 Whisker

Whisker is a Discord bot with XP-based leveling and a server economy. Members earn XP by chatting, level up to earn coins and spend those coins in a shop of pets and boosters. All progress is tracked per server.

Built with [Pycord](https://pycord.dev/) and SQLite.

## Features

- **Leveling.** Every message earns XP. Level-ups are announced in the channel and pay out coins.
- **Leaderboard.** See the 10 most active members of the server.
- **Economy.** Daily rewards, coin balances and payments between members.
- **Shop.** Buy pets that give passive bonuses and boosters that multiply XP or coins for a limited time.
- **Welcome and goodbye messages.** Posted in the server's system channel when a member joins or leaves.
- **Rotating status.** The bot's custom status changes every 60 seconds.

## Commands

All commands are slash commands.

### General

| Command | Description |
| --- | --- |
| `/help` | List the available commands (only you can see the reply). |
| `/greeting` | A friendly greeting. |

### XP and leveling

| Command | Description |
| --- | --- |
| `/xp view` | Show your level, total XP and progress to the next level. |
| `/xp rank` | Show the server's top 10 members by XP. |
| `/xp leaderboard` | Alias for `/xp rank`. |
| `/xp transfer <amount> <user>` | Send some of your XP to another member. |

### Economy

| Command | Description |
| --- | --- |
| `/balance` | Show your coin balance. |
| `/daily` | Claim your daily coins (once every 24 hours). |
| `/pay <member> <amount>` | Give coins to another member. |
| `/shop view` | List the items for sale. |
| `/shop buy <item>` | Buy an item by its tag (for example, `xp_booster`). |
| `/inventory` | Show your pets and items. |
| `/use <item>` | Activate a booster from your inventory. |

## How it works

### Leveling

Each message sent in a server gives **1 XP** (multiplied by any active XP booster). The total XP needed for each level grows as follows:

| Level | Total XP |
| --- | --- |
| 1 | 100 |
| 2 | 300 |
| 3 | 600 |
| 4 | 1,000 |
| *n* | 100 × *n* × (*n* + 1) / 2 |

Reaching a new level pays **500 × the new level** in coins, so reaching level 3 pays 1,500 coins. Coin boosters apply to this reward.

### Economy

`/daily` pays **100 coins**, plus the bonus from your equipped pet, multiplied by any active coin booster.

### Shop

| Item | Tag | Cost | Type | Effect |
| --- | --- | --- | --- | --- |
| 🐀 Rat | `rat` | 50 | Pet | +5 coins on `/daily` |
| 🪙 Coin Booster | `coin_booster` | 500 | Booster | 2× coins for 1 hour |
| 🪙 Mega Coin Booster | `mega_coin_booster` | 1,500 | Booster | 3× coins for 2 hours |
| ✨ XP Booster | `xp_booster` | 500 | Booster | 2× XP for 1 hour |
| ✨ Mega XP Booster | `mega_xp_booster` | 1,500 | Booster | 3× XP for 2 hours |
| 💎 Ultimate Booster | `ultimate_booster` | 5,000 | Booster | 3× coins and XP for 24 hours |

- **Pets** can only be owned once each. Your first pet is equipped automatically.
- **Boosters** go to your inventory when bought and start when you run `/use`. Using a booster while another one for the same effect is active adds the new duration to the remaining time and keeps the higher multiplier.

## Running your own instance

### Requirements

- Python 3.14 or newer
- A Discord application with a bot user ([Discord Developer Portal](https://discord.com/developers/applications))

### 1. Create the bot

1. In the Developer Portal, create an application and open the **Bot** tab.
2. Copy the bot token.
3. Under **Privileged Gateway Intents**, turn on **Presence Intent**, **Server Members Intent** and **Message Content Intent**. Whisker needs these to count messages and to see members joining and leaving.
4. Under **OAuth2 → URL Generator**, select the `bot` and `applications.commands` scopes and the **View Channels**, **Send Messages**, **Embed Links** and **Read Message History** permissions. Open the generated URL to invite the bot to your server.

### 2. Install

```bash
git clone https://github.com/felipe-coletti/whisker-bot.git
cd whisker-bot

python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3. Configure

Copy the example environment file and add your token:

```bash
cp .env.example .env
```

```env
DISCORD_TOKEN=your_discord_bot_token_here
```

### 4. Run

```bash
python main.py
```

On first start, Whisker creates a `whisker.db` SQLite database in the working directory. Slash commands can take a few minutes to show up in Discord after the bot first connects.

## Customization

Settings live in [`config.py`](config.py):

| Setting | Default | Description |
| --- | --- | --- |
| `DAILY_COINS` | `100` | Base reward for `/daily`. |
| `LEVEL_COINS` | `500` | Coins per level reached, multiplied by the new level. |
| `STATUSES` | `"Meow"`, `"Pow!"`, … | Texts the bot rotates through as its status. |
| `shop_items` | See [Shop](#shop) | Items available in the shop. |

New shop items follow the same shape as the existing ones: a unique `tag`, a `type` of `pet` or `booster`, an `effects` map and, for boosters, a `duration` in seconds.

## Project structure

```
whisker-bot/
├── main.py           # Entry point: creates the bot and loads the cogs
├── config.py         # Token, intents, statuses, rewards and shop items
├── database.py       # SQLite schema and helpers for XP, coins and boosters
├── cogs/
│   ├── core.py       # /help and /greeting
│   ├── economy.py    # Shop, daily, balance, pay, inventory and use
│   ├── events.py     # Ready, status rotation, welcome and goodbye
│   └── leveling.py   # XP gain, level-ups and /xp commands
├── requirements.txt
└── .env.example
```

Every `.py` file in `cogs/` is loaded automatically on startup, so a new feature can be added as a new cog with a `setup(bot)` function.