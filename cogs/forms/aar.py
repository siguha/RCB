import discord
from discord import ui, app_commands
from discord.ui import UserSelect
from discord.ext import commands
from utilities.sheetutils import SheetUtilities
from utilities.exceptions import Exceptions
from datetime import datetime

UTILS = SheetUtilities.AarUtils()
e = Exceptions()

class AARs(commands.GroupCog, name = "aar", description = "AAR Commandset."):
    def __init__(self, client: commands.Bot):
        super().__init__()
        self.client = client
        self.client.loop.create_task(self.background(self.client))
        self.views = Views()
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
            'Defcon',
            'Breaching',
            'Communications',
            'Spec Training'
        ]
        self.trial = [
            'Defcon',
            'Breaching',
            'Event Lead',
            'PvP Round 1',
            'PvP Round 2',
            'PvP Round 3',
        ]

    async def background(self, client: commands.Bot):
        await client.wait_until_ready()
        global AAR_CH 
        guild = client.get_guild(333429464752979978)
        AAR_CH = guild.get_channel(343795194333757441)

    @app_commands.command(name = 'log', description = 'Log an AAR.')
    @app_commands.checks.has_any_role(333432642878046209, 333432981605580800, 452534405874057217)
    async def aar_log(self, interaction: discord.Interaction, *, type: str, logger: discord.Member = None, bt: str = None, trial: str = None, cohost: discord.Member = None, lead: discord.Member = None, testee: discord.Member = None) -> None:
        if type not in self.types:
            await interaction.response.send_message(content = f'Type *{type}* does not exist. Try again.', ephemeral = True, delete_after = 5)
        else:
            if logger is None:
                logger = interaction.user

            select = Views.MemberSelect()
            log_id = datetime.now().strftime("%H%M%S%d%m%Y")
            embed = discord.Embed(title = "RC Logging Systems", description = f"Logged by {logger.mention}.", timestamp = datetime.now())
            embed.add_field(name = "Log Type", value = type, inline = False)
            embed.set_footer(text = f"LOG ID: {log_id}")

            if type == 'Lead' or type == 'Lead Spectate':
                if type == 'Lead':
                    modal = Modals.LeadModal()
                    await interaction.response.send_modal(modal)
                    embed.colour = discord.Colour.brand_green()
                
                else:
                    if lead is None:
                        await interaction.response.send_message("Please specify who led the event. [`/aar log TYPE:Lead Spectate LEAD:(?)`].", ephemeral = True, delete_after = 15)
                        return 1

                    modal = Modals.LeadSpecModal()
                    await interaction.response.send_modal(modal)
                    embed.colour = discord.Colour.dark_green()
                
                await modal.wait()
                
                await interaction.followup.send(content = 'Please select participants.\n\n> - **NOTE**: *If you need to accidentally forget or click out before you add everyone, use `/aar append` to add users.*', view = select, ephemeral = True)
                await select.wait()
                vals = modal.vals
                members = select.members
                embed.insert_field_at(0, name = "Attendees", value = ' '.join(list(member.mention for member in members)), inline = False)
                embed.add_field(name = "Squad Roles", value = vals['ROLES'], inline = False)
                embed.add_field(name = "Event Summary", value = vals['SUMMARY'], inline = False)
                embed.add_field(name = "Squad Performance", value = vals['PERFORMANCE'], inline = False)
                if type == 'Lead Spectate':
                    embed.insert_field_at(1, name = "Event Lead", value = lead.mention, inline = False)
                    embed.add_field(name = "Lead Evaluation", value = vals['EVAL'], inline = False)
            
                msg = await AAR_CH.send(embed = embed)
                await UTILS.aar_create(str(lead.id) if lead is not None else '', vals['ROLES'], vals['SUMMARY'], vals['PERFORMANCE'], msg_id=msg.id, log_id=log_id, log='Lead' if type == 'Lead' else 'Lead Spectate', logger_id=logger.id, users=list(user.id for user in members))

            elif type == 'Training':
                modal = Modals.TrainingModal()
                await interaction.response.send_modal(modal)
                await modal.wait()
                await interaction.followup.send(content = 'Please select participants.\n\n> - **NOTE**: *If you need to accidentally forget or click out before you add everyone, use `/aar append` to add users.*', view = select, ephemeral = True)
                await select.wait()

                vals = modal.vals
                members = select.members

                embed.colour = discord.Colour.dark_magenta()
                embed.add_field(name = "Attendees", value = ' '.join(list(member.mention for member in members)), inline = False)
                embed.add_field(name = "Cohost", value = cohost.mention if cohost is not None else "No Cohost.", inline = False)
                embed.add_field(name = "Training Type", value = vals['TYPE'], inline = False)
                embed.add_field(name = "Squad Roles", value = vals['ROLES'], inline = False)
                embed.add_field(name = "Training Summary", value = vals['SUMMARY'], inline = False)
                embed.add_field(name = "Squad Performance", value = vals['PERFORMANCE'], inline = False)

                msg = await AAR_CH.send(embed = embed)
                await UTILS.aar_create(vals['TYPE'], str(cohost.id) if cohost is not None else None, vals['ROLES'], vals['SUMMARY'], vals['PERFORMANCE'], msg_id=msg.id, log_id=log_id, log='Training', logger_id=logger.id, users=list(user.id for user in members))

            elif type == 'Lore Activities':
                modal = Modals.LoreModal()
                await interaction.response.send_modal(modal)
                await modal.wait()
                await interaction.followup.send(content = 'Please select participants.\n\n> - **NOTE**: *If you need to accidentally forget or click out before you add everyone, use `/aar append` to add users.*', view = select, ephemeral = True)
                await select.wait()

                vals = modal.vals
                members = select.members

                embed.colour = discord.Colour.gold()
                embed.add_field(name = "Attendees", value = ' '.join(list(member.mention for member in members)), inline = False)
                embed.add_field(name = "Log Type", value = vals['TYPE'], inline = False)
                embed.add_field(name = "Squads", value = vals['SQUADS'], inline = False)
                embed.add_field(name = "Battalions", value = vals['BATTS'], inline = False)
               
                msg = await AAR_CH.send(embed = embed)
                await UTILS.aar_create(vals['TYPE'], vals['SQUADS'], vals['BATTS'], msg_id=msg.id, log_id=log_id, log='Lore Activity', logger_id=logger.id, users=list(user.id for user in members))

            elif type == 'Basic Training':
                if testee is None:
                    await interaction.response.send_message("PVT name not provided. Use the optional `testee` parameter in the `/aar log` command.", ephemeral = True, delete_after = 15)
                    return 1
                if bt is None:
                    await interaction.response.send_message("BT type not provided. Use the optional `bt` parameter in the `/aar log` command.", ephemeral = True, delete_after = 15)
                    return 1
                elif bt not in self.bt:
                    await interaction.response.send_message("BT type unknown. Use the autofill options.", ephemeral = True, delete_after = 15)
                    return 1
                modal = Modals.BTModal()
                await interaction.response.send_modal(modal)
                await modal.wait()
                vals = modal.vals

                embed.colour = discord.Colour.blue()
                embed.add_field(name = "Private", value = testee.mention, inline = False)
                embed.add_field(name = "Training", value = bt, inline = False)
                embed.add_field(name = "Outcome", value = vals['OUTCOME'], inline = False)
                embed.add_field(name = "Additional Information", value = vals['ADD'], inline = False)

                msg = await AAR_CH.send(embed = embed)
                await UTILS.aar_create(str(testee.id), bt, vals['OUTCOME'], msg_id = msg.id, log_id = log_id, log = 'BT', logger_id = logger.id)

            elif type == 'SGT Trials':
                if testee is None:
                    await interaction.response.send_message("CPL name not provided. Use the optional `testee` parameter in the `/aar log` command.", ephemeral = True, delete_after = 15)
                    return 1
                if trial is None:
                    await interaction.response.send_message("Trial type not provided. Use the optional `trial` parameter in the `/aar log` command.", ephemeral = True, delete_after = 15)
                    return 1
                elif trial not in self.trial:
                    await interaction.response.send_message("Trial type unknown. Use the autofill options.", ephemeral = True, delete_after = 15)
                    return 1
                
                modal = Modals.SGTModal()
                await interaction.response.send_modal(modal)
                await modal.wait()
                vals = modal.vals

                embed.colour = discord.Colour.dark_blue()
                embed.add_field(name = "Corporal", value = testee.mention, inline = False)
                embed.add_field(name = "Training", value = trial, inline = False)
                embed.add_field(name = "Outcome", value = vals['OUTCOME'], inline = False)
                embed.add_field(name = "Additional Information", value = vals['ADD'], inline = False)

                msg = await AAR_CH.send(embed = embed)
                await UTILS.aar_create(str(testee.id), trial, vals['OUTCOME'], msg_id = msg.id, log_id = log_id, log = 'SGT Trials', logger_id = logger.id)

            elif type == 'Spec Cert':
                if testee is None:
                    await interaction.response.send_message("Testee name not provided. Use the optional `testee` parameter in the `/aar log` command.", ephemeral = True, delete_after = 15)
                    return 1

                modal = Modals.SpecModal()
                await interaction.response.send_modal(modal)
                await modal.wait()
                vals = modal.vals

                embed.colour = discord.Colour.purple()
                embed.add_field(name = "Testee", value = testee.mention, inline = False)
                embed.add_field(name = "Certification", value = vals['TYPE'], inline = False)
                embed.add_field(name = "Outcome", value = vals['OUTCOME'], inline = False)
                embed.add_field(name = "Additional Information", value = vals['ADD'], inline = False)

                msg = await AAR_CH.send(embed = embed)
                await UTILS.aar_create(str(testee.id), vals['TYPE'], vals['OUTCOME'], msg_id = msg.id, log_id = log_id, log = 'Spec Cert', logger_id = logger.id)

            elif type == 'Tryout':
                modal = Modals.TryoutModal()
                await interaction.response.send_modal(modal)
                await modal.wait()
                await interaction.followup.send(content = 'Please select participants.\n\n> - **NOTE**: *If you need to accidentally forget or click out before you add everyone, use `/aar append` to add users.*', view = select, ephemeral = True)
                await select.wait()    

                vals = modal.vals
                members = select.members

                embed.colour = discord.Colour.teal()
                embed.add_field(name = "Attendees", value = ' '.join(list(member.mention for member in members)), inline = False)
                embed.add_field(name = "Region", value = vals['REGION'], inline = False)
                embed.add_field(name = "Roles", value = vals['ROLES'], inline = False)
                embed.add_field(name = "New Members", value = vals['PASSED'], inline = False)

                msg = await AAR_CH.send(embed = embed)
                await UTILS.aar_create(logger.display_name, vals['REGION'], vals['ROLES'], vals['PASSED'], msg_id = msg.id, log_id = log_id, log = 'Tryout', logger_id = logger.id, users=list(member.id for member in members))

            await interaction.followup.send(content = f"AAR Logged. [Jump!]({msg.jump_url})", ephemeral = True)

    @app_commands.command(name = 'remove', description = 'Remove an AAR')
    @app_commands.checks.has_any_role(333432642878046209, 333432981605580800, 452534405874057217)
    async def aar_remove(self, interaction: discord.Interaction, log_id: int):
        await interaction.response.defer(ephemeral = True)
        msg_id = await UTILS.aar_fetch(log_id)
        msg = await AAR_CH.fetch_message(msg_id)
        await msg.delete()
        try:
            await UTILS.aar_remove(log_id)
        except e.LogNotFound as error:
            await interaction.followup.send(f'{error.__class__.__name__}: {error}', ephemeral = True)
        else:
            await interaction.followup.send(f"Log `{log_id}` has been removed.", ephemeral = True)

    @app_commands.command(name = 'edit', description = 'Edit an AAR.')
    @app_commands.checks.has_any_role(333432642878046209, 333432981605580800, 452534405874057217)
    async def aar_edit(self, interaction: discord.Interaction, log_id: int):
        msg_id = await UTILS.aar_fetch(log_id)
        msg = await AAR_CH.fetch_message(msg_id)
        embed = msg.embeds[0]
        fields = embed.fields
        titles = [field.name for field in fields]
        for index, field in enumerate(fields):
            if field.name == 'Attendees':
                pass
            else:
                embed.set_field_at(index, name = f"[FIELD {index}] {field.name}", value = field.value, inline = False)
        
        await interaction.response.send_message(content = f"*Original AAR* - [Jump!]({msg.jump_url})\n\nPlease select which field you'd like to edit. If you wish to edit squad members, please use `c. aar append` to add, and `c. aar pop` to remove...", embed = embed, view = Views.EditButtons(msg), ephemeral = True, delete_after = 45)
        for index, field in enumerate(fields):
                embed.set_field_at(index, name = f"{titles[index]}", value = field.value, inline = False)
    
    @app_commands.command(name = 'append', description = 'Append a user to the end of an AAR.')
    @app_commands.checks.has_any_role(333432642878046209, 333432981605580800, 452534405874057217)
    async def aar_append(self, interaction: discord.Interaction, log_id: int):
        embed = discord.Embed(title = "AAR Appending Tool", description = "Please select member(s) from below to add to your AAR.\n\n*If you misclick out of the select menu and cancel the command, you can always re-run this command.*", colour = discord.Colour.red())
        select = Views.MemberSelect()
        await interaction.response.send_message(embed = embed, view = select, ephemeral = True)
        await select.wait()
        members = select.members

        try:
            await UTILS.aar_append(log_id, list(str(member.id) for member in members))

        except e.LogNotFound as error:
            await interaction.followup.send(f'{error.__class__.__name__}: {error}', ephemeral = True)

        else:
            msg_id = await UTILS.aar_fetch(log_id)
            msg = await AAR_CH.fetch_message(msg_id)
            embed = msg.embeds[0]
            embed.set_field_at(0, name = embed.fields[0].name, value = f"{embed.fields[0].value}, {' '.join(list(member.mention for member in members))}", inline = False)
            await msg.edit(embed = embed)
            await interaction.followup.send(f'Added {" ".join(list(member.mention for member in members))} to log: `{log_id}`. [ORIGINAL]({msg.jump_url})', ephemeral = True)

    @app_commands.command(name = "pop", description = "Remove a user from an AAR.")
    @app_commands.checks.has_any_role(333432642878046209, 333432981605580800, 452534405874057217)
    async def aar_pop(self, interaction: discord.Interaction, log_id: int, user: discord.Member): # , user: discord.Member
        msg_id = await UTILS.aar_fetch(log_id)
        msg = await AAR_CH.fetch_message(msg_id)
        embed = msg.embeds[0]
        field = embed.fields[0].value

        if f"<@{user.id}" in field:
            field_new = field.replace(f"<@{user.id}>", '')
            embed.set_field_at(0, name = "Attendees", value = field_new, inline = False)
            await msg.edit(embed = embed)
            await interaction.response.send_message(f"Removed {user.mention} from log: `{log_id}`. [ORIGINAL]({msg.jump_url})", ephemeral = True)
            await UTILS.aar_pop(log_id, user.id)

    @aar_log.autocomplete('type')
    async def aar_log_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name = type, value = type)
            for type in self.types if current.lower() in type.lower()
        ]

    @aar_log.autocomplete('bt')
    async def aar_log_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name = bt, value = bt)
            for bt in self.bt if current.lower() in bt.lower()
        ]

    @aar_log.autocomplete('trial')
    async def aar_log_autocomplete(self, interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name = trial, value = trial)
            for trial in self.trial if current.lower() in trial.lower()
        ]
    
