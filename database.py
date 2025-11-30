import aiosqlite

DB_PATH = 'bot_database.sqlite3'


class Database:
    def __init__(self):
        self.db = None

    async def init(self):
        self.db = await aiosqlite.connect(DB_PATH)
        await self.create_tables()

    async def create_tables(self):
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS user_xp (
                user_id INTEGER NOT NULL,
                guild_id INTEGER NOT NULL,
                xp INTEGER NOT NULL DEFAULT 0,
                level INTEGER NOT NULL DEFAULT 1,
                PRIMARY KEY (user_id, guild_id)
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS mission_threads (
                thread_id INTEGER PRIMARY KEY,
                xp INTEGER NOT NULL
            )
        """)
        await self.db.execute("""
            CREATE TABLE IF NOT EXISTS awarded_messages (
                message_id INTEGER PRIMARY KEY
            )
        """)
        await self.db.commit()

    # User XP methods

    async def get_user_data(self, guild_id: int, user_id: int):
        async with self.db.execute(
            "SELECT xp, level FROM user_xp WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return {"xp": row[0], "level": row[1]}
            else:
                # Insert default if not exist
                await self.db.execute(
                    "INSERT INTO user_xp (user_id, guild_id, xp, level) VALUES (?, ?, 0, 1)",
                    (user_id, guild_id)
                )
                await self.db.commit()
                return {"xp": 0, "level": 1}

    async def set_user_xp_level(self, guild_id: int, user_id: int, xp: int, level: int):
        await self.db.execute("""
            INSERT INTO user_xp (user_id, guild_id, xp, level) VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, guild_id) DO UPDATE SET xp=excluded.xp, level=excluded.level
        """, (user_id, guild_id, xp, level))
        await self.db.commit()

    # Add XP, return if leveled up

    async def add_user_xp(self, guild_id: int, user_id: int, amount: int):
        data = await self.get_user_data(guild_id, user_id)
        old_level = data["level"]
        new_xp = data["xp"] + amount

        # XP to level formula: level determined by lowest integer where xp < 100 * level*level
        new_level = 1
        for lvl in range(1, 100):
            if new_xp < 100 * lvl * lvl:
                new_level = lvl
                break

        await self.set_user_xp_level(guild_id, user_id, new_xp, new_level)

        return new_level > old_level  # True if leveled up

    # Mission thread xp

    async def add_mission_thread(self, thread_id: int, xp: int):
        await self.db.execute("""
            INSERT OR REPLACE INTO mission_threads (thread_id, xp) VALUES (?, ?)
        """, (thread_id, xp))
        await self.db.commit()

    async def get_mission_xp(self, thread_id: int):
        async with self.db.execute("SELECT xp FROM mission_threads WHERE thread_id = ?", (thread_id,)) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

    # Awarded messages

    async def is_message_awarded(self, message_id: int):
        async with self.db.execute("SELECT 1 FROM awarded_messages WHERE message_id = ?", (message_id,)) as cursor:
            return await cursor.fetchone() is not None

    async def add_awarded_message(self, message_id: int):
        await self.db.execute("INSERT INTO awarded_messages (message_id) VALUES (?)", (message_id,))
        await self.db.commit()


# Create one singleton instance for easy import/use
database = Database()
