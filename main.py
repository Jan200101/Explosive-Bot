from traceback import format_exception
from os import listdir
from json import load, dump


from discord.ext import commands

from data.config import prefix, token


bot = commands.Bot(command_prefix=prefix)


class Cog:
    def __init__(self):
        self.all = []
        self.loaded = {}
        self.unloaded = []


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.errors.CommandNotFound, commands.errors.CheckFailure)):
        return
    elif isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        helpm = await bot.formatter.format_help_for(ctx, ctx.command)
        for m in helpm:
            await ctx.send(m)
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.message.channel.send("{} This command was used {:.2f}s ago and is on "
                                       "cooldown. Try again in {:.2f}s."
                                       "".format(ctx.message.author.mention,
                                                 error.cooldown.per - error.retry_after,
                                                 error.retry_after))
    else:
        exception_log = "Exception in command '{}'\n" "".format(
            ctx.command.qualified_name)
        exception_log += "".join(
            format_exception(type(error), error, error.__traceback__)
        )
        print(exception_log)


@bot.event
async def on_ready():

    bot.cog = Cog
    bot.cog.all = [x for x in listdir("cogs") if x != "__pycache__"]

    try:
        cogs = load(open("data/cogs.json"))
    except:
        cogs = [
            "core"
        ]

        with open("data/cogs.json", "w") as config:
            dump(cogs, config)

    temp = cogs.copy()

    for cog in cogs:
        try:
            bot.load_extension("cogs." + cog)
            bot.cog.loaded.update({cog: "cogs." + cog})
        except Exception as e:
            print("Failed to load {}:\n{} : {}".format(
                cog, type(e).__name__, e))
            cogs.remove(cog)
            print(cogs)

    if temp != cogs:
        with open("data/cogs.json", "w") as config:
            dump(cogs, config)

    bot.cog.unloaded = [
        x for x in bot.cog.all if not x in list(bot.cog.loaded)]

    print("{} has started\n"
          "{} Servers\n"
          "{} Cogs\n"
          "{} loaded\n"
          "prefixes:\n{}"
          "".format(bot.user.name, len(bot.guilds),
                    len(bot.cog.all), len(bot.cog.loaded), " ".join(prefix)))

if __name__ == "__main__":
    try:
        bot.run(token)
    except KeyboardInterrupt:
        bot.logout()
        print("\n")
