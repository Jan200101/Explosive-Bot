from traceback import format_exception
from importlib import import_module
from os import execl
from sys import argv, executable
from aiohttp import ClientSession
from discord.errors import HTTPException
from discord.ext import commands

from cogs.utils import checks
from cogs.utils.data import Data


class Core(commands.Cog):
    """Core commands"""

    def __init__(self, bot):
        self.bot = bot

        self.cogs = Data("data/cogs.json")
        self.botmodules = Data("data/modules.json")
        self.config = Data("data/config.json")

    @commands.command(name="cogs")
    @commands.is_owner()
    async def cogslist(self, ctx):
        """
        Show loaded and unloaded cogs
        loaded cogs show the name they were assigned by a load function
        unloaded cogs show known cogs. that exist
        """

        loaded = ", ".join(self.cogs['loaded'])
        unloaded = ", ".join(
            [y[5:] for y in self.cogs['all'] if not y[5:] in self.cogs['loaded']])

        content = ("+ Loaded\n"
                   "{}\n"
                   "- Unloaded\n"
                   "{}"
                   "".format(loaded, unloaded)
                   )

        for message in [content[i:i + 1989] for i in range(0, len(content), 1989)]:
            await ctx.send("```diff\n" + message + "```")

    @commands.command(name="load", aliases=["reload"])
    @commands.is_owner()
    async def cogsload(self, ctx, *, cog: str):
        """Load a cog"""

        try:
            try:
                self.bot.unload_extension("cogs." + cog)
            except commands.errors.ExtensionNotLoaded:
                pass
            self.bot.load_extension("cogs." + cog)
            self.cogs['loaded'].update({cog: "cogs." + cog})
            self.bot.logger.info(cog + " loaded")
            self.cogs.save()
            await ctx.send(cog + " loaded")
        except ModuleNotFoundError:
            await ctx.send("Cog not found")
            self.bot.logger.info(cog + " not found")
            return
        except Exception as error:
            self.bot.logger.warn("Failed to load {}: {}".format(cog[0], "".join(
                format_exception(type(error), error, error.__traceback__))))
            await ctx.send("A error has occured loading {}\n"
                           "Check the console or the logs".format(cog))

    @commands.command(name="unload")
    @commands.is_owner()
    async def cogsunload(self, ctx, *, cog: str):
        """Unload a cog"""

        if cog == "core":
            await ctx.send("Cannot unload core")
            return

        try:
            self.bot.unload_extension(self.cogs['loaded'][cog])
            self.cogs['loaded'].pop(cog)
            self.bot.logger.info(cog + " unloaded")
            self.cogs.save()
            await ctx.send(cog + " unloaded")
        except KeyError:
            self.bot.unload_extension("cogs." + cog)
            self.bot.logger.info(cog + " unload attempted")
            await ctx.send(cog + " not loaded, attempting unload anyways")

    @commands.group()
    @commands.is_owner()
    async def modules(self, ctx):
        """Manage bot modules"""

        if ctx.invoked_subcommand is None:
            pages = await self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    @modules.group(name="load")
    @commands.is_owner()
    async def moduleload(self, ctx, *, module: str):
        """Load a module"""

        try:
            import_module('modules.{}'.format(module)).init()
            self.botmodules['loaded'].append(module)
            self.bot.logger.info(module + " loaded")
            self.botmodules.save()
            await ctx.send(module + " loaded")
        except Exception as error:
            self.bot.logger.warn("A error occured in {}: {}".format(module, "".join(
                format_exception(type(error), error, error.__traceback__))))
            await ctx.send("A error has occured loading {}\n"
                           "Check the console or the logs".format(module))

    @modules.group(name="unload")
    @commands.is_owner()
    async def moduleunload(self, ctx, *, module: str):
        """
        Unload a module
        """

        try:
            self.botmodules['loaded'].remove(module)
            import_module('modules.{}'.format(module)).destroy()
            self.bot.logger.info(module + " unloaded")
            self.botmodules.save()
            await ctx.send(module + " unloaded")
        except ValueError:
            if module in self.botmodules['all']:
                await ctx.send(module + " is not loaded")
                self.bot.logger.info(module + " not loaded")
            else:
                await ctx.send("No such module")
                self.bot.logger.info(module + " not found")

    @modules.group(name="list")
    @commands.is_owner()
    async def moduleslist(self, ctx):
        """
        Show loaded and unloaded modules
        """

        loaded = ", ".join(self.botmodules['loaded'])
        unloaded = ", ".join(
            [y for y in self.botmodules['all'] if not y[5:] in self.botmodules['loaded']])

        content = ("+ Loaded\n"
                   "{}\n"
                   "- Unloaded\n"
                   "{}"
                   "".format(loaded, unloaded)
                   )

        for message in [content[i:i + 1989] for i in range(0, len(content), 1989)]:
            await ctx.send("```diff\n" + message + "```")

    @commands.group(name="set")
    @checks.is_mod()
    async def settings(self, ctx):
        """Change bot setting"""

        if ctx.invoked_subcommand is None:
            pages = await self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    @settings.command()
    @checks.is_mod()
    async def avatar(self, ctx, *, url: str):
        """Change the avatar"""

        try:
            session = ClientSession(loop=self.bot.loop)
            async with session.get(url) as data:
                image = await data.read()
            await session.close()
            await self.bot.user.edit(avatar=image)
            await ctx.send("Done")
            self.config['avatar'] = url

            self.bot.logger.info("Changed avatar")
        except HTTPException:
            await ctx.send("Trying to change the avatar too fast. Try again later")
        except Exception as err:
            self.bot.logger.warn("Error: {}".format(
                "".join(format_exception(type(err), err, err.__traceback__))))

    @settings.command()
    @commands.guild_only()
    @checks.is_mod()
    async def prefix(self, ctx, *, prefix: str):
        """
        Set the guild prefix
        Seperate multiple prefixes with a space
        set prefix to None to use the global prefix
        """

        guild = ctx.message.guild

        if prefix.lower() == "none":
            prefix = None
            self.bot.logger.info("[{}]Reset Guild prefix".format(guild.name))
            await ctx.send("Reset prefix")
        else:
            prefix = prefix.split()
            self.bot.logger.info("[{}]Guild prefix set to {}".format(
                guild.name, " ".join(prefix)))
            await ctx.send("Prefix changed to " + " ".join(prefix))

        self.bot.settings.setprefix(guild.id, prefix)

    @settings.group()
    @commands.is_owner()
    async def roles(self, ctx):
        """Change global settings"""

        if ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group):
            pages = await self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    @roles.group(name="admin")
    @commands.is_owner()
    async def admin(self, ctx, rolename: str):
        """Set admin role"""

        guild = ctx.message.guild

        await ctx.send("admin role changed to " + " ".join(rolename))

        self.bot.settings.setadminrole(guild.id, rolename)

    @roles.group(name="mod", aliases=["moderator"])
    @commands.is_owner()
    async def mod(self, ctx, rolename: str):
        """Set mod role"""

        guild = ctx.message.guild

        await ctx.send("moderator role changed to " + " ".join(rolename))

        self.bot.settings.setmoderatorrole(guild.id, rolename)

    @settings.group(name="global")
    @commands.is_owner()
    async def _global(self, ctx):
        """Change global settings"""
        if ((ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group))
                and ctx.invoked_subcommand.name and ctx.invoked_subcommand.name == "global"):
            pages = await self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    @_global.command(name="prefix")
    @commands.is_owner()
    async def globalprefix(self, ctx, *, prefix: str):
        """
        Set the global prefix
        Seperate multiple prefixes with a space
        """

        prefix = prefix.split()

        self.bot.settings.setprefix("DEFAULT", prefix)

        self.bot.logger.info(
            "Global prefix set to {}".format(" ".join(prefix)))
        await ctx.send("Prefix changed to " + " ".join(prefix))

    @_global.group(name="roles")
    @commands.is_owner()
    async def globalroles(self, ctx):
        """Change global settings"""

        if ((ctx.invoked_subcommand is None or isinstance(ctx.invoked_subcommand, commands.Group))
                and ctx.invoked_subcommand.name == "roles"):
            pages = await self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    @globalroles.group(name="admin")
    @commands.is_owner()
    async def globaladmin(self, ctx, rolename: str):
        """Set global admin role"""

        await ctx.send("global admin role changed to " + " ".join(rolename))
        self.bot.settings.setadminrole("DEFAULT", rolename)

    @globalroles.group(name="mod", aliases=["moderator"])
    @commands.is_owner()
    async def globalmod(self, ctx, rolename: str):
        """Set global moderator role"""

        await ctx.send("global moderator role changed to " + " ".join(rolename))
        self.bot.settings.setadminrole("DEFAULT", rolename)

    @commands.command(name="exit", aliases=["shutdown"])
    @commands.is_owner()
    async def _exit(self, ctx):
        """Shutdown the bot"""

        await ctx.send("Bye")
        self.bot.logger.info(
            "Bot shutdown via command by {}".format(ctx.message.author))
        await self.bot.logout()

    @commands.command()
    @commands.is_owner()
    async def restart(self, ctx):
        """Restart the bot"""

        await ctx.send("Restarting...")
        self.bot.logger.info(
            "Bot restart via command by {}".format(ctx.message.author))
        execl(executable, 'python', *argv)


def setup(bot):
    bot.add_cog(Core(bot))
