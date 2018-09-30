from traceback import format_exception
from argparse import ArgumentParser
from importlib import import_module
from os import listdir
from os.path import isdir, isfile
from json import load, dump
from discord.ext import commands

from data.token import token

try:
    config = load(open("data/config.json"))
except:
    config = {"prefix": ["!"], "avatar": ""}

    with open("data/config.json", "w") as conf:
        dump(config, conf)

bot = commands.Bot(command_prefix=config['prefix'])


def parse_cmd_arguments():
    parser = ArgumentParser(description="Explosive-Bot")
    parser.add_argument("-c", "--concise",
                        action="store_true",
                        help="Gives full traceback")
    return parser

args = parse_cmd_arguments().parse_args()


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
        if args.concise:
            exception_log += "".join(
                format_exception(type(error), error, error.__traceback__)
            )
        else:
            exception_log += "".join(
                format_exception(type(error), error)
            )
        print(exception_log)


@bot.event
async def on_ready():
    # Set Variables
    info = await bot.application_info()

    bot.owner = info.owner.id
    bot.client_id = info.owner
    bot.oauth_url = "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot".format(
        bot.client_id)

    # Load Modules
    try:
        botmodules = load(open("data/modules.json"))
    except:
        botmodules = {"all": [], "loaded": []}

        with open("data/modules.json", "w") as conf:
            dump(botmodules, conf)

    tempmodules = botmodules.copy()

    botmodules['all'] = [x for x in listdir(
        "modules") if isdir("modules/" + x)]

    for module in botmodules['loaded']:
        try:
            # TODO: load modules as python module
            import_module('modules.{}.init'.format(module))
        except Exception as e:
            if args.concise:
                print("A error occured in {}:\n{}".format(module, "".join(
                    format_exception(type(e), e, e.__traceback__))))
            else:
                print("A error occured in {}:\n{} : {}".format(
                    module, type(e).__name__, e))

    if tempmodules != botmodules:
        with open("data/modules.json", "w") as conf:
            dump(botmodules, conf)

    # Load cogs
    try:
        cogs = load(open("data/cogs.json"))
    except:
        cogs = {"all": ["cogs.core"], "loaded": {"core": "cogs.core"}}

        with open("data/cogs.json", "w") as conf:
            dump(cogs, conf)

    tempcogs = cogs.copy()

    cogs['all'] = list(set(cogs['all'] + ['cogs.' + (x[:-3] if x.endswith(".py") else x) for x in listdir(
        "cogs") if x != "__pycache__" and (x.endswith(".py") or isfile("cogs/" + x + "/__init__.py"))]))

    for cog in cogs['all']:
        try:
            __import__(cog)
        except ModuleNotFoundError:
            cogs['all'].remove(cog)
        except:
            pass

    for cog in list(cogs['loaded'].items()):
        try:
            bot.load_extension(cog[1])
        except Exception as e:
            cogs['loaded'].pop(cog[0])
            if args.concise:
                print("Failed to load {}:\n{}".format(cog[0], "".join(
                    format_exception(type(e), e, e.__traceback__))))

            else:
                print("Failed to load {} :\n{} : {}".format(
                    cog, type(e).__name__, e))

    if tempcogs != cogs:
        with open("data/cogs.json", "w") as conf:
            dump(cogs, conf)

    # Finish Startup
    print("{} has started\n"
          "{} Servers\n"
          "{} Modules ({} loaded) \n"
          "{} Cogs ({} loaded)\n"
          "prefixes:\n{}"
          "".format(bot.user.name, len(bot.guilds), len(botmodules['all']), len(botmodules['loaded']),
                    len(cogs['all']), len(cogs['loaded']), " ".join(config["prefix"])))

if __name__ == "__main__":
    try:
        bot.run(token)
    except KeyboardInterrupt:
        bot.logout()
        print("\n")
