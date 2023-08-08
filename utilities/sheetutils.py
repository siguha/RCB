import gspread
import discord
import asyncio
import aiosqlite
from datetime import datetime
from .exceptions import Exceptions

SA = gspread.service_account(filename = 'service_account.json')
OFFICER = SA.open_by_url('https://docs.google.com/spreadsheets/d/1k4p4lUivqTXYhWeQ8a3AwevV_SsJwokNjqSooLQ9q0k/')
PUBLIC = SA.open_by_url('https://docs.google.com/spreadsheets/d/1PBPZOHxNSw9hzSErpFxQ6E_OtyNKTptTK7M6BmG3-J8/')
AAR = SA.open_by_url('https://docs.google.com/spreadsheets/d/1dQso9v7GN4yXE5MsiTeS4tJdHQZKbR77ZXymM-wJUPg/')
AARs = AAR.worksheet('AAR Logs')
ROSTER = PUBLIC.worksheet('Roster')
DATABASE = OFFICER.worksheet('Officer View')
IDS = OFFICER.worksheet('IDs')
e = Exceptions()

# def run_and_get(coro):
#     task = asyncio.create_task(coro)
#     asyncio.get_running_loop().run_until_complete(task)
#     return task.result()

class SheetUtilities:
    """Sheet utilities for the RCBot."""

    async def id_fetch(self, did: int) -> str:
        db = await aiosqlite.connect('ids.db')

        async with db.cursor() as cursor:
            await cursor.execute('''SELECT steamid FROM ids WHERE did = ?''', (did,))
            data = await cursor.fetchone()
            
        await db.close()

        try:
            return data[0]
        
        except:
            raise e.UserNotFound('SteamID not found in database. Profile not synced.')

    # async def bulk_id_fetch(self, dids: list[int]) -> list[str]:
    #     db = await aiosqlite.connect('ids.db')
    #     ids 

    async def last_row(self, sheet: gspread.Worksheet, col: int = 2) -> None:
        """Fetches the last row of a column.
        
        Parameters
        ------------
        sheet: :class:`gspread.Worksheet`
            The worksheet to search in.
        
        col: :class:`int` = 2
            The column to search for. Defaults to 2 (side columns)
        
        Returns
        ------------
        :class:`str`
            Returns the last row.
        """

        values = sheet.col_values(col)
        size = str(len(values) + 1)

        return size
    
    async def last_arr(self, did: int) -> str:
        steamid = await self.id_fetch(did)
        row = AARs.find(steamid)
        date = AARs.acell(f'A{row.row}').value
        return date

    class ProfileUtils:
        """Profile Utilities class of SheetUtilities."""

        def __init__(self):
            # asyncio.run(self.db_connect())
            loop = asyncio.get_running_loop()

            loop.create_task(self.db_connect())
            self.utils = SheetUtilities()

        async def db_connect(self) -> None:
            db = await aiosqlite.connect('ids.db')

            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS ids (did INTEGER PRIMARY KEY, 
                                    steamid TEXT, 
                                    name TEXT)''')
            await db.commit()
    
        async def profile_sync(self, steamid: str, discordid: str, name: str) -> None:
            """Syncs a user's Discord ID to their SteamID, storing it locally as well as on a sheet.
            
            Parameters
            ------------
            steamid: :class:`str`
                The user's SteamID.
            discordid: :class:`str`
                The user's DiscordID.
            name: :class:`str`
                The user's Discord display name at the time of call.
            """
            db = await aiosqlite.connect('ids.db')
            last_row = await self.utils.last_row(IDS, 1)

            async with db.cursor() as cursor:
                await cursor.execute('''INSERT INTO ids (did, steamid, name) VALUES (?, ?, ?)
                                        ON CONFLICT(did) DO
                                        UPDATE SET steamid = excluded.steamid, name = excluded.name''', (discordid, steamid, name))
                await db.commit()
            await db.close()

            existing = IDS.find(steamid)
            if existing is None:
                IDS.batch_update([{
                    'range' : f'A{last_row}:C{last_row}',
                    'values' : [[name, steamid, str(discordid)]],

                }], value_input_option = 'RAW')

            else:
                IDS.batch_update([{
                    'range' : f'A{existing.row}:C{existing.row}',
                    'values' : [[name, steamid, str(discordid)]],

                }], value_input_option = 'USER_ENTERED')

        async def stats_fetch(self, did: int) -> dict[str]:
            row = DATABASE.find(str(did))

            if row is None:
                raise e.UserNotFound('User not found in Officer Database.')
            
            else:
                last_aar = await self.utils.last_arr(did)
                vals = DATABASE.row_values(row.row)
                data = {
                    'PROMO_DATE' : vals[8],
                    'PROMO_DAYS' : vals[9],
                    'LOGS' : vals[12],
                    'PARTICIPATED' : vals[13],
                    'TRAININGS' : vals[15],
                    'COHOSTS' : vals[16],
                    'LEADS' : vals[17],
                    'SGT_TRIALS' : vals[18],
                    'BT_TRIALS' : vals[19],
                    'LAST_AAR' : last_aar
                }

                return data
        
        async def profile_fetch(self, did: int) -> dict[str]:
            steamid = await self.utils.id_fetch(did)
            row = ROSTER.find(steamid)

            if row is None:
                raise e.UserNotFound("User not found in roster. Possibly resetting, or they don't exist.")
            
            else:
                vals = ROSTER.row_values(row.row)
                data = {
                    'NAME' : vals[3],
                    'RANK' : vals[1],
                    'CLASS' : vals[2],
                    'JOINED' : vals[7],
                    'DAYS_IN' : vals[8],
                    'DAYS_SINCE' : vals[14],
                    'REGION' : vals[26],
                    'DEMO' : 'Trainer+' if vals[17] == 'a' else 'Certified' if vals[17] == 'b' else 'Trainee' if vals[17] == 'c' else 'Untrained',
                    'ENGINEER' : 'Trainer+' if vals[19] == 'a' else 'Certified' if vals[19] == 'b' else 'Trainee' if vals[19] == 'c' else 'Untrained',
                    'MEDIC' : 'Trainer+' if vals[21] == 'a' else 'Certified' if vals[21] == 'b' else 'Trainee' if vals[21] == 'c' else 'Untrained',
                    'SNIPER' : 'Trainer+' if vals[23] == 'a' else 'Certified' if vals[23] == 'b' else 'Trainee' if vals[23] == 'c' else 'Untrained',
                }

                return data

    class AarUtils:
        ...
        
# https://discord.com/api/oauth2/authorize?client_id=1109688912026288168&permissions=8&scope=bot%20applications.commands