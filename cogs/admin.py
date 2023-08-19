import discord
import aiosqlite
import asyncio
import re
from discord.ext import commands
from discord import app_commands

from utilities.sheetutils import SheetUtilities

class Admin(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client
        self.utils = SheetUtilities.ProfileUtils()
    
    @commands.hybrid_command(name = "load", with_app_command = False)
    async def load(self, ctx: commands.Context, *, module: str):
        """Loads a module."""
        try:
            await self.client.load_extension(module)

        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')

        else:
            await ctx.message.delete()
            await ctx.send('Extension successfully loaded.', delete_after = 5)

    @commands.hybrid_command(name = "unload", with_app_command = False)
    async def unload(self, ctx: commands.Context, *, module: str):
        """Unloads a module."""
        try:
            await self.client.unload_extension(module)

        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')

        else:
            await ctx.message.delete()
            await ctx.send('Extension successfully unloaded.', delete_after = 5)

    @commands.hybrid_command(name = "reload", with_app_command = False)
    async def _reload(self, ctx: commands.Context, *, module: str):
        """Reloads a module."""
        try:
            await self.client.reload_extension(module)

        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')

        else:
            await ctx.message.delete()
            await ctx.send('Extension successfully reloaded.', delete_after = 5)

    @commands.hybrid_command(name = "sync", with_app_command = False)
    async def reload(self, ctx: commands.Context):
        await self.client.tree.sync()
        await ctx.message.delete()
        await ctx.send('Command tree re-synced.', delete_after = 5)

    @commands.hybrid_command(name="jax", with_app_command=False)
    async def jax(self, ctx: commands.Context):
        # if ctx.author.id not in [395265117497065473, 484932458538860544]:
        await ctx.message.delete()
        await ctx.channel.send("https://tenor.com/view/star-wars-yeet-darth-vader-fallen-order-jedi-gif-24487821")
       
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Admin(client))