class Views:
    class EditButtons(ui.View):
        def __init__(self, msg: discord.Message):
            super().__init__(timeout = 45)
            self.msg = msg
            self.modals = Modals()
        
        @discord.ui.button(label = "Edit", style = discord.ButtonStyle.gray, custom_id = 'persistent:EditButton', disabled = False)
        async def edit_callback(self, interaction: discord.Interaction, button: ui.Button):
            modal = self.modals.EditModal()
            await interaction.response.send_modal(modal)
            await modal.wait()
            
            index, edit = modal.index, modal.resp
            embed = self.msg.embeds[0]
            field_name = embed.fields[index]
            embed.set_field_at(index, name = field_name.name, value = edit, inline = False)
            await self.msg.edit(embed = embed)
            await interaction.followup.send(f"AAR Editted. [Jump!]({self.msg.jump_url})", ephemeral = True)

    class MemberSelect(ui.View):
        def __init__(self, log: str = None, logger: discord.Member = None, *args):
            super().__init__(timeout = 500)
            self.log = log
            self.members = []
        
        @ui.select(
            cls = UserSelect,
            placeholder = 'Select Attendees.',
            min_values = 1,
            max_values = 25
        )
        async def user_select(self, interaction: discord.Interaction, select: UserSelect):
            await interaction.response.defer(ephemeral = True)
            await interaction.delete_original_response()
            self.members = [user for user in select.values]
            self.stop()

