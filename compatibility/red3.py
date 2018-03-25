import __main__
from discord.ext import commands

__main__.settings = __main__.bot.settings
from repos.red3.redbot import *
from repos.red3.redbot.core import *
from repos.red3.redbot.core.drivers import *
from repos.red3.redbot.core.locales import *
from repos.red3.redbot.core.utils import *

class redbot:
    # I find strong disgust in the way Red Version 3 functions are Loaded"
    class core:
        __init__ = __init__
        bank = bank
        bot = bot
        checks = checks
        cli = cli
        cog_manager = cog_manager
        config = config
        context = context
        core_commands = core_commands
        data_manager = data_manager
        dev_manager = dev_manager
        events = events
        global_checks = global_checks
        i18n = i18n
        json_io = json_io
        modlog = modlog
        rpc = rpc
        sentry = sentry

        class drivers:
            __init__ = __init__
        class utils:


modules['redbot'] = redbot
modules['redbot.core'] = redbot.core
modules['redbot.core.i18n'] = redbot.core.i18n
modules['redbot.core.i18n.CogI18n'] = redbot.core.i18n.CogI18n
modules['redbot.core.utils'] = redbot.core.utils
modules['redbot.core.utils.chat_formatting'] = redbot.core.utils.chat_formatting
