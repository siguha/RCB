import discord
import re

from discord import ui, app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

class ProfileCommands(commands.GroupCog, name='profile', description='Profile Commandset.'):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.profile_ops = self.client.profile_ops

        self.client.loop.create_task(self.background(self.client))

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()
        guild = client.get_guild(333429464752979978)

        global HC_ROLE
        global O_ROLE
        global NCO_ROLE
        global ROLES

        HC_ROLE = guild.get_role(452534405874057217)
        O_ROLE = guild.get_role(333432981605580800)
        NCO_ROLE = guild.get_role(333432642878046209)
        ROLES = [NCO_ROLE, O_ROLE, HC_ROLE]

    @app_commands.command(name='register', description='Register a commando profile.')
    async def profile_register(self, interaction: discord.Interaction, name: str, steamid: str, designation: str, user: discord.Member = None):
        if re.match(r"^STEAM_0:(?:0|1):[0-9]+[^A-Z]$", steamid) is None:
            await interaction.response.send_message(content = f"Invalid SteamID. Ensure your SteamID looks simiarly to **STEAM:0:X:XXXXXXX....** and try again...", ephemeral = True, delete_after = 5)

        else:
            member = interaction.user if user is None else user

            if user is not None:
                if not any(role in interaction.user.roles for role in ROLES):
                    await interaction.response.send_message(content=f'[**Missing Permission**] {interaction.user.mention} You\'re not of the rank required to force-sync an ID.', ephemeral=True, delete_after=5)
                    return 1
                
            try:
                designation = await self.profile_ops.register_user(member.id, steamid, designation, name)

            except ValueError as e:
                await interaction.response.send_message(content=f'[**{e.__class__.__name__}**] {member.mention} - *{e}*', ephemeral=True, delete_after=5)
                return 1

            await member.edit(nick=f'{name} | SRE {designation}')
            await interaction.response.send_message(content=f'[**New Register**] {member.mention} - (`{steamid}`) has been successfully registered as **RC-{designation}**.')

    @app_commands.command(name='view', description='View a Commando\'s profile.')
    async def profile_view(self, interaction: discord.Interaction, user: discord.Member = None):
        await interaction.response.defer()

        nco_channels = [353958040648810510, 409270453836840960, 1149776758514667652]
        officer_channels = [333436275942096896, 692638901889663016, 1150110812522958929]
        command_channels = [1066417938644615249, 766849519257124895, 1150113667652788335, 845979536733765692]
        
        if user is None:
            user = interaction.user

        data = await self.profile_ops.profile_fetch(user.id)

        if interaction.channel_id in nco_channels:
            embed = discord.Embed(title = "NCO Stats Viewer", description = f"- Last Seen on **{data['LAST_SEEN']}**, **{data['LAST_SEEN_DAYS']}** days ago.\n- Last Promoted on **{data['PROMO_DATE']}**, **{data['PROMO_DAYS']}** days ago.\n- Last AAR on **{data['LAST_AAR']}**, **{data['LAST_AAR_DAYS']}** days ago.\n- Current Activity Status: `{data['LOA']}`\n\u200b", timestamp = datetime.now(), color = discord.Colour.dark_green())
            embed.set_author(name = f"{user.display_name}'s Stats Summary", icon_url = "https://i.imgur.com/rgsTDEj.png")
            embed.add_field(name = "Logging Stats", value = f"- **Total Logs**: {data['LOGS']}\n- **Participated Logs**: {data['PARTICIPATED']}\n- **Leads**: {data['LEADS']}\n\u200b", inline = False)
            embed.add_field(name="Qualifications Sheet", value=f"- **Basic Training (BT)**: {data['BT']}\n- **Squad Lead Training (SLT)**: {data['SLT']}\n- **Raider Training (RDT)**: {data['RDT']}", inline = False)
            embed.set_footer(text = "DO NOT DISCLOSE THIS INFORMATION.")

            await interaction.followup.send(embed=embed)

        elif interaction.channel_id in officer_channels:
            embed = discord.Embed(title = "Officer Stats Viewer", description = f"- Last Seen on **{data['LAST_SEEN']}**, **{data['LAST_SEEN_DAYS']}** days ago.\n- Last Promoted on **{data['PROMO_DATE']}**, **{data['PROMO_DAYS']}** days ago.\n- Last AAR on **{data['LAST_AAR']}**, **{data['LAST_AAR_DAYS']}** days ago.\n- Current Activity Status: `{data['LOA']}`\n\u200b", timestamp = datetime.now(), color = discord.Colour.yellow())
            embed.set_author(name = f"{user.display_name}'s Stats Summary", icon_url = "https://i.imgur.com/rgsTDEj.png")
            embed.add_field(name = "Logging Stats", value = f"- **Total Logs**: {data['LOGS']}\n- **Participated Logs**: {data['PARTICIPATED']}\n- **Trainings Hosted**: {data['TRAININGS']}\n- **Co-Hosts**: {data['COHOSTS']}\n- **Leads**: {data['LEADS']}\n- **SGT Trials**: {data['SGT_TRIALS']}\n- **Basic Training**: {data['BT_TRIALS']}\n\u200b", inline = False)
            embed.add_field(name="Qualifications Sheet", value=f"- **Basic Training (BT)**: {data['BT']}\n- **Squad Lead Training (SLT)**: {data['SLT']}\n- **Raider Training (RDT)**: {data['RDT']}", inline = False)
            embed.set_footer(text = "DO NOT DISCLOSE THIS INFORMATION.\n")

            await interaction.followup.send(embed=embed)

        elif interaction.channel_id in command_channels:
            embed = discord.Embed(title = "Commmand Stats Viewer", description = f"- Last Seen on **{data['LAST_SEEN']}**, **{data['LAST_SEEN_DAYS']}** days ago.\n- Last Promoted on **{data['PROMO_DATE']}**, **{data['PROMO_DAYS']}** days ago.\n- Last AAR on **{data['LAST_AAR']}**, **{data['LAST_AAR_DAYS']}** days ago.\n- Current Activity Status: `{data['LOA']}`\n\u200b", timestamp = datetime.now(), color = discord.Colour.yellow())
            embed.set_author(name = f"{user.display_name}'s Stats Summary", icon_url = "https://i.imgur.com/rgsTDEj.png")
            embed.add_field(name = "Logging Stats", value = f"- **Total Logs**: {data['LOGS']}\n- **Participated Logs**: {data['PARTICIPATED']}\n- **Trainings Hosted**: {data['TRAININGS']}\n- **Tryouts Hosted**: {data['TRYOUTS']}\n- **Co-Hosts**: {data['COHOSTS']}\n- **Leads**: {data['LEADS']}\n- **SGT Trials**: {data['SGT_TRIALS']}\n- **Basic Training**: {data['BT_TRIALS']}\n\u200b", inline = False)
            embed.add_field(name="Qualifications Sheet", value=f"- **Basic Training (BT)**: {data['BT']}\n- **Squad Lead Training (SLT)**: {data['SLT']}\n- **Raider Training (RDT)**: {data['RDT']}", inline = False)
            embed.set_footer(text = "DO NOT DISCLOSE THIS INFORMATION.\n")

            await interaction.followup.send(embed=embed)
        
        else:
            create_id_card(data)

            await interaction.followup.send(file=discord.File('id_card_output.png'))

