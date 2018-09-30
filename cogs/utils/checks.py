from discord.ext.commands import check


def is_owner():
    return check((lambda ctx: ctx.bot.owner == ctx.message.author.id))
