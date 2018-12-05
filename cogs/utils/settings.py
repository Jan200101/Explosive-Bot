from json import load, dump


class Config(dict):

    def __missing__(self, key):
        return self['DEFAULT']


class Settings():

    def __init__(self):
        try:
            self.settings = load(
                open("data/settings.json"), object_hook=Config)
        except (IOError, ValueError):
            self.settings = Config({
                "DEFAULT": {
                    "PREFIX": ["!"],
                    "ADMIN_ROLE": "Admin",
                    "MODERATOR_ROLE": "Moderator",
                }
            })

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
    def setsettings(self, guildid, prefix: list, admin: str = None, moderator: str = None, dmhelp: bool = True):
        self.setvalue(guildid, 'PREFIX', prefix)
        if admin:
            self.setvalue(guildid, 'ADMIN_ROLE', admin)
        if moderator:
            self.setvalue(guildid, 'MODERATOR_ROLE', moderator)
        if dmhelp:
            self.setvalue(guildid, 'DMHELP', dmhelp)

    @setter
    def setprefix(self, guildid, prefix: list):
        self.setvalue(guildid, 'PREFIX', prefix)

    @setter
    def setadminrole(self, guildid, role: str):
        self.setvalue(guildid, 'ADMIN_ROLE', role)

    @setter
    def setmoderatorrole(self, guildid, role: str):
        self.setvalue(guildid, 'MODERATOR_ROLE', role)

    def getprefix(self, guildid=None) -> list:
        return self.getvalue(guildid, 'PREFIX')

    def getadminrole(self, guildid=None) -> str:
        return self.getvalue(guildid, 'ADMIN_ROLE')

    def getmoderatorrole(self, guildid=None) -> str:
        return self.getvalue(guildid, 'MODERATOR_ROLE')
