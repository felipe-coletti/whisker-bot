import sqlite3
from config import DB_NAME


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS xp (
            user_id INTEGER,
            guild_id INTEGER,
            xp INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, guild_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Database initialized (whisker.db) with guild support.")


def add_xp(user_id, guild_id, amount):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT xp FROM xp WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
    row = cursor.fetchone()
    
    if row:
        new_xp = row['xp'] + amount
        cursor.execute("UPDATE xp SET xp = ? WHERE user_id = ? AND guild_id = ?", (new_xp, user_id, guild_id))
    else:
        cursor.execute("INSERT INTO xp (user_id, guild_id, xp) VALUES (?, ?, ?)", (user_id, guild_id, amount))
    
    conn.commit()
    conn.close()


def get_top_users(guild_id, limit=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id, xp FROM xp WHERE guild_id = ? ORDER BY xp DESC LIMIT ?", (guild_id, limit))
    rows = cursor.fetchall()
    
    conn.close()
    return [(row['user_id'], row['xp']) for row in rows]


def get_user_xp(user_id, guild_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT xp FROM xp WHERE user_id = ? AND guild_id = ?", (user_id, guild_id))
    row = cursor.fetchone()
    conn.close()
    
    return row['xp'] if row else 0