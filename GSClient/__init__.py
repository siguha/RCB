import gspread

# Authorizing our client with the service account
SERVICE_ACCOUNT = gspread.service_account(filename='service_account.json')

# Opening the spreadsheets
OFFICER_SHEET = SERVICE_ACCOUNT.open_by_url('https://docs.google.com/spreadsheets/d/1k4p4lUivqTXYhWeQ8a3AwevV_SsJwokNjqSooLQ9q0k/')
PUBLIC_SHEET = SERVICE_ACCOUNT.open_by_url('https://docs.google.com/spreadsheets/d/1PBPZOHxNSw9hzSErpFxQ6E_OtyNKTptTK7M6BmG3-J8/')
AAR_SHEET = SERVICE_ACCOUNT.open_by_url('https://docs.google.com/spreadsheets/d/1dQso9v7GN4yXE5MsiTeS4tJdHQZKbR77ZXymM-wJUPg/')

# Getting individual sheets
ROSTER = PUBLIC_SHEET.worksheet('Roster')
DATABASE = OFFICER_SHEET.worksheet('Officer View')
AARS = AAR_SHEET.worksheet('AAR Logs')
TRYOUTS = PUBLIC_SHEET.worksheet('Tryouts')
LOAS = PUBLIC_SHEET.worksheet('LOA / ROA')
SQUADS = PUBLIC_SHEET.worksheet('Lore Squads')
POPULATION = OFFICER_SHEET.worksheet('Population')
IDS = OFFICER_SHEET.worksheet('IDs')