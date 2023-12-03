import gspread
import asyncio
import aiosqlite
import discord
import random
from typing import List
from collections import deque
import datetime
from .exceptions import Exceptions

SA = gspread.service_account(filename = 'service_account.json')
OFFICER = SA.open_by_url('https://docs.google.com/spreadsheets/d/1k4p4lUivqTXYhWeQ8a3AwevV_SsJwokNjqSooLQ9q0k/')
PUBLIC = SA.open_by_url('https://docs.google.com/spreadsheets/d/1PBPZOHxNSw9hzSErpFxQ6E_OtyNKTptTK7M6BmG3-J8/')
AAR = SA.open_by_url('https://docs.google.com/spreadsheets/d/1dQso9v7GN4yXE5MsiTeS4tJdHQZKbR77ZXymM-wJUPg/')
AARs = AAR.worksheet('AAR Logs')
TRYOUTS = PUBLIC.worksheet('Tryouts')
ROSTER = PUBLIC.worksheet('Roster')
LOAS = PUBLIC.worksheet('LOA / ROA')
SQUADS = PUBLIC.worksheet('Lore Squads')
DATABASE = OFFICER.worksheet('Officer View')
POP = OFFICER.worksheet('Population')
IDS = OFFICER.worksheet('IDs')
e = Exceptions()

