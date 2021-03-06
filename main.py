from asyncio import get_event_loop
from traceback import format_exception
from importlib import import_module
from sys import argv, executable
from os.path import isdir, isfile
from os import listdir, mkdir, execl
from json import load, dump
from json.decoder import JSONDecodeError

from discord import Message
from discord.errors import LoginFailure
from discord.ext import commands

from cogs.utils.arguments import args
from cogs.utils.logger import Logger
from cogs.utils.settings import Settings
from cogs.utils.data import Data

try:
    mkdir("data")
except OSError:
    pass


class Bot(commands.Bot):

    def __init__(self, *args, **kwargs):
        self.logger = Logger("bot")
        self.settings = Settings()

        super().__init__(*args, command_prefix=self.prefix_manager,
                         pm_help=False, **kwargs)

    def prefix_manager(self, bot: commands.Bot, message: Message) -> list:
        guild = message.guild
        if not guild:
            guild = None
        else:
            guild = guild.id
        return self.settings.getprefix(guild)

bot = Bot()


def setup() -> dict:
    CONFIG = {
        "avatar": "",
        "token": "",
    }

    if not args.dry_run:

        print("Setup")
        print("\nInsert your bots token:")

        while True:
            token = input("> ")
            if len(token) >= 50:
                CONFIG['token'] = token
                break
            print("That is not a valid token")

        print("\nChoose a prefix\nSeperate multiple prefixes with a space")
        prefix = input(">").split()

        print("\nInput admin role name\nLeave empty for default (Admin)")
        admin = input("> ")

        print("\nInput moderator role name\nLeave empty for default (Moderator)")
        moderator = input("> ")

        bot.settings.setsettings('DEFAULT', prefix, admin, moderator)
    else:
        bot.settings.setsettings('DEFAULT', ["!"])

    with open("data/config.json", "w") as conf:
        dump(CONFIG, conf)

    return CONFIG

try:
    if args.setup:
        CONFIG = setup()
    else:
        CONFIG = load(open("data/config.json"))
except (IOError, ValueError):
    CONFIG = setup()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        await ctx.send_help(ctx.command)
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
            ctx.command.qualified_name) + "".join(format_exception(type(error), error, error.__traceback__))

        print(exception_log)


@bot.event
async def on_ready():
    info = await bot.application_info()

    bot.owner = info.owner
    bot.client_id = info.id

    bot.oauth_url = "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot".format(
        bot.client_id)

    cogs = loadcogs()
    botmodules = loadmodules()

    # Finish Startup
    if len(argv) != 1:
        bot.logger.info(
            "Bot started with the following arguments: {}".format("".join(argv[-1:])))
    else:
        bot.logger.info("Bot started")

    print("{} has started\n\n"
          "{} Servers\n"
          "{} Modules ({} loaded) \n"
          "{} Cogs    ({} loaded)\n"
          "\n{}\n"
          "".format(bot.user.name, len(bot.guilds),
                    len(botmodules['all']), len(botmodules['loaded']),
                    len(cogs['all']), len(cogs['loaded']), bot.oauth_url))


def loadmodules() -> Data:
    botmodules = Data("data/modules.json")

    for module in botmodules['loaded']:
        try:
            import_module('modules.{}'.format(module)).init()
            bot.logger.info(module + " loaded")
        except ModuleNotFoundError:
            botmodules['loaded'].remove(module)
            if module in botmodules['all']:
                botmodules['all'].remove(module)
            bot.logger.warn(module + " not found")
        except Exception as error:
            bot.logger.warn("A error occured in {}: {}".format(module, "".join(
                format_exception(type(error), error, error.__traceback__))))
        finally:
            botmodules.save()
    return botmodules


def loadcogs() -> Data:
    cogs = Data("data/cogs.json")

    for name, cog in cogs['loaded'].copy().items():
        try:
            bot.load_extension(cog)
            bot.logger.info(name + " loaded")
        except Exception as error:
            cogs['loaded'].pop(name)
            bot.logger.warn("Failed to load {}: {}".format(name, "".join(
                format_exception(type(error), error, error.__traceback__))))
        finally:
            cogs.save()
    return cogs


def prepare():
    # Prepare Modules
    preparemodules()

    # Prepare cogs
    preparecogs()

    bot.logger.info("Preparation Done")


def preparemodules():
    try:
        botmodules = load(open("data/modules.json"))
    except (FileNotFoundError, JSONDecodeError):
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
        cogs = {"all": ["cogs.core", "cogs.moderation"], "loaded": {
            "core": "cogs.core", "moderation": "cogs.moderation"}}

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
            if cog in cogs['loaded'].values():
                cogs['loaded'] = {key: val for key, val in cogs['loaded'].items() if val != cog}
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
        if not args.dry_run:
            bot.run(CONFIG['token'])
    except LoginFailure:
        setup()
        execl(executable, 'python', *argv)
    except Exception as error:
        bot.logger.warn("Error on exit: {}".format(
            "".join(format_exception(type(error), error, error.__traceback__))))
    finally:
        if args.dry_run:
            loop = get_event_loop()
            loop.run_until_complete(bot.close())
            loop.close()
        bot.logger.info("Bot stopped")
        print("")  # newline workaround
