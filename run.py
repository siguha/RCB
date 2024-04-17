import discord
# import os

from discord.ext import commands
# from cogs.form

class AZI(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            intents=discord.Intents.all(),
            owner_id=484932458538860544
        )

        self.__initial_extensions = []

    async def setup_hook(self):
        for extension in self.__initial_extensions:
            self.load_extension(extension)

    async def on_ready(self):
        print(f'Logged in as {self.user} ({self.user.id})')

        await client.change_presence(activity=discord.Game(name='v3 - BB ON TOP 💯'))
    
client = AZI()
client.run()