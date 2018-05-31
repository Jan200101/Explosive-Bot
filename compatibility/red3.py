import __main__
from discord.ext import commands
from os import makedirs
from os.path import exists
from sys import modules

import compatibility.repos.red3.redbot as red3

modules["redbot"] = red3

def check_folders():
    folders = ("data", "data/red", "data/red/V3")
    for folder in folders:
        if not exists(folder):
            print("Creating " + folder + " folder...")
            makedirs(folder)