from discord import Member
from discord.errors import Forbidden
from discord.ext import commands

from cogs.utils import checks


class Moderation:
    """
    Moderation commands
    """

    def __init__(self, bot):
        self.bot = bot

    @checks.is_mod()
    @commands.command()
    async def kick(self, ctx, member: Member, *, reason: str=None):
        """Kick a member"""

        msg = "You have been kicked from {}".format(ctx.guild.name)
        if reason:
            msg += " for the following reason:\n{}".format(reason)

        try:
            await member.send(msg)
        except Forbidden:
            pass

        try:
            await member.kick()
            await ctx.send("{} has been kicked".format(member.name))
        except Forbidden:
            await ctx.send("Unable to kick Member")

    @checks.is_mod()
    @commands.command()
    async def ban(self, ctx, member: Member, *, reason: str=None):
        """Ban a member"""

        msg = "You have been banned from {}".format(ctx.guild.name)
        if reason:
            msg += " for the following reason:\n{}".format(reason)

        try:
            await member.send(msg)
        except Forbidden:
            pass

        try:
            await member.ban(delete_message_days=0)
            await ctx.send("{} has been banned".format(member.name))
        except Forbidden:
            await ctx.send("Unable to ban Member")


def setup(bot):
    bot.add_cog(Moderation(bot))
