from traceback import format_exception
from argparse import ArgumentParser
from importlib import import_module
from sys import argv
from os.path import isdir, isfile
from os import listdir, mkdir
from json import load, dump
from discord.ext import commands
from cogs.utils.logger import Logger

try:
    mkdir("data")
except OSError:
    pass

try:
    config = load(open("data/config.json"))
except (IOError, ValueError):
    config = {"prefix": ["!"], "avatar": "", "token": ""}

    with open("data/config.json", "w") as conf:
        dump(config, conf)

bot = commands.Bot(command_prefix=config['prefix'])


def arguments():
    parser = ArgumentParser(description="Explosive-Bot")
    parser.add_argument("--debug",
                        action="store_true",
                        help="Gives more information on certain actions")
    parser.add_argument("-c", "--concise",
                        action="store_true",
                        help="Gives full traceback")
    parser.add_argument("--no-run",
                        action="store_true",
                        help="Don't run the bot")
    return parser

args = arguments().parse_args()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        helpm = await bot.formatter.format_help_for(ctx, ctx.command)
        for message in helpm:
            await ctx.send(message)
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.message.channel.send("{} This command was used {:.2f}s ago and is on "
                                       "cooldown. Try again in {:.2f}s."
                                       "".format(ctx.message.author.mention,
                                                 error.cooldown.per - error.retry_after,
                                                 error.retry_after))
    elif isinstance(error, (commands.errors.CommandNotFound, commands.errors.CheckFailure)):
        return
    else:
        exception_log = "Exception in command '{}'\n" "".format(
            ctx.command.qualified_name)
        if args.concise:
            exception_log += "".join(
                format_exception(type(error), error, error.__traceback__)
            )
        else:
            exception_log += "{} : {}".format(type(error).__name__, error)

        print(exception_log)


@bot.event
async def on_ready():
    info = await bot.application_info()

    bot.owner = info.owner.id
    bot.client_id = info.owner

    cogs = loadcogs()
    botmodules = loadmodules()

    # Finish Startup
    if len(argv) != 1:
        bot.logger.info(
            "Bot started with the following arguments: {}".format("".join(argv[-1:])))
    else:
        bot.logger.info("Bot started")

    print("{} has started\n"
          "{} Servers\n"
          "{} Modules ({} loaded) \n"
          "{} Cogs ({} loaded)\n"
          "prefixes:\n{}"
          "".format(bot.user.name, len(bot.guilds),
                    len(botmodules['all']), len(botmodules['loaded']),
                    len(cogs['all']), len(cogs['loaded']),
                    " ".join(config["prefix"])))


def loadmodules():
    botmodules = load(open("data/modules.json"))

    for module in botmodules['loaded']:
        try:
            # TODO: load modules as python module
            import_module('modules.{}.init'.format(module)).init()
            bot.logger.info(module + " loaded")
        except Exception as error:
            bot.logger.warn("A error occured in {}: {}".format(module, "".join(
                format_exception(type(error), error, error.__traceback__))))
            if args.concise:
                print("A error occured in {}:\n{}".format(module, "".join(
                    format_exception(type(error), error, error.__traceback__))))
            else:
                print("A error occured in {}:\n{} : {}".format(
                    module, type(error).__name__, error))
    return botmodules


def loadcogs():
    cogs = load(open("data/cogs.json"))

    for cog in list(cogs['loaded'].items()):
        try:
            bot.load_extension(cog[1])
            bot.logger.info(cog[0] + " loaded")
        except Exception as error:
            cogs['loaded'].pop(cog[0])
            bot.logger.warn("Failed to load {}: {}".format(cog[0], "".join(
                format_exception(type(error), error, error.__traceback__))))
            if args.concise:
                print("Failed to load {}:\n{}".format(cog[0], "".join(
                    format_exception(type(error), error, error.__traceback__))))
            else:
                print("Failed to load {} :\n{} : {}".format(
                    cog, type(error).__name__, error))
    return cogs


def prepare():
    # Set Logger
    bot.logger = Logger("bot")

    # Prepare Modules
    preparemodules()

    # Prepare cogs
    preparecogs()

    bot.logger.info("Preparation Done")


def preparemodules():
    try:
        botmodules = load(open("data/modules.json"))
    except:
        botmodules = {"all": [], "loaded": []}

        with open("data/modules.json", "w") as conf:
            dump(botmodules, conf)

    tempmodules = botmodules.copy()

    botmodules['all'] = [x for x in listdir(
        "modules") if isdir("modules/" + x)]

    if tempmodules != botmodules:
        with open("data/modules.json", "w") as conf:
            dump(botmodules, conf)


def preparecogs():
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
            bot.logger.warn(cog + " not found")
        except Exception as error:
            bot.logger.warn("Failed to load {}: {}".format(cog[0], "".join(
                format_exception(type(error), error, error.__traceback__))))

    if tempcogs != cogs:
        with open("data/cogs.json", "w") as conf:
            dump(cogs, conf)

if __name__ == "__main__":
    try:
        prepare()
        if not args.no_run:
            bot.run(config['token'])
    except Exception as error:
        bot.logger.warn("Error on exit: {}".format(
            "".join(format_exception(type(error), error, error.__traceback__))))
    finally:
        bot.logger.info("Bot stopped")
        print("")  # newline workaround
