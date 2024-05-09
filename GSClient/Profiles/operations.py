import gspread
import datetime

from GSClient import HOME, IDS, ROSTER, DATABASE, utilities


class ProfileOperations:
    def __init__(self, database_manager):
        self.db = database_manager

    async def fetch_steamid(self, discord_id: int):
        cursor = await self.db.get_cursor()
        await cursor.execute('''SELECT steamid FROM ids WHERE did = ?''', (discord_id,))
        user = await cursor.fetchone()

        if user is not None:
            return user[0]
        else:
            raise ValueError('SteamID not found in Database. Profile not synced.')
    
    async def get_last_row(self, sheet: gspread.Worksheet, col: int=2):
        return len(sheet.col_values(col))

    async def fetch_batch_number(self):
        batch_cell = 'H12'
        batch_number = HOME.acell(batch_cell).value
        return batch_number

    async def check_if_designation_exists(self, batch, designation) -> bool:
        cursor = await self.db.get_cursor()
        await cursor.execute('''SELECT 1 FROM ids WHERE batch = ? AND designation = ?''', (batch, designation))
        result = await cursor.fetchone()

        return bool(result)
  
    async def register_user(self, discord_id: int, steam_id: str, designation: str, name: str):
        batch = await self.fetch_batch_number()
        last_row = await self.get_last_row(IDS)

        if not await self.check_if_designation_exists(batch, designation):
            cursor = await self.db.get_cursor()
            await cursor.execute('''INSERT INTO ids (did, steamid, batch, designation, name) VALUES (?, ?, ?, ?, ?)
                                ON CONFLICT (did) DO
                                UPDATE SET steamid = excluded.steamid, batch = excluded.batch, designation = excluded.designation, name = excluded.name''', (discord_id, steam_id, batch, designation, name))

            await self.db.connection.commit()

            existing = IDS.find(steam_id)

            full_designation = f'{batch}{"{:02d}".format(designation)}'

            if existing is None:
                IDS.batch_update([{
                    'range' : f'A{last_row}:D{last_row}',
                    'values' : [[name, steam_id, str(discord_id), full_designation]],
                }], value_input_option = 'RAW')

            else:
                IDS.batch_update([{
                    'range' : f'A{existing.row}:D{existing.row}',
                    'values' : [[name, steam_id, str(discord_id), full_designation]],
                }], value_input_option = 'RAW')
    
            return full_designation

        else:
            raise ValueError("Batch and designation combination already exists.")

    async def profile_fetch(self, did: int) -> dict[str]:
        steamid = await self.fetch_steamid(did)
        cell_public = ROSTER.find(steamid, in_column=5)
        cell_officer = DATABASE.find(steamid, in_column=7)

        if cell_public is None or cell_officer is None:
            raise ValueError("User not found in roster. Possibly resetting, or they don't exist.")
        
        else:
            specilization_status = ROSTER.get(f"Q{cell_public.row}:Y{cell_public.row}")
            player_information = DATABASE.row_values(cell_officer.row)

            data = {
                'RANK' : player_information[1],
                'NAME' : player_information[2],
                'DESIGNATION' : player_information[3],
                'CLASS' : player_information[4] if player_information[4] != "" else player_information[4] if player_information[4] != "" else "Not Assigned.",
                'ATTACHMENT' : player_information[5],
                'STEAMID' : player_information[6],
                'JOINED' : player_information[8],
                'DAYS_IN' : player_information[9],
                'LAST_SEEN' : player_information[10],
                'LAST_SEEN_DAYS' : player_information[11],
                'DAYS_SINCE' : player_information[11],
                'LAST_AAR' : player_information[12],
                'LAST_AAR_DAYS' : player_information[13],
                'PROMO_DATE' : player_information[14],
                'PROMO_DAYS' : player_information[15],
                'DEMO' : 'Trainer+' if specilization_status[0][1] == 'a' else 'Certified' if specilization_status[0][1] == 'b' else 'Trainee' if specilization_status[0][1] == 'c' else 'Untrained',
                'ENGINEER' : 'Trainer+' if specilization_status[0][3] == 'a' else 'Certified' if specilization_status[0][3] == 'b' else 'Trainee' if specilization_status[0][3] == 'c' else 'Untrained',
                'MEDIC' : 'Trainer+' if specilization_status[0][5] == 'a' else 'Certified' if specilization_status[0][5] == 'b' else 'Trainee' if specilization_status[0][5] == 'c' else 'Untrained',
                'SNIPER' : 'Trainer+' if specilization_status[0][7] == 'a' else 'Certified' if specilization_status[0][7] == 'b' else 'Trainee' if specilization_status[0][7] == 'c' else 'Untrained',
                'LOGS' : player_information[22],
                'PARTICIPATED' : player_information[23],
                'TRYOUTS' : player_information[24],
                'TRAININGS' : player_information[25],
                'COHOSTS' : player_information[26],
                'LEADS' : player_information[27],
                'SGT_TRIALS' : player_information[28],
                'BT_TRIALS' : player_information[29],
                'LOA' : player_information[32],
                'BT' : "Completed" if player_information[18] == "TRUE" else "Uncompleted",
                'SLT' :"Completed" if player_information[20] == "TRUE" else "Uncompleted",
                'RDT' : "Completed" if player_information[21] == "TRUE" else "Uncompleted",                
            }

            return data

    async def stats_fetch(self, did: int) -> dict[str]:
        row = DATABASE.find(str(did))

        if row is None:
            raise ValueError('User not found in Officer Database.')
        
        else:
            vals = DATABASE.row_values(row.row)
            data = {
                'PROMO_DATE' : vals[14],
                'PROMO_DAYS' : vals[15],
                'LOGS' : vals[22],
                'PARTICIPATED' : vals[23],
                'TRYOUTS' : vals[24],
                'TRAININGS' : vals[25],
                'COHOSTS' : vals[26],
                'LEADS' : vals[27],
                'SGT_TRIALS' : vals[28],
                'BT_TRIALS' : vals[29],
                'LAST_AAR' : vals[12],
                'LAST_AAR_DAYS' : vals[13],
                'LAST_SEEN' : vals[10],
                'LAST_SEEN_DAYS' : vals[11],
                'LOA' : vals[32],
                'BT' : vals[18],
                'SLT' : vals[20],
                'RDT' : vals[21],
            }

            return data
        
    async def vote_user(self, did: int):
        loc = DATABASE.find(str(did))

        if loc is None:
            raise ValueError(f'DiscordID {did} not found in Officer Database.')

        else:
            user_row = loc.row
            vote_col = 31
            DATABASE.update_cell(user_row, vote_col, datetime.datetime.now().strftime('%m/%d/%Y'))

    async def warn_user(self, did: int):
        loc = DATABASE.find(str(did))

        if loc is None:
            raise ValueError(f'DiscordID {did} not found in Officer Database.')

        else:
            row = loc.row
            col = 17
            DATABASE.update_cell(row, col, 'TRUE')

    async def enlisted_promos(self) -> list[str]:
        vote_strings = []
        ready_vote_cells = DATABASE.findall("Yes", in_column=33)

        if ready_vote_cells:
            ready_vote_rows = [DATABASE.row_values(cell.row) for cell in ready_vote_cells]

            for row in ready_vote_rows:
                if row[1] == "PVT":
                    vote_strings.append(f"**{row[2]}** for **PFC**.")

                else:
                    continue

        return vote_strings

    async def cert_user(self, did: int, cert: str):
        column_locations = {
            "BT": 20,
            "SLT": 'U',
            "RDT": 'V',
        }

        date_of_completion = datetime.datetime.now().strftime('%m/%d/%Y')

        user_location = DATABASE.find(str(did), in_column=7)
        if user_location:
            if cert == "BT":
                DATABASE.batch_update([{
                    'range': f'S{user_location.row}:T{user_location.row}',
                    'values': [['TRUE', date_of_completion]],
                }], value_input_option = 'USER_ENTERED')
            
            else:
                DATABASE.update(f'{column_locations[cert]}{user_location.row}', 'TRUE', value_input_option = 'USER_ENTERED')

        else:
            raise ValueError("User ID not found in database.")