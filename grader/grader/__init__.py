import argparse
import importlib
import logging
import os

logger = logging.getLogger(__name__)

description = "An automated grading tool for programming assignments."

subcommands = {
    "init": "grader.commands.init",
    "new": "grader.commands.new",
    "image": "grader.commands.image",
    "grade": "grader.grade"
}


def run():
    """Script entry point

    .. todo::

       Add a "verbose" flag
    """
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--path', default=os.getcwd(),
                        help='Path to the root of a grader')
    # If no arguments are provided, show the usage screen
    parser.set_defaults(run=lambda x: parser.print_usage())

    # Set up subcommands for each package
    subparsers = parser.add_subparsers(title="subcommands")
    for name, path in subcommands.items():
        module = importlib.import_module(path)
        subparser = subparsers.add_parser(name, help=module.help)
        module.setup_parser(subparser)

    # The 'help' command shows the help screen
    help_parser = subparsers.add_parser("help", help="Show this help screen")
    help_parser.set_defaults(run=lambda x: parser.print_help())

    # Parse CLI args
    args = parser.parse_args()

    # Do it
    args.run(args)

if __name__ == '__main__':
    run()
