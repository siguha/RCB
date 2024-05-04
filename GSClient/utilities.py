import aiosqlite
import gspread
import datetime

from . import AARS

class SheetUtilities:
    def __init__(self, database_manager):
        self.db = database_manager

    async def get_user_id(self, discord_id: int):
        async with await self.db.get_cursor() as cursor:
            await cursor.execute('''SELECT steamid FROM ids WHERE did = ?''', (discord_id,))
            user = await cursor.fetchone()

        if user is not None:
            return user[0]
        else:
            raise ValueError('SteamID not found in Database. Profile not synced.')
    
    @staticmethod
    async def get_last_row(sheet: gspread.Worksheet, col: int=2):
        return len(sheet.col_values(col))