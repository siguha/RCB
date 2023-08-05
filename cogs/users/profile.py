import discord
import aiosqlite
import asyncio
from datetime import datetime
import re
from discord.ext import commands
from discord import app_commands
from utilities.exceptions import Exceptions
from utilities.sheetutils import SheetUtilities

"""
/nprofile and /oprofile shows last AAR date.
"""

class Profiles(commands.GroupCog, name = "profile", description = "Profile commandset."):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client
        self.utils = SheetUtilities.ProfileUtils()
        self.e = Exceptions()
    
    @app_commands.command(name = "sync", description = "Sync your SteamID to your DiscordID.")
    async def profile_sync(self, interaction: discord.Interaction, steamid: str, user: discord.Member = None) -> None:
        if re.match(r"^STEAM_0:(?:0|1):[0-9]+[^A-Z]$", steamid) is None:
            await interaction.response.send_message(content = f"Invalid SteamID. Ensure your SteamID looks simiarly to **STEAM:0:X:XXXXXXX....** and try again...", ephemeral = True, delete_after = 5)

        else:
            await interaction.response.send_message(content = f"Successfully synced SteamID **{steamid}** to DiscordID **{interaction.user.id}**.", ephemeral = True, delete_after = 5)

            member = interaction.user if user is None else user

            await self.utils.profile_sync(steamid, member.id, member.display_name)

    @app_commands.command(name = "view", description = "View a Commando's profile.")
    async def profile_view(self, interaction: discord.Interaction, user: discord.Member) -> None:
        if user is None:
            user = interaction.user

        try:
            data = await self.utils.profile_fetch(user.id)

        except self.e.UserNotFound as e:
            await interaction.response.send_message(content = f"{e.__class__.__name__}: {e}")
            return 1

        embed = discord.Embed(title = "Clone Commando Identification Card", description = f"Showing reports for commando **{data['RANK']} {data['NAME']}**, currently stationed aboard the RSD Liberator....\n", color = discord.Colour.red())
        embed.add_field(name = "Batch Information", value = f"**Callsign**: {data['CLASS']}\n**Deployed on**: {data['JOINED']}, {data['DAYS_IN']} Rotations ago.\n**Last Checkin**: {data['DAYS_SINCE']}\n**Region**: {data['REGION']}\n\n")
        embed.add_field(name = "Certifications Sheet", value = f"**Demolitions**: {data['DEMO']}\n**Engineering**: {data['ENGINEER']}\n**Field Medicine**: {data['MEDIC']}\n**Marksmanship**: {data['SNIPER']}\n\n", inline = False)
        embed.set_author(name = "GAR CCID", icon_url = "https://i.imgur.com/rgsTDEj.png")
        embed.set_footer(text = f"| File Accessed by {user.display_name}\n| Property of the Republic Commandos")

        await interaction.response.send_message(embed = embed)

    @app_commands.command(name = "nco", description = "Check an Enlisted's profile.")
    @app_commands.checks.has_any_role(452534405874057217, 333432981605580800, 333432642878046209)
    async def profile_nco(self, interaction: discord.Interaction, user: discord.Member) -> None:
        try:
            data = await self.utils.stats_fetch(user.id)

        except self.e.UserNotFound as e:
            await interaction.response.send_message(content = f"{e.__class__.__name__}: {e}")
            return 1

        embed = discord.Embed(title = "NCO Stats Viewer", description = f"Last promoted on **{data['PROMO_DATE']}**, **{data['PROMO_DAYS']}** days ago.", timestamp = datetime.now(), color = discord.Colour.yellow())
        embed.set_author(name = f"{user.display_name}'s Stats Summary", icon_url = "https://i.imgur.com/rgsTDEj.png")
        embed.add_field(name = "Logging Stats", value = f"**Total Logs**: {data['LOGS']}\n**Participated Logs**: {data['PARTICIPATED']}\n**Leads**: {data['LEADS']}")
        embed.set_footer(text = "DO NOT DISCLOSE THIS INFORMATION.")

        await interaction.response.send_message(embed = embed, delete_after = 45)

    @app_commands.command(name = "officer", description = "Check an NCO's profile.")
    @app_commands.checks.has_any_role(333432981605580800, 333432642878046209)
    async def profile_officer(self, interaction: discord.Interaction, user: discord.Member) -> None:
        try:
            data = await self.utils.stats_fetch(user.id)

        except self.e.UserNotFound as e:
            await interaction.response.send_message(content = f"{e.__class__.__name__}: {e}")
            return 1

        embed = discord.Embed(title = "Officer Stats Viewer", description = f"Last promoted on **{data['PROMO_DATE']}**, **{data['PROMO_DAYS']}** days ago.\n\nLast AAR on **{data['LAST_AAR']}**.", timestamp = datetime.now(), color = discord.Colour.yellow())
        embed.set_author(name = f"{user.display_name}'s Stats Summary", icon_url = "https://i.imgur.com/rgsTDEj.png")
        embed.add_field(name = "Logging Stats", value = f"**Total Logs**: {data['LOGS']}\n**Participated Logs**: {data['PARTICIPATED']}\n**Trainings Hosted**: {data['TRAININGS']}\n**Co-Hosts**: {data['COHOSTS']}\n**Leads**: {data['LEADS']}\n**SGT Trials**: {data['SGT_TRIALS']}\n**Basic Training**: {data['BT_TRIALS']}")
        embed.set_footer(text = "DO NOT DISCLOSE THIS INFORMATION.\n")

        await interaction.response.send_message(embed = embed, delete_after = 45)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Profiles(client))