import discord
import aiosqlite
import asyncio
from datetime import datetime
import re
from discord.ext import commands
from discord import app_commands, ui
from utilities.exceptions import Exceptions
from utilities.sheetutils import SheetUtilities

# Still need to set up time-based tasks to check for expiring LOAs.

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
        self.fields = [
            'Start',
            'End',
            'Type'
        ]

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()
        global LOA_CH 
        guild = client.get_guild(333429464752979978)
        LOA_CH = guild.get_channel(338196204234211339)

    @app_commands.command(name = "request", description = "Request an absence.")
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

    @app_commands.command(name="end", description="End an absence.")
    async def loa_end(self, interaction: discord.Interaction, user: discord.Member = None):
        if user is None:
            user = interaction.user

        try:
            await UTILS.loa_end(user=user.id)
        
        except (e.UserNotFound, e.LOAExisting, e.LOANotFound) as error:
            await interaction.response.send_message(f"{error.__class__.__name__}: {error}", ephemeral=True, delete_after=15)
            return 1

        else:
            embed = discord.Embed(title = "Notice of Return", description=f"{user.mention} has returned to station. Welcome back, commando.", colour = discord.Colour.red(), timestamp = datetime.now())
            embed.set_author(name = "Unit Logistics", icon_url="https://i.imgur.com/3gTO5ie.png")
            await LOA_CH.send(embed = embed)
            await interaction.response.send_message("Absence successfully ended.", ephemeral=True, delete_after=15)

    @app_commands.command(name='edit', description='Edit an existing absence.')
    async def loa_edit(self, interaction: discord.Interaction, field: str, edit: str, user: discord.Member = None):
        if user is None:
            user = interaction.user
        
        try:
            old = await UTILS.loa_fetch(user=user.id)

        except (e.UserNotFound, e.LOANotFound) as error:
            await interaction.response.send_message(f"{error.__class__.__name__}: {error}", ephemeral=True, delete_after=15)
            return 1

        else:
            embed = discord.Embed(title = "Absence Update Request", colour = discord.Colour.dark_red(), timestamp=datetime.now())
            embed.set_footer(text = "Awaiting response...")
            embed.set_author(name = "Unit Logistics", icon_url="https://i.imgur.com/3gTO5ie.png")
            embed.add_field(name = "Requested By", value = user.display_name, inline = False)
            embed.add_field(name = "Requester ID", value = str(user.id), inline = False)
            embed.add_field(name = "Edit Type", value = field, inline = False)
            # embed.add_field(name = "\u200b", value = '\u200b', inline = False)
            if field == 'Start':
                embed.add_field(name = "Old Start Date", value = old['start'], inline = True)
                embed.add_field(name = "New Start Date", value = edit, inline = True)
            elif field == 'End':
                embed.add_field(name = "Old End Date", value = old['end'], inline = True)
                embed.add_field(name = "New End Date", value = edit, inline = True)
            elif field == 'Type':
                embed.add_field(name = "Old Type", value = old['type'], inline = True)
                embed.add_field(name = "New Type", value = edit, inline = True)        
            await LOA_CH.send(embed = embed, view = Views.RequestButtons())
            await interaction.response.send_message(content="Absence update request submitted.", ephemeral=True, delete_after=15)

    @loa_request.autocomplete('type')
    async def loa_request_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name = type, value = type)
            for type in self.types if current.lower() in type.lower()
        ]

    @loa_edit.autocomplete('field')
    async def loa_edit_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name = field, value = field)
            for field in self.fields if current.lower() in field.lower()
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
            
            if embed.title == "Request for Absence":
                try:
                    await UTILS.loa_add(name=fields[0].value, user_id=fields[1].value, start_date=fields[2].value, end_date=fields[3].value, type=fields[4].value, reason=fields[5].value)

                except e.UserNotFound as error:
                    await interaction.message.delete(delay = 15)
                    await interaction.followup.send(content = f"{error.__class__.__name__}: {error} - Deleting AAR request in 15 seconds.", ephemeral = True)
                    return 1
                
                else:
                    embed.set_footer(text = f"Request Accepted by {interaction.user.display_name}.")
                    await interaction.message.edit(embed = embed, view = None)
                    await interaction.followup.send("Request successfully accepted.", ephemeral = True)

            else:
                try:
                    await UTILS.loa_edit(user=fields[1].value, field=fields[2].value, edit=fields[5].value)
                
                except e.LOANotFound as error:
                    await interaction.message.delete(delay = 15)
                    await interaction.followup.send(content = f"{error.__class__.__name__}: {error} - Deleting AAR request in 15 seconds.", ephemeral = True)
                    return 1
                
                else:
                    embed.set_footer(text = f"Request Accepted by {interaction.user.display_name}.")
                    await interaction.message.edit(embed = embed, view = None)
                    await interaction.followup.send("Request successfully accepted.", ephemeral = True)

        @discord.ui.button(label = "Deny (SGM+)", style = discord.ButtonStyle.danger, disabled = False, custom_id = 'persistent:DenyRequest')
        @app_commands.checks.has_any_role(842312625735860255)
        async def request_deny(self, interaction: discord.Interaction, button: ui.Button):
            embed = interaction.message.embeds[0]
            embed.set_footer(text = f"Request Denied by {interaction.user.display_name}.")
            await interaction.message.edit(embed = embed, view = None)
            await interaction.response.send_message("Request successfully denied.", ephemeral = True)

    class ReturnButtons(ui.View):
        def __init__(self):
            super().__init__(timeout = None)
        
        @discord.ui.button(label = "Return", style = discord.ButtonStyle.success, disabled = False, custom_id = 'persistent:ReturnButton')
        async def return_button(self, interaction: discord.Interaction, button: ui.Button):
            await interaction.response.defer()
            embed = interaction.message.embeds[0]
            fields = embed.fields
            
            if interaction.user.id == fields[1].value:
                embed = discord.Embed(title = "Notice of Return", description=f"{interaction.user.mention} has returned to station. Welcome back, commando.", colour = discord.Colour.red(), timestamp = datetime.now())
                embed.set_author(name = "Unit Logistics", icon_url="https://i.imgur.com/3gTO5ie.png")
                await LOA_CH.send(embed = embed)
                await interaction.response.send_message("Return recorded. Welcome back.", ephemeral=True, delete_after=15)

            else:
                await interaction.response.send_message("This is not your absence.", ephemeral=True, delete_after=15)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(LOAs(client))