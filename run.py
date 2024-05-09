import discord
import importlib
import sys
# import os

from discord.ext import commands
from GSClient import GSClient
from GSClient.Profiles.operations import ProfileOperations
from GSClient.AAR.operations import AAROperations
from GSClient.utilities import SheetUtilities
from GSClient.Squads.operations import SquadOperations
from GSClient.LOAs.operations import LOAOperations

# from cogs.form

from discord import ui
from discord.ui import View, Select, Button, UserSelect

class AZI(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='nt!',
            intents=discord.Intents.all(),
            owner_id=484932458538860544
        )

        # Intilaizing the GSClient
        self.gs_client = GSClient()
        
        # Initializing our database connection to all of our subpackages.
        self.profile_ops = None
        self.aar_ops = None
        self.squad_ops = None
        self.loa_ops = None

        self.__initial_extensions = [
            'cogs.forms.aar',
            'cogs.forms.tickets',
            'cogs.forms.loa',
            'cogs.users.squads',
            'cogs.users.profile',
            'cogs.users.officers'
        ]

    async def setup_hook(self):
        # Setting up our database connection
        await self.gs_client.async_init()
        
        self.aar_ops = AAROperations(self.gs_client.database)
        self.profile_ops = ProfileOperations(self.gs_client.database)
        self.squad_ops = SquadOperations(self.gs_client.database)
        self.loa_ops = LOAOperations(self.gs_client.database)

        # Loading cog extensions
        for extension in self.__initial_extensions:
            await self.load_extension(extension)

    async def on_ready(self):
        print(f'Logged in as {self.user} ({self.user.id})')

        await client.change_presence(activity=discord.Game(name='v3 - BB ON TOP 💯'))

    async def close(self):
        await self.gs_client.teardown()
        await super().close()
    
client = AZI()

@client.command()
async def sync(ctx):
    if ctx.author.id == client.owner_id:
        await client.tree.sync()
        await ctx.send('[**Admin**] Synced the tree.')

    else:
        await ctx.message.delete()

@client.command()
async def load_cog(ctx, cog: str):
    if ctx.author.id == client.owner_id:
        try:
            await client.load_extension(cog)
            await ctx.send(f"[**Admin**] Loaded cog `{cog}`.")

        except commands.ExtensionError as e:
            await ctx.send(f'[**{e.__class__.__name__}**]: {e}')

    else:
        await ctx.message.delete()

@client.command()
async def reload_cog(ctx, cog: str):
    if ctx.author.id == client.owner_id:
        try:
            await client.reload_extension(cog)
            await ctx.send(f"[**Admin**] Reloaded cog `{cog}`.")

        except commands.ExtensionError as e:
            await ctx.send(f'[**{e.__class__.__name__}**]: {e}')

    else:
        await ctx.message.delete()

@client.command()
async def reload_extension(ctx, extension: str):
    if ctx.author.id == client.owner_id:
        try:
            importlib.reload(sys.modules[extension])
            await ctx.send(f"[**Admin**] Reloaded extension `{extension}`.")

        except commands.ExtensionError:
            await ctx.send(f'[**FailedToLoad**]: failed to load `{extension}`.')

        except KeyError:
            await ctx.send(f'[**KeyError**]: `{extension}` not found in sys.modules.')

    else:
        await ctx.message.delete()

client.run(token="MTA3NTE2NzU4NzIyMDA3NDU2Ng.GdMwRz.wj4zg1xAyEKKOLEYwBm2MzEhVDut6AKm4EHBsM")