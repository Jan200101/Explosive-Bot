import discord
from aiohttp.client_exceptions import ClientConnectorError
from json import load as loadjson, dump, decoder
from argparse import ArgumentParser
from discord.ext import commands
from random import randint
from os import replace, makedirs
from os.path import splitext, exists

def parse_cmd_arguments():  # allows for arguments
    parser = ArgumentParser(description="Discord-Selfbot")
    parser.add_argument("-t", "--test-run",  # test run flag for Travis
                        action="store_true",
                        help="Makes the bot quit before trying to log in")
    parser.add_argument("--reset-config",  # Reset bot config
                        action="store_true",
                        help="Reruns the setup")
    parser.add_argument("--no-prompt",  # Allows for Testing of mac related code
                        action="store_true",
                        help="Supresses all errors")
    return parser


args = parse_cmd_arguments().parse_args()
_reset_cfg = args.reset_config
_no_prompt = args.no_prompt

def setup(InvalidToken=False, cfg=None):

    if _no_prompt:
        print("Can not run Setup with no prompt")
        exit(0)

    if not cfg or (not 'TOKEN' in cfg or not 'PREFIX' in cfg or not 'DESCRIPTION' in cfg):
        config = {
            'TOKEN':'',
            'PREFIX':[],
            'DESCRIPTION':''
            }
    else:
        config = cfg

    if InvalidToken:
        print('The Token is incorrect')
    else:
        print('Enter your bot Token')
    config["TOKEN"] = input('>')

    while not config["PREFIX"]:
        print('\nEnter the prefix you want to use.\n'
              'You can setup multiple prefixes by putting a space between them')

        config["PREFIX"] = input('>').split()
        if not config["PREFIX"]:
            print("Empty command prefixes are invalid.")

    if not config['DESCRIPTION']:
        print('\nEnter a description for your bot.\n'
              'It will show up with the help message')

        config["DESCRIPTION"] = input('>')

    path, ext  = splitext('data/bot/config.json')
    tmp_file = "{}.{}.tmp".format(path, randint(1000, 9999))
    with open(tmp_file, 'w', encoding='utf-8') as tmp:
        dump(config, tmp, indent=4, sort_keys=True, separators=(',', ' : '))
    try:
        with open(tmp_file, 'r', encoding='utf-8') as tmp:
            config = loadjson(tmp)
    except decoder.JSONDecodeError:
        print("Attempted to write file {} but JSON "
              "integrity check on tmp file has failed. "
              "The original file is unaltered."
              "".format('data/bot/config.json'))
    except Exception as e:
        print('A issue has occured saving ' + 'data/bot/config.json' + '.\n'
              'Traceback:\n'
              '{0} {1}'.format(str(e), e.args))

    replace(tmp_file, 'data/bot/config.json')
    return config

def check_folders():
    folders = ("data", "data/bot/", "cogs", "cogs/utils")
    for folder in folders:
        if not exists(folder):
            print("Creating " + folder + " folder...")
            makedirs(folder)

if __name__ == '__main__':

    check_folders()
    print("Starting up...")

    while True:

        if _reset_cfg:
            config = setup()
        else:
            try:
                with open('data/bot/config.json', 'r', encoding='utf-8') as f:
                    config = loadjson(f)
            except IOError:
                config = setup()

        bot = commands.Bot(command_prefix=config['PREFIX'],
                           description=config['DESCRIPTION'],
                           pm_help=None)

        async def info():
            info = await bot.application_info()
            bot.owner = info.owner
            bot.client_id = info.id
            bot.oauth_url = "https://discordapp.com/oauth2/authorize?client_id={}&scope=bot".format(bot.client_id)

            bot.formatter = commands.formatter.HelpFormatter()

        async def send_help(ctx):
            helpm = await bot.formatter.format_help_for(ctx, ctx.command)
            for m in helpm:
                await ctx.send(m)

        def is_owner():
            def _check(ctx):
                return ctx.message.author.id == bot.owner.id
            return commands.check(_check)

        @bot.event
        async def on_ready():
            await info()
            guilds = len(bot.guilds)
            prefixes = config['PREFIX']
            channels = len([x for x in bot.get_all_channels()])
            users = len(set(bot.get_all_members()))

            msg = '\n------------'
            msg += '\n' + str(bot.user.name)
            msg += '\n' + '{}#{}\n'.format(str(bot.owner.name),
                                           str(bot.owner.discriminator))

            if len(prefixes) > 1:
                msg += "\nPrefix: " + ", ".join(prefixes)
            else:
                msg += '\nPrefixes: ' + ', '.join(prefixes) + '\n'
            msg += '\nConnected to:'

            if guilds > 1:
                msg += '\n{} guilds'.format(guilds)
            else:
                msg += '\n{} guild'.format(guilds)

            if channels > 1:
                msg += '\n{} channel'.format(channels)
            else:
                msg += '\n{} channels'.format(channels)

            if users > 1:
                msg += '\n{} user'.format(users)
            else:
                msg += '\n{} users'.format(users)

            msg += '\n\nInvite:\n{}'.format(bot.oauth_url)
            print(msg)
            bot.add_command(load)

        @bot.event
        async def on_command_error(ctx, error):
            if isinstance(error, commands.MissingRequiredArgument) or isinstance(error, commands.BadArgument):
                await send_help(ctx)
            elif isinstance(error, commands.CheckFailure):
                pass

        @commands.command()
        @is_owner()
        async def load(ctx, *, msg):
            """Load a module."""
            try:
                if (exists("cogs/{}.py".format(msg)) or exists("cogs/{}.pyw".format(msg))):
                    bot.load_extension("cogs.{}".format(msg))
                else:
                    raise ImportError("No cog named '{}'".format(msg))
            except Exception as e:
                await ctx.send('Failed to load module: `{}.py`'.format(msg))
                print('Failed to load module: `{}.py`'.format(msg))
                print('{}: {}'.format(type(e).__name__, e))
            else:
                await ctx.send('Loaded module: `{}.py`'.format(msg))

        try:
            bot.run(config['TOKEN'])
        except discord.errors.LoginFailure:
            setup(True, config)
            continue
        except ClientConnectorError:
            print("Could not connect to Discord. Make sure you are connected to the internet")
            exit(0)
        except KeyboardInterrupt:
            print('exiting...')
            exit(0)

        break
