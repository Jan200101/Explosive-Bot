from os import makedirs
from os.path import exists
from sys import modules


class RepoMissing(Exception):
    pass


def init():
    try:
        import modules.redv3.repo.redbot as red3
    except:
        raise RepoMissing("a error has occured\nCheck the console or log")

    modules["redbot"] = red3

    folders = ("data/red", "data/red/v3")
    for folder in folders:
        if not exists(folder):
            makedirs(folder)

# Gets called when unloading module
# Should hopefully clean up


def destroy():
    del modules["redbot"]
