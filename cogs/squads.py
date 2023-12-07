import discord
import aiosqlite
import asyncio
import re
from utilities.exceptions import Exceptions
from discord.ext import commands, tasks
from discord import ui, app_commands

from utilities.sheetutils import SheetUtilities

class Squads(commands.GroupCog, name = "squad", description = "Squad Commandset."):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.utils = SheetUtilities.SquadUtils()
        self.client.loop.create_task(self.background(self.client))

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()
        self.squad_check.start()

    @app_commands.command(name='rename', description='Forcefully rename a squad.')
    @app_commands.checks.has_any_role(842312625735860255, 333432981605580800, 452534405874057217)
    async def rename(self, interaction: discord.Interaction, squad: str, name: str):
        try:
            await self.utils.squad_rename(interaction.guild, squad, name)
            await interaction.response.send_message(content=f"**{squad}** has been renamed to **{name}**.")

        except Exceptions.SquadNotFound as e: 
            await interaction.response.send_message(content=f'{e.__class__.__name__}: {e}', delete_after=10, ephemeral=True)

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