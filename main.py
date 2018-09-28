from traceback import format_exception
from json import load, dump

from discord.ext import commands

from data.config import prefix, token


bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, (commands.errors.CommandNotFound, commands.errors.CheckFailure)):
        return
    elif isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument)):
        helpm = await bot.formatter.format_help_for(ctx, ctx.command)
        for m in helpm:
            await ctx.send(m)
    elif isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.message.channel.send("{} This command was used {:.2f}s ago and is on "
                                       "cooldown. Try again in {:.2f}s."
                                       "".format(ctx.message.author.mention,
                                                 error.cooldown.per - error.retry_after,
                                                 error.retry_after))
    else:
        exception_log = "Exception in command '{}'\n" "".format(
            ctx.command.qualified_name)
        exception_log += "".join(
            format_exception(type(error), error, error.__traceback__)
        )
        print(exception_log)

@bot.event
async def on_ready():


    try:
        addons = load(open("config/addons.json"))
    except:
        addons = []
        with open("config/addons.json", "w") as config:
            dump(addons, config, indent=4, sort_keys=True, separators=(',', ':'))

    for addon in addons:
        try:
            bot.load_extension("addons." + addon)
            print("{} addon loaded.".format(addon))
        except Exception as e:
            print("Failed to load {} :\n{} : {}".format(
                addon, type(e).__name__, e))

    print("{} has started\nServers: {}"
          "".format(bot.user.name, len(bot.guild)))

if __name__ == "__main__":
    try:
        bot.run(token)
    except KeyboardInterrupt:
        bot.logout()