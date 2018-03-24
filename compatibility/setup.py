from importlib import import_module
from os import listdir
from sys import modules
try:
    from __main__ import bot
except:
    class bot:
        pass

def compatibilitysetup():
    for x in [x[:-3] for x in listdir('compatibility') if not '_' in x]:
        import_module('compatibility.' + x)

compatibilitysetup()