def create_id_card(data):
    template_img = Image.open('template.png')
    draw = ImageDraw.Draw(template_img)

    font_path = 'Tw Cen MT.ttf' 
    font_size = 19
    font = ImageFont.truetype(font_path, font_size)

    name_pos = (210, 158)
    rank_pos = (210, 190)
    callsign_pos = (210, 222)
    join_pos = (210, 276)
    promotion_pos = (210, 308)
    last_seen_pos = (210, 341)

    demo_pos = (217, 487)
    engineer_pos = (217, 519)
    medic_pos = (217, 551)
    sniper_pos = (217, 583)

    bt_pos = (217, 628)
    slt_pos = (217, 649)
    rdt_pos = (217, 670)

    draw.text(name_pos, f"\"{data['NAME']}\", {data['DESIGNATION']}", font=font, fill='#979798')
    draw.text(rank_pos, data['RANK'], font=font, fill='#979798')
    draw.text(callsign_pos, data['CLASS'], font=font, fill='#979798')
    draw.text(join_pos, data['JOINED'], font=font, fill='#979798')
    draw.text(promotion_pos, data['PROMO_DATE'], font=font, fill='#979798')
    draw.text(last_seen_pos, data['LAST_SEEN'], font=font, fill='#979798')
    
    draw.text(demo_pos, data['DEMO'], font=font, fill='#7a2d2d' if data['DEMO'] == 'Trainee' else '#88c45c' if data['DEMO'] == 'Certified' else '#0a538a' if data['DEMO'] == 'Trainer+' else '#979798')
    draw.text(engineer_pos, data['ENGINEER'], font=font, fill='#7a2d2d' if data['ENGINEER'] == 'Trainee' else '#88c45c' if data['ENGINEER'] == 'Certified' else '#0a538a' if data['ENGINEER'] == 'Trainer+' else '#979798')
    draw.text(medic_pos, data['MEDIC'], font=font, fill='#7a2d2d' if data['MEDIC'] == 'Trainee' else '#88c45c' if data['MEDIC'] == 'Certified' else '#0a538a' if data['MEDIC'] == 'Trainer+' else '#979798')
    draw.text(sniper_pos, data['SNIPER'], font=font, fill='#7a2d2d' if data['SNIPER'] == 'Trainee' else '#88c45c' if data['SNIPER'] == 'Certified' else '#0a538a' if data['SNIPER'] == 'Trainer+' else '#979798')

    draw.text(bt_pos, data['BT'], font=font, fill='#88c45c' if data['BT'] == 'Completed' else '#7a2d2d')
    draw.text(slt_pos, data['SLT'], font=font, fill='#88c45c' if data['SLT'] == 'Completed' else '#7a2d2d')
    draw.text(rdt_pos, data['RDT'], font=font, fill='#88c45c' if data['RDT'] == 'Completed' else '#7a2d2d')

    output_path = 'id_card_output.png'
    template_img.save(output_path)

    return output_path

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ProfileCommands(client))