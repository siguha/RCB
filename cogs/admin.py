import discord
import aiosqlite
import asyncio
import re
from discord.ext import commands
from discord import app_commands

from utilities.sheetutils import SheetUtilities

class Admin(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        super().__init__()
        self.client = client
        self.utils = SheetUtilities.ProfileUtils()
        self.miscUtils = SheetUtilities.MiscUtils()
    
    @commands.hybrid_command(name = "load", with_app_command = False)
    @app_commands.checks.has_any_role(333432981605580800, 452534405874057217)
    async def load(self, ctx: commands.Context, *, module: str):
        """Loads a module."""
        try:
            await self.client.load_extension(module)

        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')

        else:
            await ctx.message.delete()
            await ctx.send('Extension successfully loaded.', delete_after = 5)

    @commands.hybrid_command(name = "unload", with_app_command = False)
    @app_commands.checks.has_any_role(333432981605580800, 452534405874057217)
    async def unload(self, ctx: commands.Context, *, module: str):
        """Unloads a module."""
        try:
            await self.client.unload_extension(module)

        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')

        else:
            await ctx.message.delete()
            await ctx.send('Extension successfully unloaded.', delete_after = 5)

    @commands.hybrid_command(name = "reload", with_app_command = False)
    @app_commands.checks.has_any_role(333432981605580800, 452534405874057217)
    async def _reload(self, ctx: commands.Context, *, module: str):
        """Reloads a module."""
        try:
            await self.client.reload_extension(module)

        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')

        else:
            await ctx.message.delete()
            await ctx.send('Extension successfully reloaded.', delete_after = 5)

    @commands.hybrid_command(name = "sync", with_app_command = False)
    @app_commands.checks.has_any_role(333432981605580800, 452534405874057217)
    async def reload(self, ctx: commands.Context):
        await self.client.tree.sync()
        await ctx.message.delete()
        await ctx.send('Command tree re-synced.', delete_after = 5)

    @commands.hybrid_command(name="jax", with_app_command=False)
    async def jax(self, ctx: commands.Context):
        await ctx.message.delete()
        await ctx.channel.send("https://tenor.com/view/star-wars-yeet-darth-vader-fallen-order-jedi-gif-24487821")

    @commands.hybrid_command(name="spec_aar", with_app_command=False)
    async def spec(self, ctx: commands.Context):
        await ctx.channel.send("## Logging a Spec AAR?\nGo into <#343795194333757441> and type `/aar`.\n\nSelect **Spec Certs** and **testee** as the optional parameter. Select whoever the testee was in the member select menu that pops up above.\n\nFill out the logging form as directed, and done.\n\n*If you make a mistake, you'll need to contact an NCO+ to get it fixed, alongside the necessary corrections.")

    @commands.hybrid_command(name="jedi_aar", with_app_command=False)
    async def lore(self, ctx: commands.Context):
        await ctx.channel.send("## Logging a Lore AAR?\nGo into <#343795194333757441> and type `/aar`.\n\nSelect **Lore Activities**.\n\nFill out the logging form as directed.\n\nSelect the participants, being the RC present. If it was just yourself, you can select only yourself as the participant.\n\n*If you make a mistake, you'll need to contact an NCO+ to get it fixed, alongside the necessary corrections.")       

    @commands.hybrid_command(name="retention", with_app_command=False)
    async def retention(self, ctx: commands.Context):
        data = await self.miscUtils.retention_fetch()

        await ctx.channel.send(f"# Retention Stats\n**Analysis Period**: __{data['date']} - {data['date_old']}__\n- **Headcount**: `{data['headcount']}`\n- **Prev. Headcount**: `{data['headcount_old']}`\n\n**Retention Rate**: `{data['retention']}`")

    @commands.hybrid_command(name="chaind", with_app_command=False)
    @app_commands.checks.has_any_role(333432981605580800, 452534405874057217)
    async def chain_delete(self, ctx: commands.Context, *args: int):
        try:
            if args[0] <= 100:
                await ctx.channel.purge(limit=args[0])
                await ctx.send(f"Deleting the last **{args[0]}** Messages from cur. channel.", delete_after=15)

            else:
                not_found = []
                not_found_count = 0

                for arg in args:
                    try:
                        message = await ctx.fetch_message(arg)
                        await message.delete()

                    except Exception as e:
                        not_found_count += 1
                        not_found.append(f'\n- `{arg}: {e.__class__.__name__}`')
                
                deleted_count = len(args) - not_found_count
                
                await ctx.send(f"**{len(args)}** Message IDs processed, **{deleted_count if deleted_count > 0 else 0}** Messages deleted, **{not_found_count}** Message IDs not found.\n\n{''.join(not_found)}", delete_after=15)
        except:
            await ctx.send("Invalid command usage. `!chaind *MSG IDs/Purge Count`.")
            
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Admin(client))