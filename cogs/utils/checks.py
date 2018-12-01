from discord.ext.commands import check

def is_staff():
    return any(is_moderator(), is_admin(), is_owner())

def is_moderator():
    return (lambda ctx: ctx.bot.settings.getmoderatorrole() in [y.name for y in ctx.message.author.roles])

def is_mod():
    return is_moderator()

def is_admin():
    return (lambda ctx: ctx.bot.settings.getadminrole() in [y.name for y in ctx.message.author.roles])

def is_owner():
    return check((lambda ctx: ctx.bot.owner == ctx.message.author.id))
