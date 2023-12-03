import discord
import aiosqlite
import asyncio
import re
from discord.ext import commands, tasks
from discord import app_command

from utilities.sheetutils import SheetUtilities

class Squads(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client
        self.utils = SheetUtilities.SquadUtils()
        self.client.loop.create_task(self.background(self.client))

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()
        self.squad_check.start()


    @commands.hybrid_command(name = "sc", with_app_command = False)
    async def squad_check_cmd(self, ctx: commands.Context):
        """Loads a module."""
        await self.utils.squad_builder(ctx.guild)

    @tasks.loop(hours = 12)
    async def squad_check(self) -> None:
        guild = self.client.get_guild(333429464752979978)
        await self.utils.squad_builder(guild)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Squads(client))