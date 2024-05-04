import discord

from discord.ext import commands, tasks
from discord import ui, app_commands

restricted_numbers = [
    40,
    90,
    91,
    2,
    22,
    42,
    62,
    82,
    92,
    13,
    23,
    33,
    93,
    15,
    16,
    36,
    46,
    86,
    7,
    37,
    38,
    68,
    9,
    29,
    39,
    69,
]

class Squads(commands.GroupCog, name='squad', description='Squdas Commandset.'):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.profile_ops = self.client.profile_ops

        self.client.loop.create_task(self.background(self.client))

    async def background(self, client: commands.Bot):
        ...

    @app_commands.command(name='rename', description='Forcefully rename a squad.')
    async def squad_rename(self, interaction: discord.Interaction, squad: str, name: str, color: str = None):
        # 56

        ...