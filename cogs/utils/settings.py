from discord import Guild
from json import load, dump


class Settings():

    def __init__(self):
        try:
            self.settings = load(open("data/settings.json"))
        except (IOError, ValueError):
            self.settings = {
                "DEFAULT": {
                    "PREFIX": [],
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
    def setglobalprefix(self, prefix):
        self.settings['DEFAULT']['PREFIX'] = prefix

    @setter
    def setprefix(self, guild: Guild, prefix):
        if not guild.id in self.settings: self.settings[guild.id] = self.default_settings.copy()
        self.settings[guild.id]['PREFIX'] = prefix

    def getprefix(self, guild: Guild = None):
        if not guild or not guild.id in self.settings or not self.settings[guild.id]['PREFIX']:
            return self.settings['DEFAULT']['PREFIX']
        return self.settings[guild.id]['PREFIX']
