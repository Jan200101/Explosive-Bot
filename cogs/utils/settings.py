from discord import Guild
from json import load, dump


class config(dict):

    def __missing__(self, key):
        return self['DEFAULT']


class Settings():

    def __init__(self):
        try:
            self.settings = load(
                open("data/settings.json"), object_hook=config)
        except (IOError, ValueError):
            self.settings = config({
                "DEFAULT": config({
                    "PREFIX": ["!"],
                    "ADMIN_ROLE": "Admin",
                    "MODERATOR_ROLE": "Moderator",
                })
            })

        self.default_settings = config{
            "PREFIX": None,
            "ADMIN_ROLE": None,
            "MODERATOR_ROLE": None,
        })

    def save(self):
        with open("data/settings.json", "w") as conf:
            dump(self.settings, conf)

    def setter(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.save()
        return wrapper

    def setvalue(self, keyid, key, value):
        if not str(keyid) in self.settings:
            self.settings[str(keyid)] = self.default_settings.copy()
        self.settings[str(keyid)][key] = value

    def getvalue(self, keyid, key):
        value = self.settings[str(keyid)][key]
        if not value:
            value = self.settings["DEFAULT"][key]
        return value

    @setter
    def setglobalsettings(self, prefix: list, admin: str = None, moderator: str = None):
        self.setvalue('DEFAULT', 'PREFIX', prefix)
        if admin:
            self.setvalue('DEFAULT', 'ADMIN_ROLE', admin)
        if moderator:
            self.setvalue('DEFAULT', 'MODERATOR_ROLE', moderator)

    @setter
    def setglobalprefix(self, prefix: list):
        self.setvalue('DEFAULT', 'PREFIX', prefix)

    @setter
    def setglobaladminrole(self, prefix: list):
        self.setvalue('DEFAULT', 'ADMIN_ROLE', prefix)

    @setter
    def setglobalmoderatorrole(self, prefix: list):
        self.setvalue('DEFAULT', 'MODERATOR_ROLE', prefix)

    @setter
    def setprefix(self, guild: Guild, prefix):
        self.setvalue(guild.id, 'PREFIX', prefix)

    @setter
    def setadminrole(self, guild: Guild, prefix):
        self.setvalue(guild.id, 'ADMIN_ROLE', prefix)

    @setter
    def setmoderatorrole(self, guild: Guild, prefix):
        return self.setvalue(guild.id, 'MODERATOR_ROLE', prefix)

    def getprefix(self, guild: Guild = None) -> list:
        return self.getvalue(guild.id, 'PREFIX')

    def getadminrole(self, guild: Guild = None) -> str:
        return self.getvalue(guild.id, 'ADMIN_ROLE')

    def getmoderatorrole(self, guild: Guild = None) -> str:
        return self.getvalue(guild.id, 'MODERATOR_ROLE')
