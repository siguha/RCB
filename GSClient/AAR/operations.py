import datetime

from GSClient import AARS, TRYOUTS, utilities

class AAROperations:
    def __init__(self, database_manager):
        self.db = database_manager

    async def save_aar_to_sheet(self, *args, msg_id: int, log_id: int, log: str, logger_id: int, users: list[int] = None):
        await self.create_aar(log_id, msg_id)
        date = datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
        AARS.insert_row(values = [date, str(log_id), log, str(logger_id)], value_input_option = 'USER_ENTERED', index = 3)   
        
        if log == 'Lead' or log == "Lead Spectate" or log == "Advisor Spectate":
            AARS.append_row(values = [str(args[4]), args[0], args[1], args[2], args[3]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'E3:I3')

        elif log == 'Training':
            AARS.append_row(values = [args[0], args[1], args[2], args[3], args[4]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'J3:N3')
        
        elif log == 'Lore Activity':
            AARS.append_row(values = [args[0], args[1], args[2]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'O3:Q3')

        elif log == 'BT':
            AARS.append_row(values = [args[0], args[1], args[2]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'R3:T3')               

        elif log == 'SGT Trials':
            AARS.append_row(values = [args[0], args[1], args[2]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'U3:W3')

        elif log == 'Spec Cert':
            AARS.append_row(values = [args[0], args[1], args[2]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'X3:Z3')

        elif log == 'Tryout':
            last_row = await utilities.SheetUtilities.get_last_row(TRYOUTS)
            date = datetime.datetime.now().strftime("%m/%d/%Y")
            AARS.append_row(values = [args[1], args[2], args[3]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = 'AA3:AC3')
            TRYOUTS.append_row(values = [date, args[0], args[3], args[4], args[1], args[2]], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = f'B{int(last_row)}:G{int(last_row)}')

        if users is not None:
            col = 30
            for user in users:
                AARS.update_cell(3, col, str(user))
                col += 1

    async def aar_append(self, log_id: int, members: list[str]):
        loc = AARS.find(str(log_id).zfill(14))

        if loc is None:
            raise e.LogNotFound(f'LogID `{log_id}` not found in AAR sheet.')
        else:
            row = loc.row
            length = len(AARS.row_values(row))
            col = (length + 1) if length >= 29 else 29

            for member in members:
                AARS.update_cell(row, col, member)
                col += 1

    async def create_aar(self, log_id: int, msg_id: int):
        async with await self.db.get_cursor() as cursor:
            await cursor.execute('''INSERT INTO AARS (log_id, msg_id) VALUES (?, ?)''', (log_id, msg_id))
        
        await self.db.connection.commit()
    
    async def remove_aar(self, log_id: int):
        async with await self.db.get_cursor() as cursor:
            await cursor.execute('''DELETE FROM AARS WHERE log_id = ?''', (log_id,))
        
        await self.db.connection.commit()

        log_location = AARS.find(str(log_id).zfill(14))

        try: 
            AARS.delete_row(log_location.row)
        
        except AttributeError:
            raise ValueError("Log ID not found in the database.")
        
    async def fetch_aar(self, log_id: int):
        async with await self.db.get_cursor() as cursor:
            await cursor.execute('''SELECT * FROM AARS WHERE log_id = ?''', (log_id,))
            result = await cursor.fetchone()
        
        return result[0]

    async def add_member_to_aar(self, log_id: int, members: list[str]):
        log_location = AARS.find(str(log_id).zfill(14))

        if log_location is None:
            raise ValueError(f'Log not found in the database.')
        
        else:
            row = log_location.row
            length = len(AARS.row_values(row))
            col = (length + 1) if length >= 29 else 29

            for member in members:
                AARS.update_cell(row, col, member)
                col += 1

    async def pop_member_from_aar(self, log_id: int, user: int):
        log_location = AARS.find(str(log_id).zfill(14))
        row_vals = AARS.row_values(log_location.row)
        col = row_vals.index(str(user)) + 1
        AARS.update_cell(log_location.row, col, '')