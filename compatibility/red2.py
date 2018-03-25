from os import listdir
from sys import modules

import __main__

__main__.settings = __main__.bot.settings
from repos.red2.cogs.utils import *

listutils = [x[:-3] for x in listdir('compatibility/.repos/red2/cogs/utils') if not '_' in x]

class cogs:
    class utils:
        __init__ = __init__
        chat_formatting = chat_formatting
        checks = checks
        converters = converters
        dataIO = dataIO
        settings = settings

modules['cogs.utils'] = cogs.utils

modules['cogs.utils.chat_formatting'] = cogs.utils.chat_formatting
modules['cogs.utils.checks'] = cogs.utils.checks
modules['cogs.utils.converters'] = cogs.utils.converters
modules['cogs.utils.dataIO'] = cogs.utils.dataIO
modules['cogs.utils.settings'] = cogs.utils.settings
