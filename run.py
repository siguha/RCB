import discord
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
client.run()