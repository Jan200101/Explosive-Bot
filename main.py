from logging import getLogger, Formatter, INFO
from logging.handlers import RotatingFileHandler
from traceback import format_exception
from argparse import ArgumentParser
from importlib import import_module
from os.path import isdir, isfile
from os import listdir, mkdir
from json import load, dump
from discord.ext import commands

try:
    mkdir("data")
except:
    pass

try:
    config = load(open("data/config.json"))
except:
    config = {"prefix": ["!"], "avatar": "", "token": ""}

    with open("data/config.json", "w") as conf:
        dump(config, conf)

bot = commands.Bot(command_prefix=config['prefix'])


def arguments():
    parser = ArgumentParser(description="Explosive-Bot")
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

    cogs = loadmodules()
    botmodules = loadcogs()

    # Finish Startup
    bot.logger.info("Bot started")
    print("{} has started\n"
          "{} Servers\n"
          "{} Modules ({} loaded) \n"
          "{} Cogs ({} loaded)\n"
          "prefixes:\n{}"
          "".format(bot.user.name, len(bot.guilds), len(botmodules['all']),
                    len(botmodules['loaded']), len(cogs['all']),
                    len(cogs['loaded']), " ".join(config["prefix"])))


def loadmodules():
    botmodules = load(open("data/modules.json"))

    for module in botmodules['loaded']:
        try:
            # TODO: load modules as python module
            import_module('modules.{}.init'.format(module))
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
    # Set Variables

    bot.logger = getLogger("bot")
    bot.logger.setLevel(INFO)

    logformat = Formatter(
        '%(asctime)s %(levelname)s %(module)s '
        '%(funcName)s %(lineno)d: %(message)s',
        datefmt="[%d/%m/%Y %H:%M]")

    filehandler = RotatingFileHandler(
        filename='data/bot.log', encoding='utf-8', mode='a', maxBytes=10**7, backupCount=5)
    filehandler.setFormatter(logformat)

    bot.logger.addHandler(filehandler)

    # Prepare Modules
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

    # Prepare cogs
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

    bot.logger.info("Preparation Done")

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
        print("")