class SheetUtilities:
    """Sheet utilities for the RCBot."""

    class Paginator(discord.ui.View):
        def __init__(self, embeds: List[discord.Embed]):
            super().__init__(timeout=None)
            self._embeds = embeds
            self._initial = embeds[0]
            self._len = len(embeds)
            self._current_page = 1

        @discord.ui.button(emoji = "⬅️")
        async def previous(self, interaction: discord.Interaction, _) -> None:
            self._queue.rotate(1)
            embed = self._queue[0]
            await interaction.response.edit_message(embed = embed)
        
        @discord.ui.button(emoji = "➡️")
        async def next(self, interaction: discord.Interaction, _) -> None:
            self._queue.rotate(-1)
            embed = self._queue[0]
            await interaction.response.edit_message(embed = embed)

        @property
        def initial(self) -> discord.Embed:
            return self._initial

    def chunks(self, list, n) -> list:
        n = max(1, n)
        return (list[i:i+n] for i in range(0, len(list), n))

    async def id_fetch(self, did: int) -> str:
        db = await aiosqlite.connect('rcb.db')

        async with db.cursor() as cursor:
            await cursor.execute('''SELECT steamid FROM ids WHERE did = ?''', (did,))
            data = await cursor.fetchone()
            
        await db.close()

        try:
            return data[0]
        
        except:
            raise e.UserNotFound('SteamID not found in database. Profile not synced.')

    async def last_row(self, sheet: gspread.Worksheet, col: int = 2) -> str:
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
    
    async def last_arr(self, did: int) -> tuple[datetime.datetime, int]:
        row = AARs.find(str(did))
        print(row)
        date = datetime.datetime.strptime(AARs.acell(f'A{row.row}').value, '%m/%d/%Y %H:%M:%S')
        today = datetime.datetime.now()
        days = (today - date).days

        return date, days

    class ProfileUtils:
        """Profile Utilities class of SheetUtilities."""

        def __init__(self):
            # asyncio.run(self.db_connect())
            loop = asyncio.get_running_loop()
            loop.create_task(self.db_connect())
            self.utils = SheetUtilities()

        async def db_connect(self) -> None:
            db = await aiosqlite.connect('rcb.db')

            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS ids (did INTEGER PRIMARY KEY, 
                                    steamid TEXT, 
                                    name TEXT)''')
            await db.commit()
            await db.close()
    
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
            db = await aiosqlite.connect('rcb.db')
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
                }], value_input_option = 'RAW')

        async def stats_fetch(self, did: int) -> dict[str]:
            row = DATABASE.find(str(did))

            if row is None:
                raise e.UserNotFound('User not found in Officer Database.')
            
            else:
                # last_aar, days = await self.utils.last_arr(did)
                vals = DATABASE.row_values(row.row)
                data = {
                    'PROMO_DATE' : vals[13],
                    'PROMO_DAYS' : vals[14],
                    'LOGS' : vals[17],
                    'PARTICIPATED' : vals[18],
                    'TRYOUTS' : vals[19],
                    'TRAININGS' : vals[20],
                    'COHOSTS' : vals[21],
                    'LEADS' : vals[22],
                    'SGT_TRIALS' : vals[23],
                    'BT_TRIALS' : vals[24],
                    'LAST_AAR' : vals[11],
                    'LAST_AAR_DAYS' : vals[12],
                    'LAST_SEEN' : vals[9],
                    'LAST_SEEN_DAYS' : vals[10],
                    'LOA' : vals[27]
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

    class OfficerUtils:
        def __init__(self):
            self.utils = SheetUtilities()

        async def officer_vote(self, did: int):
            loc = DATABASE.find(str(did))

            if loc is None:
                raise e.UserNotFound(f'DiscordID {did} not found in Officer Database.')

            else:
                row = loc.row
                col = 26
                DATABASE.update_cell(row, col, datetime.datetime.now().strftime('%m/%d/%Y'))

        async def officer_warn(self, did: int):
            loc = DATABASE.find(str(did))

            if loc is None:
                raise e.UserNotFound(f'DiscordID {did} not found in Officer Database.')

            else:
                row = loc.row
                col = 16
                DATABASE.update_cell(row, col, 'TRUE')

    class AarUtils:
        """AAR Utilities class of SheetUtilities."""

        def __init__(self):
            loop = asyncio.get_running_loop()
            loop.create_task(self.db_connect())
            self.utils = SheetUtilities()

        async def db_connect(self) -> None:
            db = await aiosqlite.connect('rcb.db')

            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS aars (log_id INTEGER PRIMARY KEY, 
                                    msg_id INTEGER)''')
            await db.commit()
            await db.close()

        async def aar_cache(self, log_id: int, msg_id: int):
            db = await aiosqlite.connect('rcb.db')

            async with db.cursor() as cursor:
                await cursor.execute('''INSERT INTO aars (log_id, msg_id) VALUES (?, ?)''', (log_id, msg_id))

            await db.commit()
            await db.close()

        async def aar_remove(self, log_id: int):
            db = await aiosqlite.connect('rcb.db')

            async with db.cursor() as cursor:
                await cursor.execute('''DELETE FROM aars WHERE log_id = ?''', (log_id,))
            
            await db.commit()
            await db.close()

            log_loc = AARs.find(str(log_id).zfill(14))
            try:
                AARs.delete_row(log_loc.row)

            except AttributeError:
                raise e.LogNotFound(f'LogID `{log_id}` not found in AAR sheet.')

        async def aar_fetch(self, log_id: str):
            db = await aiosqlite.connect('rcb.db')

            async with db.cursor() as cursor:
                await cursor.execute('''SELECT msg_id FROM aars WHERE log_id = ?''', (log_id,))
                msg_id = await cursor.fetchone()

            await db.close()
            return msg_id[0]

        async def aar_create(self, *args, msg_id: int, log_id: int, log: str, logger_id: int, users: list[int] = None):
            await self.aar_cache(log_id, msg_id)
            date = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
            AARs.insert_row(values = [date, str(log_id), log, str(logger_id)], value_input_option = 'USER_ENTERED', index = 3)   
            
            if log == 'Lead' or log == "Lead Spectate":
                AARs.append_row(values = [str(args[4]), args[0], args[1], args[2], args[3]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'E3:I3')

            elif log == 'Training':
                AARs.append_row(values = [args[0], args[1], args[2], args[3], args[4]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'J3:N3')
            
            elif log == 'Lore Activity':
                AARs.append_row(values = [args[0], args[1], args[2]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'O3:Q3')

            elif log == 'BT':
                AARs.append_row(values = [args[0], args[1], args[2]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'R3:T3')               

            elif log == 'SGT Trials':
                AARs.append_row(values = [args[0], args[1], args[2]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'U3:W3')

            elif log == 'Spec Cert':
                AARs.append_row(values = [args[0], args[1], args[2]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'X3:Z3')

            elif log == 'Tryout':
                last_row = await self.utils.last_row(TRYOUTS)
                date = datetime.datetime.now().strftime("%m/%d/%Y")
                AARs.append_row(values = [args[1], args[2], args[3]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'AA3:AC3')
                TRYOUTS.append_row(values = [date, args[0], args[3], args[4], args[1], args[2]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = f'B{int(last_row)}:G{int(last_row)}')

            if users is not None:
                col = 30
                for user in users:
                    AARs.update_cell(3, col, str(user))
                    col += 1

        async def aar_append(self, log_id: int, members: list[str]):
            loc = AARs.find(str(log_id).zfill(14))

            if loc is None:
                raise e.LogNotFound(f'LogID `{log_id}` not found in AAR sheet.')
            else:
                row = loc.row
                length = len(AARs.row_values(row))
                col = (length + 1) if length >= 29 else 29

                for member in members:
                    AARs.update_cell(row, col, member)
                    col += 1
        
        async def aar_pop(self, log_id: int, user: int):
            log_loc = AARs.find(str(log_id).zfill(14))
            row_vals = AARs.row_values(log_loc.row)
            col = row_vals.index(str(user)) + 1
            AARs.update_cell(log_loc.row, col, '')

    class LOAUtils:
        """LOA Utilities class of SheetUtilities."""

        def __init__(self):
            self.utils = SheetUtilities()
            self.conversions = {
                'Start' : 5,
                'End' : 6,
                'Type' : 8
            }

        async def loa_add(self, *, name: str, user_id: int, start_date: str, end_date: str, type: str, reason: str):
            last_row = await self.utils.last_row(LOAS, 3)
            steamid = await self.utils.id_fetch(user_id)
            if LOAS.find(steamid) is not None:
                raise e.LOAExisting(f"User {steamid} has an existing LOA.")
            
            LOAS.append_row([name, steamid, start_date, end_date, None, type, None, reason, '0', str(user_id)], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = f'C{last_row}:J{last_row}')

        async def loa_end(self, *, user: int) -> bool:
            steamid = await self.utils.id_fetch(user)
            loc = LOAS.find(steamid)
            
            if loc is None:
                raise e.LOANotFound(f"LOA for user `{steamid}` not found.")

            else:
                LOAS.delete_row(loc.row)
        
        async def loa_edit(self, *, user: str, field: str, edit: str):
            steamid = await self.utils.id_fetch(user)
            loc = LOAS.find(steamid)

            if loc is None:
                raise e.LOANotFound(f"LOA for user `{steamid}` not found.")

            else:
                row = loc.row
                col = self.conversions[field]
                LOAS.update_cell(row, col, edit)
                LOAS.update_cell(row, 11, '0')

        async def loa_fetch(self, *, user: int):
            steamid = await self.utils.id_fetch(user)
            loc = LOAS.find(steamid)

            if loc is None:
                raise e.LOANotFound(f"LOA for user `{steamid}` not found.")

            else:
                row_vals = LOAS.row_values(loc.row)
                data = {
                    'start' : row_vals[4],
                    'end' : row_vals[5],
                    'type' : row_vals[7]
                }

                return data
        
        async def loa_checkin(self):
            active_loas = LOAS.col_values(9)
            expirations = []
            
            for index, loa in enumerate(active_loas):
                try:
                    if int(loa) <= 2:
                        row_values = LOAS.row_values(index + 1)

                        if row_values[10] == '0':
                            LOAS.update_cell(index + 1, 11, '1')
                            did, end, days, absence, name = row_values[11], row_values[5], row_values[8], row_values[7], row_values[2]
                            expirations.append([did, end, days, absence, name])       

                        else:
                            pass         
                except:
                    pass
            return expirations
            
    class MiscUtils:
        """Misc Utilities class of SheetUtilities."""

        def __init__(self):
            self.utils = SheetUtilities()

        async def retention_fetch(self):
            __retention_stats = POP.get("A1:B31")
            
            data = {
                'date' : __retention_stats[1][0],
                'headcount' : __retention_stats[1][1],
                'date_old' : __retention_stats[30][0],
                'headcount_old' : __retention_stats[30][1],
                'retention' : __retention_stats[0][0],
            }

            return data

        async def trainer_fetch(self, spec: str = None):
            __c = {
                'a': 'Trainer+',
                'b': 'Certified',
                'c': 'Trainee',
                '' : 'Uncertified'
            }
            __trainer_list_raw = ROSTER.get('D5:X')
            trainer_list = []

            for row in __trainer_list_raw:
                trainer_list.append([row[0], row[14], row[16], row[18], row[20]])
                

        async def squad_fetch(self, squad: str = None):
            __squad_list_raw = SQUADS.batch_get(['B3:F6', 'B8:F11', 'B13:F16', 'B18:F21', 'B23:F26', 'B28:F31', 'B33:F36'])
            __squad_list = [[item[0], item[4]] for sublist in __squad_list_raw for item in sublist]
            pages = []
            squad_names = {
                0 : ['Foxtrot Squad', 'A squad of elite commandos lead by Gregor who supported and stood by members of the 212th Attack Battalion in a line up of hard fought victories. Specialized and war trained in calculated brute force blitz attack formations, composed of Gregor, Impact, Point and Hardwire.', discord.Colour.gold(), 'https://i.imgur.com/aPMJied.jpeg', 0, 4],
                1 : ['Delta Squad', 'Delta Squad was an elite clone commando squad that carried out demanding missions for the Grand Army of the Republic during the Clone Wars, composed of Boss, Fixer, Scorch and Sev alongside Jedi companion Echuu Shen-Jon.', discord.Colour.from_rgb(230, 139, 3), 'https://i.imgur.com/FKInLWQ.jpeg', 4, 8],
                2 : ['Omega Squad', 'Omega Squad are a clone commando unit who frequently were deployed on covert ops missions.The members of this unit were brought together after each of their respective squads were killed during action at Geonosis, composed of Niner, Atin, Darman, Fi and their Jedi companion Etain Tur-Mukan.', discord.Colour.from_rgb(11, 83, 148), 'https://i.imgur.com/U7gNRfC.jpeg', 8, 12],
                3 : ['Ion Squad', 'Ion Team was a squad of clone commandos attached to the 22nd Air Combat Wing. They’re considered aces with spacecraft. Ion was trained by Cuy’val Dar and Corellians. On the server they act as pilots for RC or assist pilots if needed, composed of Climber, Unknown, Ras, Trace and Jedi companion Roan Shryne.', discord.Colour.light_grey(), 'https://i.imgur.com/iJulcAP.jpeg', 12, 16],
                4 : ['Clone Force-99, informally dubbed the "Bad Batch"', 'Unofficially known as the "Bad Batch", this is a squad of clones with extreme genetic modifications that resulted in each clone having unique traits focused around their individual personalities. Infamous for their unorthodox technique and strategy, the squad was composed of Hunter with sensory abilities, Wrecker with incredible strength, Tech with enhanced mental capacity and intelligence, and Crosshair with unmatched marksmanship and eyesight.', discord.Colour.red(), 'https://i.imgur.com/JhkFmIv.png', 16, 20],
                5 : ['Yayax Squad', 'Yayax is a squad of clone commandos specialized in covert urban warfare and night operations. This squad makes use of advanced Republic issued tools consisting of reinforced armor plating, opto-electronics, as well as secondary and tertiary lighting. Their performance in the Battle of Coruscant alongside Omega Squad sealed its legacy. They were one of the squads trained by Mandalorian Rav Bralor on the planet Kamino, composed of Cov, Jind, Yover, Dev and Jedi companion Naat Reath.', discord.Colour.from_rgb(139, 119, 75), 'https://i.imgur.com/7FfMSsb.jpeg', 20, 24],
                6 : ['Aiwha Squad', "Aiwha is a squad of clone commandos specialized in guerrilla warfare. This squad routinely executed various avant-garde techniques and strategies to best their opponents in often irregular terrain, composed of Sarge, Zag, Tyto, Di'kut and Jedi companion Traavis.", discord.Colour.from_rgb(105, 141, 115), 'https://i.imgur.com/jmMmZs2.jpeg', 24, 28]
            }   

            if squad is None:
                squad_list = list(self.utils.chunks(__squad_list, 4))
                for n_chunk, chunk in enumerate(squad_list):
                    text = ''
                    for member in chunk:
                        text += f'**{member[0]}**: {member[1] if member[1] != "Open" else "*Open*"}\n'
                    embed = discord.Embed(title=squad_names[n_chunk][0], description=squad_names[n_chunk][1], colour=squad_names[n_chunk][2])
                    embed.set_image(url=squad_names[n_chunk][3])
                    embed.add_field(name='Squad Members', value=text)
                    embed.set_author(name='Lore Squad Information', icon_url='https://i.imgur.com/rgsTDEj.png')
                    pages.append(embed)
            
                return pages
            else:
                for key, value in squad_names.items():
                    if squad in value[0]:
                        text = ''
                        for member in __squad_list[value[4]:value[5]]:
                            text += f'**{member[0]}**: {member[1]}\n'
                        
                        embed = discord.Embed(title=value[0], description=value[1], colour=value[2])
                        embed.set_image(url=value[3])
                        embed.add_field(name='Squad Members', value=text)
                        embed.set_author(name='Lore Squad Information', icon_url='https://i.imgur.com/rgsTDEj.png')

                        return embed

    class SquadUtils: 
        """Squad Utilities class of SheetUtilities."""
        
        def __init__(self):
            loop = asyncio.get_running_loop()
            loop.create_task(self.db_connect())
            self.utils = SheetUtilities()

        async def db_connect(self) -> None:
            db = await aiosqlite.connect('rcb.db')

            async with db.cursor() as cursor:
                await cursor.execute('''CREATE TABLE IF NOT EXISTS squads (name TEXT PRIMARY KEY,
                                    role INTEGER,
                                    channel INTEGER,
                                    mem1 INTEGER,
                                    mem2 INTEGER,
                                    mem3 INTEGER,
                                    mem4 INTEGER,
                                    mem5 INTEGER)''')

            await db.commit()
            await db.close()

        async def squad_builder(self, guild: discord.Guild) -> None:
            db = await aiosqlite.connect('rcb.db')
            _squad_list = list(set([item for sublist in DATABASE.get("E4:E") for item in sublist if item]))
            _user_list = [user for user in DATABASE.get("E4:G") if user[0]]        

            for squad in _squad_list:
                placeholder = []

                for user in _user_list:
                    if squad in user:
                        placeholder.append(user[2])

                if len(placeholder) < 3:
                    continue
                
                else:
                    while len(placeholder) < 5:
                        placeholder.append(None)

                    if discord.utils.get(guild.channels, name=f"{squad.lower()}-squad") is not None:
                        async with db.cursor() as cursor:
                            await cursor.execute('''SELECT mem1, mem2, mem3, mem4, mem5 FROM squads WHERE name = ?''', (squad,))
                            existing = await cursor.fetchone()

                            await cursor.execute('''INSERT INTO squads (name, role, channel, mem1, mem2, mem3, mem4, mem5) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                                ON CONFLICT(name) DO
                                                UPDATE SET mem1 = excluded.mem1, mem2 = excluded.mem2, mem3 = excluded.mem3, mem4 = excluded.mem4, mem5 = excluded.mem5
                                                ''', (squad, None, None, placeholder[0], placeholder[1], placeholder[2], placeholder[3], placeholder[4]))
                        
                            await db.commit()
                            await cursor.close()

                        squad_role = discord.utils.get(guild.roles, name=f"{squad} Squad")

                        try:
                            for id in existing:
                                if str(id) not in placeholder and id is not None:
                                    print(f"ID NOT FOUND: {id} - {guild.get_member(int(id)).display_name}\n")
                                    await guild.get_member(int(id)).remove_roles(squad_role)
                        
                        except ValueError as e:
                            print(f'{e.__class__.__name__}: {e}')
                            pass
                    
                    else:
                        squad_role = await guild.create_role(name=f"{squad} Squad")
                        cat = discord.utils.get(guild.categories, id=1164281181529985044)
                        overwrites = {
                            guild.default_role: discord.PermissionOverwrite(view_channel=False, read_messages=False),
                            squad_role: discord.PermissionOverwrite(view_channel=True, read_messages=True),
                            guild.get_role(842312625735860255): discord.PermissionOverwrite(view_channel=True, read_messages=True),
                            guild.get_role(333432981605580800): discord.PermissionOverwrite(view_channel=True, read_messages=True, manage_channels=True),
                        }
                        squad_ch = await cat.create_text_channel(name=f"{squad} Squad", overwrites=overwrites)
                        await squad_ch.send(f"# {squad}'s Communication Frequency\n### FREQUENCY HASH CODE #03-{random.randint(1,999)}-{random.randint(1000,9999)}\n\n<@&{squad_role.id}> - Welcome to your communications hub, a channel frequency provided to you by the 03 Commando Battalion. This is where you'll communicate amongst yourselves.\n\nThis frequency will be scrambled after:\n- **Two weeks of message inactivity + having less than 3 squad members.**\n- **Dropping to 0 squad members.**\n\n**If you have questions, please contact an <@&842312625735860255>+.**")

                        async with db.cursor() as cursor:
                            await cursor.execute('''INSERT INTO squads (name, role, channel, mem1, mem2, mem3, mem4, mem5) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                                                ON CONFLICT(name) DO
                                                UPDATE SET name = excluded.name, role = excluded.role, channel = excluded.channel, mem1 = excluded.mem1, mem2 = excluded.mem2, mem3 = excluded.mem3, mem4 = excluded.mem4, mem5 = excluded.mem5
                                                ''', (squad, squad_role.id, squad_ch.id, placeholder[0], placeholder[1], placeholder[2], placeholder[3], placeholder[4]))  

                            await db.commit()
                            await cursor.close()

                    for id in placeholder:
                        if id is not None:
                            try:
                                await guild.get_member(int(id)).add_roles(squad_role)
                            except:
                                pass

            await db.commit()
            await db.close()

            await self.squad_checker(guild)

        async def squad_checker(self, guild: discord.Guild) -> None:
            db = await aiosqlite.connect('rcb.db')
            _active_squad_list = list(set([item for sublist in DATABASE.get("E4:E") for item in sublist if item]))
            _deleted = []

            async with db.cursor() as cursor:
                await cursor.execute('''SELECT * FROM squads''')
                _old_squad_list = await cursor.fetchall()

                await cursor.close()

            for squad in _old_squad_list:
                role = guild.get_role(int(squad[1]))
                channel = guild.get_channel(int(squad[2]))

                if squad[0] not in _active_squad_list:
                    try:
                        await role.delete(reason="Squad is empty.")
                    
                    except: pass
                    try:
                        await channel.delete(reason="Squad is empty.")
                        _deleted.append(squad[0])
                    
                    except: pass

                    async with db.cursor() as cursor:
                            await cursor.execute('''DELETE FROM squads WHERE name = ?''', (squad[0],))
                            await db.commit()             
                
                else:
                    async for message in channel.history(limit=1):
                        date = message.created_at
                        today = datetime.datetime.now(datetime.timezone.utc)
                        delta = today - date

                    if int(delta.days) >= 14:
                        member_count = squad.count(None)

                        if member_count <= 2:
                            await channel.delete(reason="2 Week+ Inactivity -2 Members.")
                            await role.delete(reason="2 Week+ Inactivity -2 Members.")
                            _deleted.append(squad[0])

                            async with db.cursor() as cursor:
                                    await cursor.execute('''DELETE FROM squads WHERE name = ?''', (squad[0],))
                                    await db.commit()
            
            sgm_channel = guild.get_channel(946095177695653988)
            if len(_deleted) == 0:
                pass
            else:
                await sgm_channel.send(content=f"# Channel Purge\n\nThe following channels were purged either for inactivity or zero memebers:\n\n {', '.join(_deleted)}\n\n**If this was a mistake, please ping Officer+.**")
            await db.close()