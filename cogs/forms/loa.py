import discord
import aiosqlite
import asyncio
from datetime import datetime
import re
from discord.ext import commands
from discord import app_commands, ui
from discord.interactions import Interaction
from utilities.exceptions import Exceptions
from utilities.sheetutils import SheetUtilities

e = Exceptions()
UTILS = SheetUtilities.LOAUtils()

class LOAs(commands.GroupCog, name = "loa", description = "LOA commandset."):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client
        self.client.loop.create_task(self.background(self.client))
        self.utils = SheetUtilities.ProfileUtils()
        self.e = Exceptions()

        self.types = [
            'LOA',
            'ROA'
        ]

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()
        global LOA_CH 
        guild = client.get_guild(333429464752979978)
        LOA_CH = guild.get_channel(338196204234211339)

    @app_commands.command(name = "request", description = "Request an LOA.")
    async def loa_request(self, interaction: discord.Interaction, type: str, user: discord.Member = None) -> None:
        if type not in self.types: 
            await interaction.response.send_message(f"Invalid absence type- use the autocomplete options.", ephemeral = True, delete_after = 15)
        
        else:
            if user is None:
                user = interaction.user

            modal = Modals.RequestModal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            vals = modal.vals

            embed = discord.Embed(title = 'Request for Absence', colour = discord.Colour.red())
            embed.set_author(name = user.display_name, icon_url = user.display_avatar)
            embed.set_footer(text = "Awaiting response...")
            embed.add_field(name = "Requested By", value = user.display_name, inline = False)
            embed.add_field(name = "Requester ID", value = str(user.id), inline = False)
            embed.add_field(name = "Start Date", value = vals['START'], inline = True)
            embed.add_field(name = "End Date", value = vals['END'], inline = True)
            embed.add_field(name = "Type", value = type, inline = False)
            embed.add_field(name = "Reason", value = vals['REASON'], inline = False)

            await interaction.followup.send(embed = embed, view = Views.RequestButtons())

    @loa_request.autocomplete('type')
    async def loa_request_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name = type, value = type)
            for type in self.types if current.lower() in type.lower()
        ]

class Modals:
    class RequestModal(ui.Modal, title = 'LOA Request Form'):
        def __init__(self):
            super().__init__()
            self.custom_id = 'id:RequestModal'
            self.vals = {}

        start = ui.TextInput(label = "Start Date - (MM-DD-YY)", style = discord.TextStyle.short, placeholder = "Start Date", default = datetime.now().strftime("%m-%d-%y"), required = True, max_length = 8)
        end = ui.TextInput(label = "End Date - (MM-DD-YY)", style = discord.TextStyle.short, placeholder = "End Date", default = "", required = True, max_length = 8)
        reason = ui.TextInput(label = "Reason for your Depature", style = discord.TextStyle.short, placeholder = "If private, please notify an Officer+.", default = "Private (Contact Officer+)", required = True, max_length = 4000)
    
        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral = True)
            self.start.value
            self.vals['START'] = self.start.value
            self.vals['END'] = self.end.value
            self.vals['REASON'] = self.reason.value
            self.stop()

class Views:
    class RequestButtons(ui.View):
        def __init__(self):
            super().__init__(timeout = None)
        
        @discord.ui.button(label = "Approve (SGM+)", style = discord.ButtonStyle.success, disabled = False, custom_id = 'persistent:ApproveRequest')
        @app_commands.checks.has_any_role(842312625735860255)
        async def request_approve(self, interaction: discord.Interaction, button: ui.Button):
            await interaction.response.defer()
            embed = interaction.message.embeds[0]
            fields = embed.fields
                    
            try:
                await UTILS.loa_add(name=fields[0].value, user_id=fields[1].value, start_date=fields[2].value, end_date=fields[3].value, type=fields[4].value, reason=fields[5].value)

            except e.UserNotFound as error:
                await interaction.message.delete(delay = 15)
                await interaction.followup.send(content = f"{error.__class__.__name__}: {error} - Deleting AAR request in 15 seconds.", ephemeral = True)
                return 1
            
            else:
                embed.set_footer(text = f"Request Accepted by {interaction.user.display_name}.")
                await interaction.message.edit(embed = embed, view = None)
                await interaction.followup.send("AAR successfully accepted.", ephemeral = True)

        @discord.ui.button(label = "Deny (SGM+)", style = discord.ButtonStyle.danger, disabled = False, custom_id = 'persistent:DenyRequest')
        @app_commands.checks.has_any_role(842312625735860255)
        async def request_deny(self, interaction: discord.Interaction, button: ui.Button):
            embed = interaction.message.embeds[0]
            embed.set_footer(text = f"Request Denied by {interaction.user.display_name}.")
            await interaction.message.edit(embed = embed, view = None)
            await interaction.response.send_message("AAR successfully denied.", ephemeral = True)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(LOAs(client))