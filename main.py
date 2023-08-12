import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

"""
Written by @sigRao for Superior Severs CWRP

for the Republic Commandos
"""

load_dotenv()
TOKEN = os.getenv('TOKEN')

class RCBot(commands.Bot):

    def __init__(self) -> None:
        super().__init__(
            intents = discord.Intents.all(),
            command_prefix = "c. ",
            owner_id = 484932458538860544
        )

        self.init_extensions = [
            'cogs.admin',
            'cogs.forms.aar',
            'cogs.users.profile',
        ]

    async def setup_hook(self) -> None:
        for ext in self.init_extensions:
            await self.load_extension(ext)

    async def on_ready(self) -> None:
        print(f"Connected as {self.user}")
        await client.change_presence(activity = discord.Game('BB ON TOP 💯'))

client = RCBot()
client.run(TOKEN)