import discord

from discord import ui, app_commands
from discord.ext import commands

class AARCommands(commands.GroupCog, name='aar', description='AARs Commandset.'):
    def __init__(self, client: commands.Bot, aar_operations):
        super().__init__()
        self.client = client
        self.aar_ops = aar_operations

        self.client.loop.create_task(self.background(self.client))

        self.types = [ 
            'Lead',
            'Lead Spectate',
            'Training',
            'Lore Activities',
            'Basic Training',
            'SGT Trials',
            'Spec Certs',
            'Tryout',
        ]
        self.bt = [
            'Introduction',
            'Lore',
            'Basic Combat Training',
            'Event Protocol Training',
            'Squad Lead Training',
            'Raider Training'
        ]
        self.trial = [
            'Interview',
            'Basic Combat Training',
            'Event Protocol Training',
            'Event Lead',
            'PvP Round 1',
            'PvP Round 2',
            'PvP Round 3',
        ]

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()

        # Initializing global variables that'll be used throughout the class.
        global AAR_CHANNEL
        global ADVISOR_ROLE

        guild = client.get_guild(333429464752979978)
        AAR_CHANNEL = guild.get_channel(343795194333757441)
        ADVISOR_ROLE = guild.get_role(1205615781027782736)

    @app_commands.command(name='log', description='Log an AAR')
    async def aar_log(self):
        ...
        
    @app_commands.command(name='remove', description='Remove an AAR')
    async def aar_remove(self):
        ...
        
    @app_commands.command(name='edit', description='Edit an AAR')
    async def aar_edit(self):
        ...

    @app_commands.command(name='append', description='Append members to an AAR')
    async def aar_append(self):
        ...

    @app_commands.command(name='pop', description='Remove members to an AAR')
    async def aar_pop(self):
        ...