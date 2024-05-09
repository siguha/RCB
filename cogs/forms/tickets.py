import discord
from discord import ui, app_commands
from discord.ext import commands
from datetime import datetime

class support_modal(ui.Modal, title = "RC Support System"):
    def __init__(self, group):
        super().__init__()
        self.group = group
    
    name = ui.TextInput(label = "Your Name", style = discord.TextStyle.short, placeholder = "If you'd like to remain anonymous, please leave this blank.", default = "Anonymous", required = True)
    report = ui.TextInput(label = "Your Report/Concern", style = discord.TextStyle.long, placeholder = "Please type your report out here. Be sure to include any evidence if necessary, and spare no detail.", required = True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking = True, ephemeral = True)

        nco = interaction.guild.get_channel(1080374717430648864)
        officer = interaction.guild.get_channel(1080358106913050696)
        hc = interaction.guild.get_channel(1080358231743934494)

        group = self.group

        if self.name == "Anonymous":
            embed = discord.Embed(title = "Confidential Support Request", description = f"**Filed By:** Anonymous\n\n", timestamp = datetime.now(), color = discord.Colour.red())

        else:
            embed = discord.Embed(title = "Confidential Support Request", description = f"**Filed By:** {str(interaction.user.display_name)}\n\n", timestamp = datetime.now(), color = discord.Colour.red())
        
        embed.add_field(name = "Report Details", value = str(self.report))
        embed.set_footer(text = "Submitted")
        
        if group == "1":
            msg = await nco.send(embed = embed)

            thread = await msg.create_thread(name = "Report Thread")
            await thread.send(content = "<@&333432642878046209>")
            await interaction.followup.send("Your report/complaint has been submitted to the NCO+. If you've included your name, please expect a follow up message shortly.")
            
        elif group == "2":
            msg = await officer.send(embed = embed)

            thread = await msg.create_thread(name = "Report Thread")
            await thread.send(content = "<@&333432981605580800>")
            await interaction.followup.send("Your report/complaint has been submitted to the Officer+. If you've included your name, please expect a follow up message shortly.")

        elif group == "3":
            msg = await hc.send(embed = embed)
            
            thread = await msg.create_thread(name = "Report Thread")
            await thread.send(content = "<@&452534405874057217>")
            await interaction.followup.send("Your report/complaint has been submitted to the High Command+. If you've included your name, please expect a follow up message shortly.")

        else:
            don_dm = await interaction.guild.get_member(484932458538860544).create_dm()
            await don_dm.send(embed = embed)
            await interaction.followup.send("Your report/complaint has been submitted to the Commander. If you've included your name, please expect a follow up message shortly.")

class group_select(ui.View):
    
    @discord.ui.select(
        placeholder = "Please select who you'd like to reach out to.",
        options = [
            discord.SelectOption(label = "NCO+", value = "1", description = "Contact NCO+."),
            discord.SelectOption(label = "Officer+", value = "2", description = "Contact Officer+."),
            discord.SelectOption(label = "High Command+", value = "3", description = "Contact High Command+"),
            discord.SelectOption(label = "Commander", value = "4", description = "Contact the acting Commander directly.")
        ]
    )

    async def select_callback(self, interaction: discord.Interaction, select):
        select.disabled = True

        if select.values[0] == "1":
            await interaction.response.send_modal(support_modal("1"))

        elif select.values[0] == "2":
            await interaction.response.send_modal(support_modal("2"))

        elif select.values[0] == "3":
            await interaction.response.send_modal(support_modal("3"))
        
        else:
            await interaction.response.send_modal(support_modal("4"))

class support_button(ui.View):
    def __init__(self):
        super().__init__(timeout = None)

    @discord.ui.button(label = "RC Ticket System", style = discord.ButtonStyle.gray, custom_id = 'persistent_view:support', disabled = False, emoji = "📩")
    async def support_button(self, interaction: discord.Interaction, button: ui.Button): 
        enlisted = discord.utils.find(lambda r: r.name == 'Enlisted', interaction.message.guild.roles)
        nco = discord.utils.find(lambda r: r.name == 'NCO', interaction.message.guild.roles)
        officer = discord.utils.find(lambda r: r.name == 'Officer', interaction.message.guild.roles)

        if enlisted in interaction.user.roles or nco in interaction.user.roles or officer in interaction.user.roles:
            await interaction.response.send_message(view = group_select(), ephemeral = True) 
        
class tickets(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @commands.hybrid_command(name="intro", with_app_command=False)
    async def intro(self, interaction: discord.Interaction):
        embed = discord.Embed(title = f"Welcome to the Republic Commandos", description = f"If you're a member of the battalion, use `/profile sync [STEAMID]` to grant yourself access to our Bot functions, like LOAs.\n‎", timestamp = datetime.now(), color = discord.Colour.red())
        embed.set_author(name = "05 Commando Battalion High Command", icon_url = "https://i.imgur.com/rgsTDEj.png")
        embed.add_field(name = "Discord Policies", value = """> **1**: Follow formats and rules pinned within channels, and keep topics relevant to them.\n> **2:** Your Discord username must reflect your in-game name, for example: "**Don | Delta 38 Boss**" (*We ask that our guest's mirror this convention for our convenience as well.*).\n> **3:** Both battalion members and guests must adhere to Discord policy and Officer discretion.\n> **4:** We ask that you please don't spam any of our chats.\n> **5:** Use common sense.\n‎""", inline = False)        
        embed.add_field(name="Discord Guests", value="If you're joining the Discord in hopes of Guest access, please contact an <@&333432981605580800>+. Your request may or may not be denied and is dependant on Officer discretion but will most likely get accepted if you're:\n- **An external High Command member.**\n- **A friend of/with the battalion.**\n- **A trusted Gamemaster.**\n\nIf you're given access, we ask that you adhere to our Discord policies and guidelines. We will occasionally purge Discord Access to clean our member list- if you fall victim to a purge but believe you still deserve access, please DM another Officer+.\n‎", inline=False)
        embed.add_field(name = "RC Support System", value = "The RC Support system is designed to be a multi-purpose ticket system, contacting specific rank groups for any matter. If you have questions, need AARs logged, or more, you can use this for that purpose.\n\nIf you need to contact <@&333432642878046209>+ __confidentially__ for any matter, whether it be __peer-to-peer relations__, __qualms with the battalion__, or *any other* reason, click the button below. You can either remain named, or be entirely anonymous.\n\n**If you're making a serious complaint about a player and don't include either evidence or your name**, please know that it's hard for Officer+ to ensure the validity of your claims. Keep this in mind when making a report.\n‎", inline = False)
        embed.add_field(name = "Permanent Invite Link", value = "https://discord.gg/suprc", inline = False)
        embed.set_footer(text = "Last Updated")
        await interaction.channel.send(embed = embed, view = support_button())

async def setup(client: commands.Bot) -> None:
    await client.add_cog(tickets(client))