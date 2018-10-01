from os import makedirs
from os.path import exists
from sys import modules


class RepoMissing(Exception):
    pass

try:
    import modules.redv3.repo.redbot as red3
except:
    raise RepoMissing("Red v3 Repo has not been cloned")

modules["redbot"] = red3

folders = ("data/red", "data/red/v3")
for folder in folders:
    if not exists(folder):
        makedirs(folder)
