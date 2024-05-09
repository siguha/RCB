import aiosqlite

class DatabaseManager:
    def __init__(self, database_path):
        self.database_path = database_path
        self.connection = None

    @classmethod
    async def create(cls, database_path):
        self = cls(database_path)
        await self.connect()
        await self.initialize_db()
        return self

    async def connect(self):
        if not self.connection:
            self.connection = await aiosqlite.connect(self.database_path)
            print("Database Connection Established.")
    
    async def get_cursor(self):
        return await self.connection.cursor()
    
    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
            print("Database Connection Terminated.")

    async def test_cursor(self):
        async with self.connection.cursor() as cursor:
            await cursor.execute('SELECT 1;')
            print(await cursor.fetchone())    

    async def initialize_db(self):
        table_creation_commands = [
            """
            CREATE TABLE IF NOT EXISTS ids (
                did INTEGER PRIMARY KEY,
                steamid TEXT,
                batch TEXT,
                designation TEXT,
                name TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS aars (
                log_id INTEGER PRIMARY KEY, 
                msg_id INTEGER
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS squads (
                squad_name TEXT PRIMARY KEY,
                role_id INTEGER,
                channel_id INTEGER,
                mem1 INTEGER,
                mem2 INTEGER,
                mem3 INTEGER,
                mem4 INTEGER,
                mem5 INTEGER,
                persistent TEXT
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS stickies (
                message_id INTEGER PRIMARY KEY,
                title TEXT
            );
            """
        ]

        async with self.connection.cursor() as cursor:
            for command in table_creation_commands:
                await cursor.execute(command)
            
            await self.connection.commit()