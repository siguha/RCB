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
        self.client.loop.create_task(self.background(self.client))

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()
        global O_ROLE
        global HC_ROLE
        global NCO_ROLE
        global ROLES
        guild = client.get_guild(333429464752979978)
        NCO_ROLE = guild.get_role(333432642878046209)
        O_ROLE = guild.get_role(333432981605580800)
        HC_ROLE = guild.get_role(452534405874057217)
        ROLES = [NCO_ROLE, O_ROLE, HC_ROLE]

    @app_commands.command(name = "sync", description = "Sync your SteamID to your DiscordID.")
    async def profile_sync(self, interaction: discord.Interaction, steamid: str, user: discord.Member = None) -> None:
        if re.match(r"^STEAM_0:(?:0|1):[0-9]+[^A-Z]$", steamid) is None:
            await interaction.response.send_message(content = f"Invalid SteamID. Ensure your SteamID looks simiarly to **STEAM:0:X:XXXXXXX....** and try again...", ephemeral = True, delete_after = 5)
        
        else:
            member = interaction.user if user is None else user
            if user is not None:
                if any(role in interaction.user.roles for role in ROLES):
                    await self.utils.profile_sync(steamid, member.id, member.display_name)  
                    await interaction.response.send_message(content = f"Successfully synced SteamID **{steamid}** to DiscordID **{user.id}**.", ephemeral = True, delete_after = 5)

                else:
                    await interaction.response.send_message("You're not of the rank required to force-sync an ID.", ephemeral=True, delete_after=15)
                    return 1
            else: 
                await interaction.response.send_message(content = f"Successfully synced SteamID **{steamid}** to DiscordID **{interaction.user.id}**.", ephemeral = True, delete_after = 5)
                await self.utils.profile_sync(steamid, member.id, member.display_name)       

    @app_commands.command(name = "view", description = "View a Commando's profile.")
    async def profile_view(self, interaction: discord.Interaction, user: discord.Member) -> None:
        await interaction.response.defer()

        if user is None:
            user = interaction.user

        try:
            data = await self.utils.profile_fetch(user.id)

        except self.e.UserNotFound as e:
            await interaction.followup.send(content = f"{e.__class__.__name__}: {e}")
            return 1

        embed = discord.Embed(title = "Clone Commando Identification Card", description = f"Showing reports for **{data['RANK']} {data['NAME']}**, currently stationed aboard the RSD Liberator....\n\u200b", color = discord.Colour.red())
        embed.add_field(name = "Batch Information", value = f"\n**Callsign**: {data['CLASS']}\n**Deployed on**: {data['JOINED']}, {data['DAYS_IN']} Rotations ago.\n**Last Checkin**: {data['DAYS_SINCE']} Days Ago.\n**Region**: {data['REGION']}\n\u200b")
        embed.add_field(name = "Certifications Sheet", value = f"\n**Demolitions**: {data['DEMO']}\n**Engineering**: {data['ENGINEER']}\n**Field Medicine**: {data['MEDIC']}\n**Marksmanship**: {data['SNIPER']}\n\n", inline = False)
        embed.set_author(name = "GAR CCID", icon_url = "https://i.imgur.com/rgsTDEj.png")
        embed.set_footer(text = f"File Accessed by {user.display_name}", icon_url=user.display_avatar)

        await interaction.followup.send(embed = embed)

    @app_commands.command(name = "nco", description = "Check an Enlisted's profile.")
    @app_commands.checks.has_any_role(452534405874057217, 333432981605580800, 333432642878046209)
    async def profile_nco(self, interaction: discord.Interaction, user: discord.Member) -> None:
        try:
            data = await self.utils.stats_fetch(user.id)

        except self.e.UserNotFound as e:
            await interaction.response.send_message(content = f"{e.__class__.__name__}: {e}")
            return 1

        embed = discord.Embed(title = "NCO Stats Viewer", description = f"Last Seen on **{data['LAST_SEEN']}**, **{data['LAST_SEEN_DAYS']}** days ago.\n\nLast Promoted on **{data['PROMO_DATE']}**, **{data['PROMO_DAYS']}** days ago.\n\nLast AAR on **{data['LAST_AAR']}**, **{data['LAST_AAR_DAYS']}** days ago.\n\nCurrent Activity Status: `{data['LOA']}`", timestamp = datetime.now(), color = discord.Colour.dark_green())
        embed.set_author(name = f"{user.display_name}'s Stats Summary", icon_url = "https://i.imgur.com/rgsTDEj.png")
        embed.add_field(name = "Logging Stats", value = f"**Total Logs**: {data['LOGS']}\n**Participated Logs**: {data['PARTICIPATED']}\n**Leads**: {data['LEADS']}")
        embed.set_footer(text = "DO NOT DISCLOSE THIS INFORMATION.")

        await interaction.response.send_message(embed = embed, delete_after = 45)

    @app_commands.command(name = "officer", description = "Check an NCO's profile.")
    @app_commands.checks.has_any_role(333432981605580800, 452534405874057217)
    async def profile_officer(self, interaction: discord.Interaction, user: discord.Member) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            data = await self.utils.stats_fetch(user.id)

        except self.e.UserNotFound as e:
            await interaction.followup.send(content = f"{e.__class__.__name__}: {e}")
            return 1

        embed = discord.Embed(title = "Officer Stats Viewer", description = f"Last Seen on **{data['LAST_SEEN']}**, **{data['LAST_SEEN_DAYS']}** days ago.\n\nLast Promoted on **{data['PROMO_DATE']}**, **{data['PROMO_DAYS']}** days ago.\n\nLast AAR on **{data['LAST_AAR']}**, **{data['LAST_AAR_DAYS']}** days ago.\n\nCurrent Activity Status: `{data['LOA']}`", timestamp = datetime.now(), color = discord.Colour.yellow())
        embed.set_author(name = f"{user.display_name}'s Stats Summary", icon_url = "https://i.imgur.com/rgsTDEj.png")
        embed.add_field(name = "Logging Stats", value = f"**Total Logs**: {data['LOGS']}\n**Participated Logs**: {data['PARTICIPATED']}\n**Trainings Hosted**: {data['TRAININGS']}\n**Co-Hosts**: {data['COHOSTS']}\n**Leads**: {data['LEADS']}\n**SGT Trials**: {data['SGT_TRIALS']}\n**Basic Training**: {data['BT_TRIALS']}")
        embed.set_footer(text = "DO NOT DISCLOSE THIS INFORMATION.\n")

        msg = await interaction.channel.send(embed = embed)
        await interaction.followup.send('Profile Loaded.', ephemeral=True)
        await msg.delete(delay = 45)

    @app_commands.command(name = "hc", description = "Check an NCO's profile.")
    @app_commands.checks.has_any_role(452534405874057217)
    async def profile_hc(self, interaction: discord.Interaction, user: discord.Member) -> None:
        try:
            data = await self.utils.stats_fetch(user.id)

        except self.e.UserNotFound as e:
            await interaction.response.send_message(content = f"{e.__class__.__name__}: {e}")
            return 1

        embed = discord.Embed(title = "Officer Stats Viewer", description = f"Last Seen on **{data['LAST_SEEN']}**, **{data['LAST_SEEN_DAYS']}** days ago.\n\nLast Promoted on **{data['PROMO_DATE']}**, **{data['PROMO_DAYS']}** days ago.\n\nLast AAR on **{data['LAST_AAR']}**, **{data['LAST_AAR_DAYS']}** days ago.\n\nCurrent Activity Status: `{data['LOA']}`", timestamp = datetime.now(), color = discord.Colour.yellow())
        embed.set_author(name = f"{user.display_name}'s Stats Summary", icon_url = "https://i.imgur.com/rgsTDEj.png")
        embed.add_field(name = "Logging Stats", value = f"**Total Logs**: {data['LOGS']}\n**Participated Logs**: {data['PARTICIPATED']}\n**Trainings Hosted**: {data['TRAININGS']}\n**Tryouts Hosted**: {data['TRYOUTS']}\n**Co-Hosts**: {data['COHOSTS']}\n**Leads**: {data['LEADS']}\n**SGT Trials**: {data['SGT_TRIALS']}\n**Basic Training**: {data['BT_TRIALS']}")
        embed.set_footer(text = "DO NOT DISCLOSE THIS INFORMATION.\n")

        await interaction.response.send_message(embed = embed, delete_after = 45)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Profiles(client))