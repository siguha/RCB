import gspread

from GSClient import LOAS, utilities

class LOAOperations:
    def __init__(self, database_manager):
        self.db = database_manager
        self.conversions = {
            'Start' : 5,
            'End' : 6,
            'Type' : 8
        }

    async def loa_add(self, *, name: str, user_id: int, start_date: str, end_date: str, type: str, reason: str):
        last_row = await utilities.SheetUtilities.get_last_row(LOAS, 3)
        steamid = await utilities.SheetUtilities.get_user_id(user_id)
        if LOAS.find(steamid) is not None:
            raise ValueError(f"User {steamid} has an existing LOA.")
        
        LOAS.append_row([name, steamid, start_date, end_date, None, type, None, reason, '0', str(user_id)], value_input_option = 'USER_ENTERED', insert_data_option = 'OVERWRITE', table_range = f'C{last_row}:J{last_row}')

    async def loa_end(self, *, user: int) -> bool:
        steamid = await self.utils.id_fetch(user)
        loc = LOAS.find(steamid)
        
        if loc is None:
            raise ValueError(f"LOA for user `{steamid}` not found.")

        else:
            LOAS.delete_row(loc.row)
    
    async def loa_edit(self, *, user: str, field: str, edit: str):
        steamid = await self.utils.id_fetch(user)
        loc = LOAS.find(steamid)

        if loc is None:
            raise ValueError(f"LOA for user `{steamid}` not found.")

        else:
            row = loc.row
            col = self.conversions[field]
            LOAS.update_cell(row, col, edit)
            LOAS.update_cell(row, 11, '0')

    async def loa_fetch(self, *, user: int):
        steamid = await self.utils.id_fetch(user)
        loc = LOAS.find(steamid)

        if loc is None:
            raise ValueError(f"LOA for user `{steamid}` not found.")

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