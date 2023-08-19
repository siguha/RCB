import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import datetime

from utilities.sheetutils import SheetUtilities
from utilities.exceptions import Exceptions

S_UTILS = SheetUtilities()
M_UTILS = SheetUtilities.MiscUtils()

class Misc(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.squad_list = [
            'Delta',
            'Omega',
            'Bad Batch',
            'Ion',
            'Aiwha',
            'Yayax',
            'Foxtrot'
        ]
        self.spec_list = [
            'Engineer',
            'Sniper',
            'Demo',
            'Medic'
        ]
    
    @app_commands.command(name='squads', description='View a list of all lore squads.')
    async def squads(self, interaction: discord.Interaction, squad: str = None):
        await interaction.response.defer()
        if squad is None:
            pages = await M_UTILS.squad_fetch()
            view = S_UTILS.Paginator(pages)
            await interaction.followup.send(embed=view.initial, view=view)
        else:
            embed = await M_UTILS.squad_fetch(squad)
            await interaction.followup.send(embed=embed)

    # @app_commands.command(name='trainers', description='Fetch a list of trainers.')
    # async def trainers(self, interaction: discord.Interaction, spec: str = None):
    #     await M_UTILS.trainer_fetch()

    @squads.autocomplete('squad')
    async def squad_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name = squad, value = squad)
            for squad in self.squad_list if current.lower() in squad.lower()
        ]

    # @trainers.autocomplete('spec')
    # async def trainers_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    #     return [
    #         app_commands.Choice(name = spec, value = spec)
    #         for spec in self.spec_list if current.lower() in spec.lower()
    #     ]

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Misc(client))