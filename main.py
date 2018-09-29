from traceback import format_exception
from os import listdir
from json import load, dump
from discord.ext import commands

from data.token import token

try:
    config = load(open("data/config.json"))
except:
    config = {"prefix": ["!"], "avatar":""}

    with open("data/config.json", "w") as conf:
        dump(config, conf)

bot = commands.Bot(command_prefix=config['prefix'])


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
    try:
        cogs = load(open("data/cogs.json"))
    except:
        cogs = {"all": ["cogs.core"], "loaded": {"core": "cogs.core"}}

        with open("data/cogs.json", "w") as conf:
            dump(cogs, conf)

    temp = cogs.copy()

    cogs['all'] = list(set(cogs['all'] + ['cogs.' + x[:-3] for x in listdir("cogs")
                                          if x != "__pycache__" and x.endswith(".py")]))

    for cog in cogs['all']:
        try:
            __import__(cog)
        except ModuleNotFoundError:
            cogs['all'].remove(cog)

    for cog in list(cogs['loaded'].items()):
        try:
            bot.load_extension(cog[1])
        except Exception as e:
            cogs['loaded'].pop(cog[0])
            print("Failed to load {}:\n{} : {}".format(
                cog[0], type(e).__name__, e))

    if temp != cogs:
        with open("data/cogs.json", "w") as conf:
            dump(cogs, conf)

    print("{} has started\n"
          "{} Servers\n"
          "{} Cogs\n"
          "{} loaded\n"
          "prefixes:\n{}"
          "".format(bot.user.name, len(bot.guilds),
                    len(cogs['all']), len(cogs['loaded']), " ".join(config["prefix"])))

if __name__ == "__main__":
    try:
        bot.run(token)
    except KeyboardInterrupt:
        bot.logout()
        print("\n")
