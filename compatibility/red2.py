import __main__
from discord.ext import commands
from os import makedirs
from os.path import exists
from sys import modules

from __main__ import bot

import compatibility.repos.red2.cogs.utils as red2

modules["cogs.utils"] = red2

def _get_variable(name):
    stack = inspect.stack()
    try:
        for frames in stack:
            try:
                frame = frames[0]
                current_locals = frame.f_locals
                if name in current_locals:
                    return current_locals[name]
            finally:
                del frame
    finally:
        del stack

async def send_message(destination, content, *args, **kwargs):

    await destination.send(content, *args, **kwargs)

async def say(content, *args, **kwargs):

    print(_get_variable('_internal_channel'))
    
bot.send_message = send_message
bot.say = say

def check_folders():
    folders = ("data", "data/red", "data/red/V2")
    for folder in folders:
        if not exists(folder):
            print("Creating " + folder + " folder...")
            makedirs(folder)