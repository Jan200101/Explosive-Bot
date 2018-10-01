from importlib import import_module
from os import execl
from sys import argv, executable
from json import load, dump
from discord.ext import commands

from cogs.utils import checks


class Core:
    """Core commands"""

    def __init__(self, bot):
        self.bot = bot

        self.cogs = load(open("data/cogs.json"))
        self.botmodules = load(open("data/modules.json"))
        self.config = load(open("data/config.json"))

    @commands.command(name="cogs")
    @checks.is_owner()
    async def _cogs(self, ctx):
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

    @commands.command(aliases=["reload"])
    @checks.is_owner()
    async def load(self, ctx, *, cog: str):
        """Load a cog"""

        try:
            self.bot.unload_extension("cogs." + cog)
            self.bot.load_extension("cogs." + cog)
            self.cogs['loaded'].update({cog: "cogs." + cog})
            with open("data/cogs.json", "w") as config:
                dump(self.cogs, config)
            await ctx.send(cog + " loaded")
        except ModuleNotFoundError:
            await ctx.send("Cog not found")
            return
        except Exception as error:
            await ctx.send("Failed to load {}:\n{} : {}".format(
                cog, type(error).__name__, error))
            return

    @commands.command()
    @checks.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Unload a cog"""

        if cog == "core":
            await ctx.send("Cannot unload core")
            return

        try:
            self.bot.unload_extension(self.cogs['loaded'][cog])
            self.cogs['loaded'].pop(cog)
            with open("data/cogs.json", "w") as config:
                dump(self.cogs, config)
            await ctx.send(cog + " unloaded")
        except KeyError:
            self.bot.unload_extension("cogs." + cog)
            await ctx.send(cog + " not loaded, attempting unload anyways")

    @commands.group()
    @checks.is_owner()
    async def modules(self, ctx):
        """Manage bot modules"""

        if ctx.invoked_subcommand is None:
            pages = await self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    @modules.group(name="load")
    @checks.is_owner()
    async def moduleload(self, ctx, *, module: str):
        """Load a module"""

        try:
            import_module('modules.{}.init'.format(module))
            self.botmodules['loaded'].append(module)
            with open("data/modules.json", "w") as conf:
                dump(self.botmodules, conf)
            await ctx.send(module + " loaded")
        except Exception as error:
            await ctx.send("Failed to load {}:\n{} : {}".format(
                module, type(error).__name__, error))
            return

    @modules.group(name="unload")
    @checks.is_owner()
    async def moduleunload(self, ctx, *, module: str):
        """
        Unload a module
        Requires restarting the bot to take affect
        """

        try:
            self.botmodules['loaded'].remove(module)
            with open("data/modules.json", "w") as conf:
                dump(self.botmodules, conf)
            await ctx.send(module + " remove from autoloading\nRestart for it to take affect")
        except ValueError:
            if module in self.botmodules['all']:
                await ctx.send(module + " is not loaded")
            else:
                await ctx.send("No such module")

    @commands.group(name="set")
    @checks.is_owner()
    async def settings(self, ctx):
        """Change bot setting"""

        if ctx.invoked_subcommand is None:
            pages = await self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    @settings.command()
    @checks.is_owner()
    async def prefix(self, ctx, *, prefix: str):
        """Set the prefix"""

        self.config['prefix'] = prefix.split()

        with open("data/config.json", "w") as conf:
            dump(self.config, conf)

        await ctx.send("Prefix set\nRestart to apply it")

    @commands.command(name="exit", aliases=["shutdown"])
    @checks.is_owner()
    async def _exit(self, ctx):
        """Shutdown the bot"""

        await ctx.send("Bye")
        await self.bot.logout()

    @commands.command()
    @checks.is_owner()
    async def restart(self, ctx):
        """Restart the bot"""

        await ctx.send("Restarting...")
        execl(executable, 'python', "main.py", *argv[1:])


def setup(bot):
    bot.add_cog(Core(bot))
