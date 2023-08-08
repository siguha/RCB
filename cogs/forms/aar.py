"""
Tryout Logs go to the Roster automatically.

Update embeds with additional AAR information.

Add a logging type - Spectated events (Logs into S1 Main, host will be the NCO+, will also take lead, roles, and include a summary section.)

Make ID posting more accurate (for some reason sometimes they're missing digits? Might be google side)

Support mort edit complexity with removing people from participants, changing different fields, changing host, etc.

Figure out why modals don't isolate?
- add_item or modal.wait()
"""

import discord
from discord import ui, app_commands
from discord.interactions import Interaction
from discord.ui import UserSelect
from discord.ext import commands
import gspread
from datetime import datetime

class AARs(commands.groupCog, name = "aar", description = "AAR Commandset."):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.types = [ 
            'Lead',
            'Lead Spectate',
            'Training',
            'Lore Activities',
            'Basic Training',
            'SGT Trials',
            'Spec Certs',
            'Tryout',
        ]

    @app_commands.command(name = 'log', description = 'Log an AAR.')
    async def aar_log(self, interaction: discord.Interaction, type: str, host: discord.Member = None) -> None:
        if type not in self.types:
            await interaction.response.send_message(content = f'Type *{type}* does not exist. Try again.', ephemeral = True, delete_after = 5)
        else:
            if host is None:
                host = interaction.user
            if type == 'Tryout':
                ...
            elif type == 'Basic Training':
                ...
            elif type == 'SGT Trials':
                ...
            elif type == 'Spec Cert':
                ...
            else:
                ...
    
    @aar_log.autocomplete('type')
    async def aar_log_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name = type, value = type)
            for type in self.types if current.lower() in type.lower()
        ]
    
class Views:
    ...

class Modals:
    ...