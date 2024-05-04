import discord

from datetime import datetime
from discord import ui, app_commands
from discord.ui import UserSelect
from discord.ext import commands

class AARCommands(commands.GroupCog, name='aar', description='AARs Commandset.'):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.aar_ops = self.client.aar_ops

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

        self.embed_design_dict = {
            'Lead': {
                'color': discord.Colour.brand_green(),
                'title': 'Lead Log',
                'fields': lead_modal_fields
            },
            'Lead Spectate': {
                'color': discord.Colour.dark_green(),
                'title': 'Lead Spectate Log',
                'fields': lead_spec_modal_fields
            },
            'Training': {
                'color': discord.Colour.dark_magenta(),
                'title': 'Training Log',
                'fields': training_modal_fields
            },
            'Lore Activities': {
                'color': discord.Colour.gold(),
                'title': 'Lore Activities Log',
                'fields': lore_modal_fields
            },
            'Basic Training': {
                'color': discord.Colour.blue(),
                'title': 'Basic Training Log',
                'fields': bt_modal_fields
            },
            'SGT Trials': {
                'color': discord.Colour.dark_blue(),
                'title': 'SGT Trials Log',
                'fields': sgt_modal_fields
            },
            'Spec Certs': {
                'color': discord.Colour.purple(),
                'title': 'Spec Certs Log',
                'fields': spec_modal_fields
            },
            'Tryout': {
                'color': discord.Colour.teal(),
                'title': 'Tryout Log',
                'fields': tryout_modal_fields
            },
        }

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()

        global AAR_CHANNEL
        global ADVISOR_ROLE

        guild = client.get_guild(333429464752979978)
        AAR_CHANNEL = guild.get_channel(343795194333757441)
        ADVISOR_ROLE = guild.get_role(1205615781027782736)

    @app_commands.command(name='log', description='Log an AAR')
    async def aar_log(self, interaction: discord.Interaction, *, type: str, logger: discord.Member = None, bt: str = None, trial: str = None, cohost: discord.Member = None, lead: discord.Member = None, trainee: discord.Member = None, gm: discord.Member = None):
        if type not in self.types:
            await interaction.response.send_message(content=f'[**Invalid Type**] {interaction.user.mention} - `{type}` is not a valid AAR type.', ephemeral=True, delete_after=5)
            return 1
        
        if logger is None:
            logger = interaction.user

        member_select = MemberSelect()
        logging_modal = LoggingModal(title=self.embed_design_dict[type]['title'], fields=self.embed_design_dict[type]['fields'])

        log_id = datetime.now().strftime("%H%M%S%d%m%Y")
        embed = discord.Embed(title=f'{type} Logging', description=f'Logged by {logger.mention}', color=self.embed_design_dict[type]['color'])
        embed.set_author(name = "RC Logging Systems", icon_url = "https://i.imgur.com/3gTO5ie.png")
        embed.set_footer(text=f'Log ID: {log_id}')

        if type == 'Lead':
            if type == 'Lead Spectate':
                if lead is None:
                    await interaction.response.send_message(content=f'[**Missing Lead**] {interaction.user.mention} - You must specify a Lead.', ephemeral=True, delete_after=5)
                    return 1
                
                if ADVISOR_ROLE in interaction.user.roles:
                    embed.title = "Advisor Lead Spectate"
                    embed.colour = discord.Colour.from_str("#800000")  
            
            else:
                lead = interaction.user

            await interaction.response.send_modal(logging_modal)  
            await logging_modal.wait()

            await interaction.followup.send(content=f'[**AAR Logging**] Please select attending member(s).', view=member_select, ephemeral=True)
            await member_select.wait()                        

            responses = logging_modal.values
            members = member_select.members

            embed.add_field(name="Attendees", value =' '.join(list(member.mention for member in members)), inline=False)
            embed.add_field(name="Event Lead", value=lead.mention, inline=False)
            for key, value in responses.items():
                embed.add_field(name=key, value=value, inline=False)

            message = await AAR_CHANNEL.send(embed=embed)

        if type == 'Basic Training':
            if bt not in self.bt:
                await interaction.response.send_message(content=f'[**Invalid Type**] {interaction.user.mention} - `{bt}` is not a valid Basic Training type.', ephemeral=True, delete_after=5)
                return 1
            
            await interaction.response.send_modal(logging_modal)
            await logging_modal.wait()

            await interaction.followup.send(content=f'[**Basic Training**] Please select private(s).', view=member_select, ephemeral=True)
            await member_select.wait()

            responses = logging_modal.values
            members = member_select.members

            embed.add_field(name="Private(s)", value =' '.join(list(private.mention for private in members)), inline=False)
            for key, value in responses.items():
                embed.add_field(name=key, value=value, inline=False)
            
            message = await AAR_CHANNEL.send(embed=embed)

        if type == 'SGT Trials':
            if trial not in self.trial or trial is None:
                await interaction.response.send_message(content=f'[**Invalid Type**] {interaction.user.mention} - `{trial}` is not a valid SGT Trial type.', ephemeral=True, delete_after=5)
                return 1
            if trainee is None:
                await interaction.response.send_message(content=f'[**Missing CPL**] {interaction.user.mention} - You must specify the CPL for this trial.', ephemeral=True, delete_after=5)
                return 1
            
            await interaction.response.send_modal(logging_modal)
            await logging_modal.wait()

            responses = logging_modal.values

            embed.add_field(name="Corporal", value=trainee.mention, inline=False)
            embed.add_field(name="Trial", value=trial, inline=False)
            for key, value in responses.items():
                embed.add_field(name=key, value=value, inline=False)
            
            message = await AAR_CHANNEL.send(embed=embed)            

        if type == 'Spec Certs':
            if trainee is None:
                await interaction.response.send_message(content=f'[**Missing Testee**] {interaction.user.mention} - You must specify the trainee for the cert.', ephemeral=True, delete_after=5)
                return 1

            await interaction.response.send_modal(logging_modal)
            await logging_modal.wait()

            responses = logging_modal.values

            embed.add_field(name="Trainee", value=trainee.mention, inline=False)
            for key, value in responses.items():
                embed.add_field(name=key, value=value, inline=False)

            message = await AAR_CHANNEL.send(embed=embed)            

        if type == 'Tryout':
            await interaction.response.send_modal(logging_modal)
            await logging_modal.wait()

            await interaction.followup.send(content=f'[**Tryouts**] Please select attending member(s).', view=member_select, ephemeral=True)
            await member_select.wait()

            responses = logging_modal.values
            members = member_select.members

            embed.add_field(name="Attendees", value =' '.join(list(member.mention for member in members)), inline=False)
            for key, value in responses.items():
                embed.add_field(name=key, value=value, inline=False)

            message = await AAR_CHANNEL.send(embed=embed)
        
    @app_commands.command(name='remove', description='Remove an AAR')
    async def aar_remove(self, interaction: discord.Interaction, log_id: int):
        await interaction.response.defer(ephemeral=True)

        message_id = await self.aar_ops.fetch_aar(log_id) 
        message = await AAR_CHANNEL.fetch_message(message_id)

        await message.delete()

        try:
            await self.aar_ops.remove_aar(log_id)
            await interaction.followup.send(f"Log `{log_id}` has been removed.", ephemeral = True)
        
        except:
            await interaction.followup.send(content=f'[**LogNotFound**] Log ID not found in database.', ephemeral=True, delete_after=5)
        
    #@app_commands.command(name='edit', description='Edit an AAR')
    #async def aar_edit(self):

    #@app_commands.command(name='append', description='Append members to an AAR')
    #async def aar_append(self):

    #@app_commands.command(name='pop', description='Remove members to an AAR')
    #async def aar_pop(self):