class Modals:
    class EditModal(ui.Modal, title = "AAR Editting"):
        def __init__(self):
            super().__init__(timeout = None, custom_id = 'id:EditModal')
            self.index = None
            self.resp = None

        field = ui.TextInput(label = "Field to edit (ONLY THE NUMBER)", style = discord.TextStyle.short, placeholder = "1", required = True)     
        data = ui.TextInput(label = "Please enter your corrections.", style = discord.TextStyle.short, required = True)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer()
            self.index = int(self.field.value)
            self.resp = self.data.value
            self.stop()
    
    class LeadModal(ui.Modal, title = "Lead Logging"):
        def __init__(self):
            super().__init__(timeout = None)
            self.custom_id = "id:LeadModal"
            self.vals = {}

        lead_type = ui.TextInput(label = "Event Type", style = discord.TextStyle.short, placeholder = "i.e S1 Main, S2 Mini...", required = True)
        squad_roles = ui.TextInput(label = "Squad Roles", style = discord.TextStyle.short, required = True)
        summary = ui.TextInput(label = "BRIEF Event Summary", style = discord.TextStyle.long, required = True)
        performance = ui.TextInput(label = "Squad Performance", style = discord.TextStyle.long, required = True)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral = True)

            self.vals['TYPE'] = self.lead_type.value
            self.vals['ROLES'] = self.squad_roles.value
            self.vals['SUMMARY'] = self.summary.value
            self.vals['PERFORMANCE'] = self.performance.value
            self.stop()

    class LeadSpecModal(ui.Modal, title = "Lead Spectate Logging"):
        def __init__(self):
            super().__init__()
            self.custom_id = "id:LeadSpecModal"
            self.vals = {}

        lead_type = ui.TextInput(label = "Event Type", style = discord.TextStyle.short, placeholder = "i.e S1 Main, S2 Mini...", required = True)
        squad_roles = ui.TextInput(label = "Squad Roles", style = discord.TextStyle.short, required = True)
        summary = ui.TextInput(label = "BRIEF Event Summmary", style = discord.TextStyle.long, required = True)
        performance = ui.TextInput(label = "Squad Performance", style = discord.TextStyle.long, required = True)
        evaluation = ui.TextInput(label = "Lead Evaluation", style = discord.TextStyle.long, required = True)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral = True)

            self.vals['TYPE'] = self.lead_type.value
            self.vals['ROLES'] = self.squad_roles.value
            self.vals['SUMMARY'] = self.summary.value
            self.vals['PERFORMANCE'] = self.performance.value
            self.vals['EVAL'] = self.evaluation.value
            self.stop()  

    class TrainingModal(ui.Modal, title = "Trainnig Logging"):
        def __init__(self):
            super().__init__()
            self.custom_id = "id:TrainingModal"
            self.vals = {}
        
        training_type = ui.TextInput(label = "Training Type", style = discord.TextStyle.short, required = True)
        squad_roles = ui.TextInput(label = "Squad Roles", style = discord.TextStyle.short, required = True)
        summary = ui.TextInput(label = "BRIEF Training Summmary", style = discord.TextStyle.long, required = True)
        performance = ui.TextInput(label = "Squad Performance", style = discord.TextStyle.long, required = True)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral = True)

            self.vals['TYPE'] = self.training_type.value
            self.vals['ROLES'] = self.squad_roles.value
            self.vals['SUMMARY'] = self.summary.value
            self.vals['PERFORMANCE'] = self.performance.value
            self.stop()  

    class LoreModal(ui.Modal, title = "Lore Squad Logging"):
        def __init__(self):
            super().__init__()
            self.custom_id = "id:LoreModal"
            self.vals = {}

        lore_type = ui.TextInput(label = "Log Type", style = discord.TextStyle.short, required = True)
        squads = ui.TextInput(label = "Squads Involved", style = discord.TextStyle.short, required = True)
        battalions = ui.TextInput(label = "Battalions Involved", style = discord.TextStyle.short, required = True)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral = True)

            self.vals['TYPE'] = self.lore_type.value
            self.vals['SQUADS'] = self.squads.value
            self.vals['BATTS'] = self.battalions.value
            self.stop()

    class BTModal(ui.Modal, title = "Basic Training Logging"):
        def __init__(self):
            super().__init__()
            self.custom_id = "id:BTModal"
            self.vals = {}

        outcome = ui.TextInput(label = "Did the PVT pass or fail?", style = discord.TextStyle.short, placeholder = "Pass | Fail", required = True)
        additional = ui.TextInput(label = "Any notes about their performance?", style = discord.TextStyle.long, required = False)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral = True)

            self.vals['OUTCOME'] = self.outcome.value
            self.vals['ADD'] = self.additional.value if self.additional.value != '' else "No additional comments."
            self.stop()

    class SGTModal(ui.Modal, title = "SGT Trials Logging"):
        def __init__(self):
            super().__init__()
            self.custom_id = "id:SGTModal"
            self.vals = {}

        outcome = ui.TextInput(label = "Did the CPL pass or fail?", style = discord.TextStyle.short, placeholder = "Pass | Fail", required = True)
        additional = ui.TextInput(label = "Any notes about their performance?", style = discord.TextStyle.long, required = False)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral = True)

            self.vals['OUTCOME'] = self.outcome.value
            self.vals['ADD'] = self.additional.value if self.additional.value != '' else "No additional comments."
            self.stop()

    class SpecModal(ui.Modal, title = "Spec Cert Logging"):
        def __init__(self):
            super().__init__()
            self.custom_id = "id:SpecModal"
            self.vals = {}

        cert_type = ui.TextInput(label = "Certification Type", style = discord.TextStyle.short, required = True)
        outcome = ui.TextInput(label = "Did the CPL pass or fail?", style = discord.TextStyle.short, placeholder = "Pass | Fail", required = True)
        additional = ui.TextInput(label = "Any notes about their performance?", style = discord.TextStyle.long, required = False)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral = True)

            self.vals['TYPE'] = self.cert_type.value
            self.vals['OUTCOME'] = self.outcome.value
            self.vals['ADD'] = self.additional.value if self.additional.value != '' else "No additional comments."
            self.stop()

    class TryoutModal(ui.Modal, title = "Tryout Logging"):
        def __init__(self):
            super().__init__()
            self.custom_id = "id:TryoutModal"
            self.vals = {}

        region = ui.TextInput(label = "Region", style = discord.TextStyle.short, required = True)
        roles = ui.TextInput(label = "Tryout Roles", style = discord.TextStyle.short, required = True)
        passed = ui.TextInput(label = "Who Passed?", style = discord.TextStyle.long, required = False)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral = True)

            self.vals['REGION'] = self.region.value
            self.vals['ROLES'] = self.roles.value
            self.vals['PASSED'] = self.passed.value
            self.stop()

async def setup(client: commands.Bot) -> None:
    await client.add_cog(AARs(client))