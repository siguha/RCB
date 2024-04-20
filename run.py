import discord
import importlib
import sys
# import os

from discord.ext import commands
from GSClient import GSClient
# from cogs.form

class AZI(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.all(),
            owner_id=484932458538860544
        )

        # Intilaizing the GSClient
        self.gs_client = GSClient()

        self.__initial_extensions = []

    async def setup_hook(self):
        # Setting up our database connection
        await self.gs_client.setup()

        # Loading cog extensions
        for extension in self.__initial_extensions:
            self.load_extension(extension)

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

client.run()