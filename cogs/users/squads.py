import discord

from discord.ext import commands, tasks
from discord import ui, app_commands

class SquadCommands(commands.GroupCog, name='squad', description='Squdas Commandset.'):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.squad_ops = self.client.squad_ops

        self.client.loop.create_task(self.background(self.client))

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()
        self.squads_check.start()

    @app_commands.command(name='rename', description='Forcefully rename a squad.')
    @app_commands.checks.has_any_role(842312625735860255, 333432981605580800, 452534405874057217)
    async def squads_rename(self, interaction: discord.Interaction, squad: str, name: str, color: str = None):
        try:
            await self.squad_ops.squad_rename(interaction.guild, squad, name, color, "yes" if color is not None else "no")
            await interaction.response.send_message(content=f'**{squad}** has been renamed to **{name}**.')

        except Exception as e:
            await interaction.response.send_message(content=f'{e.__class__.__name__}: {e}', delete_after=10, ephemeral=True)

    @app_commands.command(name="stick", description="Stick a squad for legacy purposes.")
    @app_commands.checks.has_any_role(842312625735860255, 333432981605580800, 452534405874057217)
    async def squads_stick(self, interaction: discord.Interaction, squad: str):
        try:
            await self.squad_ops.squad_stick(squad=squad)
            await interaction.response.send_message(content=f"**{squad}** has been stuck.")

        except Exception as e: 
            await interaction.response.send_message(content=f'{e.__class__.__name__}: {e}', delete_after=10, ephemeral=True)

    @tasks.loop(minutes=10)
    async def squads_check(self) -> None:
        guild = self.client.get_guild(333429464752979978)
        await self.squad_ops.squad_builder(guild)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(SquadCommands(client))