async def setup(client: commands.Bot) -> None:
    await client.add_cog(AARCommands(client))

#class LoggingModal(ui.Modal):
#    def __init__(self, title, fields):
#        super().__init__(title=title, timeout=None)
#        self.fields = {field['label']: ui.TextInput(**field) for field in fields}
#        self.values = {}

#    async def on_submit(self, interaction: discord.Interaction):
#        await interaction.response.defer(ephemeral=True)

#        for label, field in self.fields.items():
#            self.values[label] = field.value

#        print(self.values)

#        self.stop()

class LoggingModal(ui.Modal):
    def __init__(self, title, fields):
        super().__init__(title=title, timeout=None)
        self.fields = {}
        self.values = {}

        # Dynamically create and add TextInput fields to the modal
        for field in fields:
            text_input = ui.TextInput(label=field['label'], style=field.get('style', discord.TextStyle.short), required=field.get('required', True), placeholder=field.get('placeholder', ''))
            self.fields[field['label']] = text_input
            self.add_item(text_input)  # Add TextInput to the modal

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        # Collect the values from each field
        for label, field in self.fields.items():
            self.values[label] = field.value

        self.stop()

class EditModal(ui.Modal, title='AAR Editor'):
    def __init__(self):
        super().__init__(timeout=None, custom_id='editModal')
        self.index = None
        self.corrections = None

    edit_field = ui.TextInput(label='Field to Edit', placeholder='Enter the NUMBER of the field to edit.', style=discord.TextStyle.short, required=True)
    corrections = ui.TextInput(label='Corrections', placeholder='Enter the corrections.', style=discord.TextStyle.short, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer()

        self.index = int(self.edit_field.value)
        self.corrections = self.corrections.value

        self.stop()

    async def on_cancel(self, interaction: discord.Interaction):
        await interaction.response.send_message(content='[**AAR Editor**] All edits cancelled.', ephemeral=True, delete_after=5)

class EditButtons(ui.View):
    def __init__(self, msg: discord.Message):
        super().__init__(timeout=45)
        self.msg = msg

    @ui.button(label='Edit', style=discord.ButtonStyle.gray, custom_id='editButton', disabled=False)
    async def edit_button(self, interaction: discord.Interaction, button: ui.Button):
        edit_modal = EditModal()

        await interaction.response.send_modal(modal=edit_modal)
        await edit_modal.wait()

        index, corrections = edit_modal.index, edit_modal.corrections
        embed = self.msg.embeds[0]
        field = embed.fields[index]
        embed.set_field_at(index, name=field.name, value=corrections, inline=False)

        await self.msg.edit(embed=embed)
        await interaction.followup.send(f'[**AAR Editor**] AAR Editted. [Jump!]({self.msg.jump_url})', ephemeral=True)

class MemberSelect(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.members = []
    
    @ui.select(
        cls=UserSelect,
        placeholder="Select Members.",
        min_values=1,
        max_values=25
    )

    async def user_select(self, interaction: discord.Interaction, select: UserSelect):
        await interaction.response.defer(ephemeral=True)
        self.members = [user for user in select.values]

    @ui.button(label='Submit', custom_id='button:Submit') 
    async def on_submit(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.defer(ephemeral=True)
        await interaction.delete_original_response()

        self.stop()

lead_modal_fields = [
    {'label': "Event Type", 'style': discord.TextStyle.short, 'placeholder': "i.e S1 Main, S2 Mini...", 'required': True},
    {'label': "Squad Roles", 'style': discord.TextStyle.short, 'required': True},
    {'label': "Brief Event Summary", 'style': discord.TextStyle.long, 'required': True},
    {'label': "Squad Performance", 'style': discord.TextStyle.long, 'required': True}
]

lead_spec_modal_fields = [
    {'label': "Event Type", 'style': discord.TextStyle.short, 'placeholder': "i.e S1 Main, S2 Mini...", 'required': True},
    {'label': "Squad Roles", 'style': discord.TextStyle.short, 'required': True},
    {'label': "Brief Event Summary", 'style': discord.TextStyle.long, 'required': True},
    {'label': "Squad Performance", 'style': discord.TextStyle.long, 'required': True},
    {'label': "Lead Evaluation", 'style': discord.TextStyle.long, 'required': True}
]

training_modal_fields = [
    {'label': "Training Type", 'style': discord.TextStyle.short, 'required': True},
    {'label': "Squad Roles", 'style': discord.TextStyle.short, 'required': True},
    {'label': "Brief Training Summary", 'style': discord.TextStyle.long, 'required': True},
    {'label': "Squad Performance", 'style': discord.TextStyle.long, 'required': True},
    {'label': "Lead Performance", 'style': discord.TextStyle.long, 'required': False}
]

lore_modal_fields = [
    {'label': "Log Type", 'style': discord.TextStyle.short, 'required': True},
    {'label': "Squads Involved", 'style': discord.TextStyle.short, 'required': True},
    {'label': "Battalions Involved", 'style': discord.TextStyle.short, 'required': True},
    {'label': "Additional Information", 'style': discord.TextStyle.short, 'required': False}
]

bt_modal_fields = [
    {'label': "Did the PVT(s) pass or fail?", 'style': discord.TextStyle.short, 'placeholder': "If one private fails and another passes, you may specify that here.", 'required': True},
    {'label': "Any notes about their performance?", 'style': discord.TextStyle.long, 'required': False}
]

sgt_modal_fields = [
    {'label': "Did the CPL pass or fail?", 'style': discord.TextStyle.short, 'placeholder': "Pass | Fail", 'required': True},
    {'label': "Any notes about their performance?", 'style': discord.TextStyle.long, 'required': False}
]

spec_modal_fields = [
    {'label': "Certification Type", 'style': discord.TextStyle.short, 'required': True},
    {'label': "Did the attendee pass or fail?", 'style': discord.TextStyle.short, 'placeholder': "Pass | Fail", 'required': True},
    {'label': "Any notes about their performance?", 'style': discord.TextStyle.long, 'required': False}
]

tryout_modal_fields = [
    {'label': "Region", 'style': discord.TextStyle.short, 'required': True},
    {'label': "Tryout Roles", 'style': discord.TextStyle.short, 'required': True},
    {'label': "Number Passed", 'style': discord.TextStyle.short, 'default': "0", 'required': True},
    {'label': "Who Passed?", 'style': discord.TextStyle.long, 'required': False}
]