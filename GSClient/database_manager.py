import aiosqlite

class DatabaseManager:
    def __init__(self, database_path):
        self.database_path = database_path
        self.connection = None

    async def connect(self):
        if not self.connection:
            self.connection = await aiosqlite.connect(self.database_path)\
    
    async def get_cursor(self):
        return await self.connection.cursor()
    
    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None