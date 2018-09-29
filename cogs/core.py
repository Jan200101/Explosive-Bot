from os import execl
from sys import argv, executable
from json import load, dump
from discord.ext import commands


class Core:
    """Core commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["reload"])
    async def load(self, ctx, *, cog):
        """Load a cog"""

        cogs = load(open("data/cogs.json"))

        try:
            self.bot.unload_extension("cogs." + cog)
            self.bot.load_extension("cogs." + cog)
            cogs['loaded'].update({cog: "cogs." + cog})
        except ModuleNotFoundError:
            await ctx.send("Cog not found")
            return
        except Exception as e:
            await ctx.send("Failed to load {}:\n{} : {}".format(
                cog, type(e).__name__, e))
            return

        cogs['loaded'].update({cog: 'cogs.' + cog})

        with open("data/cogs.json", "w") as config:
            dump(cogs, config)

        await ctx.send("{} loaded".format(cog))

    @commands.command()
    async def unload(self, ctx, *, cog):
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
            await ctx.send("{} unloaded".format(cog))
        except KeyError:
            self.bot.unload_extension("cogs." + cog)
            await ctx.send("{} not loaded, attempting unload anyways".format(cog))

    @commands.group(name="set")
    async def settings(self, ctx):
        """Change bot setting"""

        if ctx.invoked_subcommand is None:
            pages = await self.bot.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                await ctx.send(page)

    @settings.command()
    async def prefix(self, ctx, *, prefix: str):
        """Change the prefix"""

        config = load(open("data/config.json"))
        config['prefix'] = prefix.split()

        with open("data/config.json", "w") as conf:
            dump(config, conf)

        await ctx.send("Prefix set\nRestart to apply it")

    @commands.command(name="exit", aliases=["shutdown"])
    async def _exit(self, ctx):
        """Shutdown the bot"""

        await ctx.send("Bye")
        await self.bot.logout()

    @commands.command()
    async def restart(self, ctx):
        """Restart the bot"""

        await ctx.send("Restarting...")
        execl(executable, 'python', "main.py", *argv[1:])


def setup(bot):
    bot.add_cog(Core(bot))
