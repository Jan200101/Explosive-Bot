from argparse import ArgumentParser


def arguments():
    parser = ArgumentParser(description="Explosive-Bot")
    parser.add_argument("--setup",
                        action="store_true",
                        help="Runs the setup")
    parser.add_argument("--dry-run", "--no-run",
                        action="store_true",
                        help="Don't run the bot")
    return parser

args = arguments().parse_args()
