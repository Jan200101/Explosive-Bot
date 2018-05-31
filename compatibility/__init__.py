from importlib import import_module
from os import listdir
from sys import modules

# from __main__ import bot

for x in [x[:-3] for x in listdir('compatibility') if not '_' in x and x[-3:] == ".py"]:
    import_module('compatibility.' + x)
