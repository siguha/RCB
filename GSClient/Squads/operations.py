import gspread
import discord
import random
import datetime

from GSClient import DATABASE, utilities

class SquadOperations:
    def __init__(self, database_manager):
        self.db = database_manager

    async def squad_rename(self, guild: discord.Guild, squad: str, name: str, color: str = None):
        cursor = self.db.get_cursor()
        await cursor.execute('''SELECT * FROM squads WHERE name = ?''', (squad.capitalize(),))
        data = await cursor.fetchone()

        if data is None:
            raise ValueError(f"Squad {squad} not found.")
        
        else:
            await cursor.execute('''UPDATE squads SET name = ? WHERE name = ?''', (name.capitalize(), squad.capitalize()))

        await self.db.connection.commit()

        role = guild.get_role(data[1])
        channel = guild.get_channel(data[2])
        await role.edit(name=f"{name.capitalize()} Squad", colour = discord.Colour.from_str(color) if color is not None else discord.Colour.default())
        await channel.edit(name=f"{name.lower()}-squad")

    async def squad_builder(self, guild: discord.Guild) -> None:
        squad_list = list(set([item for sublist in DATABASE.get("E4:E") for item in sublist if item]))
        user_list = [user for user in DATABASE.get("E4:G") if user[0]]   
        cursor = self.db.get_cursor()

        enlisted_role = guild.get_role(333432571201585152)
        nco_role = guild.get_role(333432642878046209)
        officer_role = guild.get_role(333432981605580800)

        for squad in squad_list:
            placeholder = []

            for user in user_list:
                try:
                    if squad in user:
                        placeholder.append(int(user[2]))

                except ValueError:
                    pass

            for user in user_list:
                if squad in user:
                    try:
                        placeholder.append(int(user[2]))

                    except ValueError:
                        pass

            if len(placeholder) < 3:
                continue
            
            else:
                while len(placeholder) < 5:
                    placeholder.append(None)

                # If squad channel already exist.
                if discord.utils.get(guild.channels, name=f"{squad.lower()}-squad") is not None:
                    cursor = await self.db.get_cursor()
                    await cursor.execute('''SELECT mem1, mem2, mem3, mem4, mem5 FROM squads WHERE name = ?''', (squad,))
                    existing = await cursor.fetchone()

                    await cursor.execute('''INSERT INTO squads (name, role, channel, mem1, mem2, mem3, mem4, mem5, persistent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        ON CONFLICT(name) DO
                                        UPDATE SET mem1 = excluded.mem1, mem2 = excluded.mem2, mem3 = excluded.mem3, mem4 = excluded.mem4, mem5 = excluded.mem5, persistent = excluded.persistent
                                        ''', (squad, None, None, placeholder[0], placeholder[1], placeholder[2], placeholder[3], placeholder[4], "no"))
                
                    await self.db.connection.commit()

                    squad_role = discord.utils.get(guild.roles, name=f"{squad} Squad")

                    try:
                        for id in existing:
                            try:
                                if id is not None:
                                    if id not in placeholder:
                                        print(f"ID NOT FOUND: {id} - {guild.get_member(int(id)).display_name}\n")
                                        member = guild.get_member(id)

                                        rank = "SRE" if enlisted_role in member.roles else "SRN" if nco_role in member.roles else "SRO" if officer_role in member.roles else None
                                        member_name = member.display_name.split(" | ")[0]
                                        member_designation = member.display_name.split(" | ")[1].split(" ")[1]
                                        new_name = f"{member_name} | {rank} {member_designation}"

                                        await member.edit(nick=new_name)
                                        await guild.get_member(int(id)).remove_roles(squad_role)

                            except AttributeError:
                                print(f"ID NOT EXISTS: {id}")
                    
                    except ValueError as e:
                        print(f'{e.__class__.__name__}: {e}')
                        pass
                
                # If squad channel doesn't already exist.
                else:
                    squad_role = await guild.create_role(name=f"{squad.capitalize()} Squad")
                    cat = discord.utils.get(guild.categories, id=1164281181529985044)
                    overwrites = {
                        guild.default_role: discord.PermissionOverwrite(view_channel=False, read_messages=False),
                        squad_role: discord.PermissionOverwrite(view_channel=True, read_messages=True),
                        guild.get_role(842312625735860255): discord.PermissionOverwrite(view_channel=True, read_messages=True),
                        guild.get_role(1205615781027782736): discord.PermissionOverwrite(view_channel=True, read_messages=True),
                        guild.get_role(333432981605580800): discord.PermissionOverwrite(view_channel=True, read_messages=True, manage_channels=True),
                    }
                    squad_ch = await cat.create_text_channel(name=f"{squad.lower()}-squad", overwrites=overwrites)
                    await squad_ch.send(f"# {squad}'s Communication Frequency\n### FREQUENCY HASH CODE #03-{random.randint(1,999)}-{random.randint(1000,9999)}\n\n<@&{squad_role.id}> - Welcome to your communications hub, a channel frequency provided to you by the 03 Commando Battalion. This is where you'll communicate amongst yourselves.\n\nThis frequency will be scrambled after:\n- **Two weeks of message inactivity + having less than 3 squad members.**\n- **Dropping to 0 squad members.**\n\nOne of the luxuries provided to you is the ability to take the **Commando Squad Exam**, hosted and advised by our <@&1205615781027782736>'s. Satisfactory performance will grant you a custom **squad name**, **role icon** and **role color**. If you'd like to schedule an exam, please speak with the Advisors.\n\nIf you have questions, please contact an <@&842312625735860255>+.")

                    cursor = await self.db.get_cursor()
                    await cursor.execute('''INSERT INTO squads (name, role, channel, mem1, mem2, mem3, mem4, mem5, persistent) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                                        ON CONFLICT(name) DO
                                        UPDATE SET name = excluded.name, role = excluded.role, channel = excluded.channel, mem1 = excluded.mem1, mem2 = excluded.mem2, mem3 = excluded.mem3, mem4 = excluded.mem4, mem5 = excluded.mem5, persistent = excluded.persistent
                                        ''', (squad, squad_role.id, squad_ch.id, placeholder[0], placeholder[1], placeholder[2], placeholder[3], placeholder[4], "no"))  

                    await self.db.connection.commit()

                for id in placeholder:
                    if id is not None:
                        try:
                            member = guild.get_member(id)
                            member_name = member.display_name.split(" | ")[0]
                            member_designation = member.display_name.split(" | ")[1].split(" ")[1]
                            new_name = f"{member_name} | {squad.capitalize()} {member_designation}"
                            await member.edit(nick=new_name)
                            await member.add_roles(squad_role)

                        except:
                            pass

        await self.db.connection.commit()
        await self.squad_checker(guild)

        async def squad_checker(self, guild: discord.Guild) -> None:
            db = await aiosqlite.connect('rcb.db')
            _active_squad_list = list(set([item for sublist in DATABASE.get("E4:E") for item in sublist if item]))
            _deleted = []

            async with db.cursor() as cursor:
                await cursor.execute('''SELECT * FROM squads''')
                _old_squad_list = await cursor.fetchall()

                await cursor.close()

            for squad in _old_squad_list:
                role = guild.get_role(int(squad[1]))
                channel = guild.get_channel(int(squad[2]))

                if squad[8] == "yes":
                    pass

                else:
                    if squad[0] not in _active_squad_list:
                        try:
                            await role.delete(reason="Squad is empty.")
                        
                        except: pass
                        try:
                            await channel.delete(reason="Squad is empty.")
                            _deleted.append(f"{squad[0]} - Squad is Empty.\n")
                        
                        except: pass

                        async with db.cursor() as cursor:
                                await cursor.execute('''DELETE FROM squads WHERE name = ?''', (squad[0],))
                                await db.commit()             
                    
                    else:
                        async for message in channel.history(limit=1):
                            date = message.created_at
                            today = datetime.datetime.now(datetime.timezone.utc)
                            delta = today - date

                        if int(delta.days) >= 14:
                            member_count = squad.count(None)

                            if member_count <= 2:
                                await channel.delete(reason="2 Week+ Inactivity -2 Members.")
                                await role.delete(reason="2 Week+ Inactivity -2 Members.")
                                _deleted.append(f"{squad[0]} - 2 Week+ Inactivity -2 Members.\n")

                                async with db.cursor() as cursor:
                                        await cursor.execute('''DELETE FROM squads WHERE name = ?''', (squad[0],))
                                        await db.commit()
                
            sgm_channel = guild.get_channel(946095177695653988)
            if len(_deleted) == 0:
                pass
            else:
                await sgm_channel.send(content=f"# Channel Purge\n\nThe following channels were purged either for inactivity or zero memebers:\n\n {', '.join(_deleted)}\n\n**If this was a mistake, please ping Officer+.**")
            await db.close()
