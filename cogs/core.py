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

    @commands.command()
    @checks.is_owner()
    async def cogs(self, ctx):
        """
        Show loaded and unloaded cogs
        loaded cogs show the name they were assigned by a load function
        unloaded cogs show known cogs. that exist
        """
        cogs = load(open("data/cogs.json"))

        loaded = ", ".join(cogs['loaded'])
        unloaded = ", ".join(
            [y[5:] for y in cogs['all'] if not y[5:] in cogs['loaded']])

        message = ("+ Loaded\n"
                   "{}\n"
                   "- Unloaded\n"
                   "{}"
                   "".format(loaded, unloaded)
                   )

        for x in ["```diff\n" + message[i:i + 1989] + "```" for i in range(0, len(message), 1989)]:
            await ctx.send(x)

    @commands.command(aliases=["reload"])
    @checks.is_owner()
    async def load(self, ctx, *, cog: str):
        """Load a cog"""

        cogs = load(open("data/cogs.json"))

        try:
            self.bot.unload_extension("cogs." + cog)
            self.bot.load_extension("cogs." + cog)
            cogs['loaded'].update({cog: "cogs." + cog})
            with open("data/cogs.json", "w") as config:
                dump(cogs, config)
            await ctx.send(cog + " loaded")
        except ModuleNotFoundError:
            await ctx.send("Cog not found")
            return
        except Exception as e:
            await ctx.send("Failed to load {}:\n{} : {}".format(
                cog, type(e).__name__, e))
            return

    @commands.command()
    @checks.is_owner()
    async def unload(self, ctx, *, cog: str):
        """Unload a cog"""

        cogs = load(open("data/cogs.json"))

        if cog == "core":
            await ctx.send("Cannot unload core")
            return

        try:
            self.bot.unload_extension(cogs['loaded'][cog])
            cogs['loaded'].pop(cog)
            with open("data/cogs.json", "w") as config:
                dump(cogs, config)
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

        botmodules = load(open("data/modules.json"))

        try:
            import_module('modules.{}.init'.format(module))
            botmodules['loaded'].append(module)
            with open("data/modules.json", "w") as conf:
                dump(botmodules, conf)
            await ctx.send(module + " loaded")
        except Exception as e:
            await ctx.send("Failed to load {}:\n{} : {}".format(module, type(e).__name__, e))
            return

    @modules.group(name="unload")
    @checks.is_owner()
    async def moduleunload(self, ctx, *, module: str):
        """
        Unload a module
        Requires restarting the bot to take affect
        """

        botmodules = load(open("data/modules.json"))

        try:
            botmodules['loaded'].remove(module)
            with open("data/modules.json", "w") as conf:
                dump(botmodules, conf)
            await ctx.send(module + " remove from autoloading\nRestart for it to take affect")
        except ValueError:
            if module in botmodules['all']:
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
        """Change the prefix"""

        config = load(open("data/config.json"))
        config['prefix'] = prefix.split()

        with open("data/config.json", "w") as conf:
            dump(config, conf)

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
