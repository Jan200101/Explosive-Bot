from discord import Guild
from json import load, dump


class Settings():

    def __init__(self):
        try:
            self.settings = load(open("data/settings.json"))
        except (IOError, ValueError):
            self.settings = {
                "DEFAULT": {
                    "PREFIX": ["!"],
                    "ADMIN_ROLE": "Admin",
                    "MODERATOR_ROLE": "Moderator",
                }
            }

        self.default_settings = {
            "PREFIX": None,
            "ADMIN_ROLE": None,
            "MODERATOR_ROLE": None,
        }

    def save(self):
        with open("data/settings.json", "w") as conf:
            dump(self.settings, conf)

    def setter(func):
        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self.save()
        return wrapper

    @setter
    def setglobalsettings(self, prefix: list, admin: str = None, moderator: str = None):
        self.settings['DEFAULT']["PREFIX"] = prefix
        if admin:
            self.settings['DEFAULT']["ADMIN_ROLE"] = admin
        if moderator:
            self.settings['DEFAULT']["MODERATOR_ROLE"] = moderator

    @setter
    def setglobalprefix(self, prefix: list):
        self.settings['DEFAULT']['PREFIX'] = prefix

    @setter
    def setprefix(self, guild: Guild, prefix):
        if not str(guild.id) in self.settings: self.settings[str(guild.id)] = self.default_settings.copy()
        self.settings[str(guild.id)]['PREFIX'] = prefix

    def getprefix(self, guild: Guild = None) -> list:
        if not guild or not str(guild.id) in self.settings or not self.settings[str(guild.id)]['PREFIX']:
            return self.settings['DEFAULT']['PREFIX']
        return self.settings[str(guild.id)]['PREFIX']

    def getadminrole(self, guild: Guild = None) -> str:
        if not guild or not str(guild.id) in self.settings or not self.settings[str(guild.id)]['ADMIN_ROLE']:
            return self.settings['DEFAULT']['ADMIN_ROLE']
        return self.settings[str(guild.id)]['ADMIN_ROLE']

    def getmoderatorrole(self, guild: Guild = None) -> str:
        if not guild or not str(guild.id) in self.settings or not self.settings[str(guild.id)]['MODERATOR_ROLE']:
            return self.settings['DEFAULT']['MODERATOR_ROLE']
        return self.settings[str(guild.id)]['MODERATOR_ROLE']

