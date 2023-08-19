import discord
from discord import app_commands
from discord.ext import commands
from datetime import datetime
import datetime

from utilities.sheetutils import SheetUtilities
from utilities.exceptions import Exceptions

P_UTILS = SheetUtilities.ProfileUtils()
O_UTILS = SheetUtilities.OfficerUtils()
e = Exceptions()

class Officers(commands.GroupCog, name='officer', description='Officer comamndset.'):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.vote_reactions = [
            "<:Agree:997952326260244540>", 
            "<:Disagree:997952324418945274>"
        ]
        self.client.loop.create_task(self.background(self.client))

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()
        global O_ROLE
        global HC_ROLE 
        guild = client.get_guild(333429464752979978)
        O_ROLE = guild.get_role(333432981605580800)
        HC_ROLE = guild.get_role(452534405874057217)

    @app_commands.command(name='vote', description='Initiate an Officer+ Vote.')
    async def officer_vote(self, interaction: discord.Interaction, user: discord.Member, rank: str):
        await interaction.response.defer(ephemeral=True)
        
        try:
            data = await P_UTILS.stats_fetch(user.id)
            await O_UTILS.officer_vote(user.id)
        except e.UserNotFound as error:
            await interaction.followup.send(content = f"{error.__class__.__name__}: {error}")
            return 1
        else:
            if interaction.channel_id == 692638901889663016:
                embed = discord.Embed(title=f"{user.display_name} for {rank}", description=f"**Days at Rank:** {data['PROMO_DAYS']}\n**Total Logs**: {data['LOGS']}\n**Participated Logs**: {data['PARTICIPATED']}\n**Trainings Hosted**: {data['TRAININGS']}\n**Co-Hosts**: {data['COHOSTS']}\n**Leads**: {data['LEADS']}\n**SGT Trials**: {data['SGT_TRIALS']}\n**Basic Training**: {data['BT_TRIALS']}", colour=discord.Colour.red(), timestamp=datetime.datetime.now())
                embed.set_author(name='Officer Vote', icon_url="https://i.imgur.com/rgsTDEj.png")
            
            elif interaction.channel_id == 766849519257124895:
                embed = discord.Embed(title=f"{user.display_name} for {rank}", description=f"**Days at Rank:** {data['PROMO_DAYS']}\n**Total Logs**: {data['LOGS']}\n**Participated Logs**: {data['PARTICIPATED']}\n**Tryouts Hosted**: {data['TRYOUTS']}\n**Trainings Hosted**: {data['TRAININGS']}\n**Co-Hosts**: {data['COHOSTS']}\n**Leads**: {data['LEADS']}\n**SGT Trials**: {data['SGT_TRIALS']}\n**Basic Training**: {data['BT_TRIALS']}", colour=discord.Colour.red(), timestamp=datetime.datetime.now())
                embed.set_author(name='High Command Vote', icon_url="https://i.imgur.com/rgsTDEj.png")

            embed.set_footer(text=f'Started by {interaction.user.display_name}', icon_url=interaction.user.display_avatar)
            msg = await interaction.channel.send(content=f"{O_ROLE.mention} {HC_ROLE.mention}", embed = embed)
            await msg.create_thread(name=f'{embed.title} - Vote Discussion')
            for reaction in self.vote_reactions:
                await msg.add_reaction(reaction)

            await interaction.followup.send('Vote Initiated.', ephemeral=True)
    
    @app_commands.command(name='warn', description='Warn a user for inactivity.')
    @app_commands.checks.has_any_role(333432642878046209, 333432981605580800, 452534405874057217)
    async def officer_warn(self, interaction: discord.Interaction, user: discord.Member):
        try:
            await O_UTILS.officer_warn(user.id)
        
        except e.UserNotFound as error:
            await interaction.response.send_message(content = f"{error.__class__.__name__}: {error}")
            return 1

        else:
            embed = discord.Embed(title='Record of Warn', description=f'{user.mention} has been warned for inactivity to be checked again in 24 hours.', colour=discord.Colour.red())
            embed.set_author(name='Inactivity Warning', icon_url="https://i.imgur.com/rgsTDEj.png")
            embed.set_footer(text=f'Administered by {interaction.user.display_name}', icon_url=interaction.user.display_avatar)
            await interaction.response.send_message(embed = embed)

    @app_commands.command(name = "promos", description = "Check #nco-votes & #officer-votes for a list of passed votes.")
    @app_commands.checks.has_any_role(333432981605580800, 452534405874057217)
    async def vote_checks(self, interaction: discord.Interaction) -> None:
        date = datetime.datetime.today() - datetime.timedelta(days = 1)
        passed = []

        if interaction.channel_id == 409270453836840960:
            channel = interaction.guild.fetch_channel(409270453836840960)

        else:
            channels = [409270453836840960, 692638901889663016]
        
            for id in channels:
                channel = await interaction.guild.fetch_channel(id)
                async for message in channel.history(limit = 15, before = date):
                    reactions = []
                        
                    for reaction in message.reactions:
                        if reaction.is_custom_emoji():
                            reactions.append({'emoji':reaction.emoji.id, 'count':reaction.count})

                        else:
                            reactions.append({'emoji':reaction.emoji, 'count':reaction.count})

                    if not any(reaction['emoji'] == "🔥" for reaction in reactions) and not any(reaction['emoji'] == 1013466597974888498 for reaction in reactions):
                        content = (message.content[:300] + "...") if len(message.content) > 300 else message.content
                        time = message.created_at
                        time_f = time.strftime("%d-%m-%Y")
                        if reactions[0]['count'] > reactions[1]['count']:
                            passed.append(f"> `{time_f}` - {content}... **{reactions[0]['count']} Votes** for, **{reactions[1]['count']} against**. [[Jump!]]({message.jump_url})")

        embed = discord.Embed(title = "Pending Votes", color = discord.Colour.red(), timestamp = datetime.datetime.now())
        n = 1
        for vote in passed:
            embed.add_field(name = f"Vote {n}", value = vote, inline = False)
            n += 1

        await interaction.response.send_message(embed = embed)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        reactions = ["<:Agree:997952326260244540>", "<:Disagree:997952324418945274>"]
        vote_channels = [409270453836840960, 510612993252392960, 692638901889663016, 766849519257124895, 529031321536954381]

        if message.author.id == 1075167587220074566:
            return

        if message.channel.id in vote_channels:
            for emoji in reactions:
                await message.add_reaction(emoji)
            
                await message.create_thread(name = "Vote Discussion")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(Officers(client))