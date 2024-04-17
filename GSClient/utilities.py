import aiosqlite
import gspread
import datetime

from . import AARS

class SheetUtilities:
    @staticmethod
    async def get_user_id(discord_id: int):
        db = await aiosqlite.connect('data.db')

        async with db.cursor() as cursor:
            await cursor.execute('''SELECT steamid FROM ids WHERE did = ?''', (discord_id,))
            user = await cursor.fetchone()

        await db.close()

        if user is not None:
            return user[0]
        else:
            raise ValueError('SteamID not found in Database. Profile not synced.')
    
    @staticmethod
    async def get_last_row(sheet: gspread.Worksheet, col: int=2):
        return len(sheet.col_values(col))