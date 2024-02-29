import discord
from discord import ui, app_commands
from discord.ui import UserSelect
from discord.ext import commands
from utilities.sheetutils import SheetUtilities
from utilities.exceptions import Exceptions
from datetime import datetime

UTILS = SheetUtilities.AarUtils()
e = Exceptions()

class Events(commands.GroupCog, name = "event", description = "Events Commandset."):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.client.loop.create_task(self.background(self.client))

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()
        global CH_LINK 
        guild = client.get_guild(333429464752979978)
        CH_LINK = guild.get_channel(1192859840935104714)

    @app_commands.command(name="submit", description="Submit an event idea.")
    async def event_submit(self, interaction: discord.Interaction, title: str):
        modal = StorylineModal()
        await interaction.response.send_modal(modal)
        await modal.wait()
        
        embed = discord.Embed(title="Event Submission", timestamp=datetime.now(), color=discord.Colour.random())
        if len(modal.vals['STORY']) >= 1024:
            embed.add_field(name="Event Summary (1)", value=modal.vals['STORY'][0:1024], inline=False)
            embed.add_field(name="Event Summary (2)", value=modal.vals['STORY'][1025:], inline=False)
        else:
            embed.add_field(name="Event Summary", value=modal.vals['STORY'], inline=False)

        if len(modal.vals['OBJ']) >= 1024:
            embed.add_field(name="Objectives (1)", value=modal.vals['OBJ'][0:1024], inline=False)
            embed.add_field(name="Objectives (2)", value=modal.vals['OBJ'][1025:], inline=False)
        else:
            embed.add_field(name="Objectives", value=modal.vals['OBJ'], inline=False)
    
        embed.add_field(name="Suggested Bans", value=modal.vals['BANS'], inline=False)
        embed.add_field(name="Author's Notes", value=modal.vals['NOTES'], inline=False)
        embed.add_field(name="Suggested Map", value=modal.vals['MAP'], inline=False)
        embed.set_author(name=interaction.user.display_name, icon_url=interaction.user.display_avatar)
        await CH_LINK.create_thread(name=f'"{title.title()}"', embed=embed, applied_tags=[CH_LINK.get_tag(1192860049991798884)])

class StorylineModal(ui.Modal, title = "Storyline Event Submission"):
    def __init__(self):
        super().__init__(timeout = None)
        self.vals = {}

    story = ui.TextInput(label = "Summarize the backstory of your event.", style = discord.TextStyle.long, placeholder = "Please keep this section to a few paragraphs maximum.", required = True, max_length = 2000)
    objectives = ui.TextInput(label = "What are the objectives of your event?", style = discord.TextStyle.short, placeholder = '"The RC will need to destroy an artillery and vehicle depot..."', required = True, max_length = 2000)
    bans = ui.TextInput(label = "What bans would you recommend, if any?", style = discord.TextStyle.short, default="No Suggested Bans.",  required = False)
    advice = ui.TextInput(label = "Any additional advice/notes for the GM?", style = discord.TextStyle.short, default="No Suggested Notes.",  required = False)
    maps = ui.TextInput(label = "Do you have a recommended map for the event?", style = discord.TextStyle.short, default="No Suggested Map.", required = False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral = True)

        self.vals['STORY'] = self.story.value
        self.vals['OBJ'] = self.objectives.value
        self.vals['BANS'] = self.bans.value
        self.vals['NOTES'] = self.advice.value
        self.vals['MAP'] = self.maps.value
        self.stop()

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Events(client))