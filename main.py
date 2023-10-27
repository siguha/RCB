import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

from cogs.forms import loa
from cogs.forms import tickets

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
            command_prefix = "!",
            owner_id = 484932458538860544
        )

        self.init_extensions = [
            'cogs.admin',
            'cogs.misc',
            'cogs.squads',
            'cogs.forms.aar',
            'cogs.forms.loa',
            'cogs.forms.tickets',
            'cogs.users.officer',
            'cogs.users.profile',
        ]

    async def setup_hook(self) -> None:
        for ext in self.init_extensions:
            await self.load_extension(ext)

        self.add_view(loa.Views.ReturnButtons())
        self.add_view(tickets.support_button())


    async def on_ready(self) -> None:
        print(f"Connected as {self.user}")
        await client.change_presence(activity = discord.Game('BB ON TOP 💯'))

client = RCBot()
client.run(TOKEN)