from discord.ext.commands import check


def check_rolename(ctx, rolename):
    if not ctx.guild:
        return
    elif type(rolename) == str:
        return rolename in [y.name for y in ctx.message.author.roles]
    elif type(rolename) in (list, tuple, set):
        for role in rolename:
            if role in [y.name for y in ctx.message.author.roles]:
                return True
        return False


def check_mod(ctx):
    if check_owner(ctx):
        return True
    guild = ctx.message.guild
    if not guild:
        guild = None
    else:
        guild = guild.id
    return check_rolename(ctx, (ctx.bot.settings.getmoderatorrole(guild), ctx.bot.settings.getadminrole(guild)))


def check_admin(ctx):
    if check_owner(ctx):
        return True
    guild = ctx.message.guild
    if not guild:
        guild = None
    else:
        guild = guild.id
    return check_rolename(ctx, ctx.bot.settings.getadminrole(guild))


def check_owner(ctx):
    return ctx.bot.owner == ctx.message.author


def is_moderator():
    return check(check_mod)


def is_mod():
    return is_moderator()


def is_admin():
    return check(check_admin)
