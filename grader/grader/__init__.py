import argparse
import importlib
import logging
import os
import sys

from grader.utils.utils import is_grader_dir

logger = logging.getLogger(__name__)

description = "An automated grading tool for programming assignments."

subcommands = {
    "new": "grader.new",
    "image": "grader.image",
    "grade": "grader.grade"
}


def run():
    # Configure logging
    logging.basicConfig()

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

    # Check whether we're in a valid path
    if not is_grader_dir(args.path):
        # TODO implement "grader config" command
        logger.critical("Cannot execute grader! "
                        "{} has no grader.yml".format(args.path))
        sys.exit(1)

    # Do it
    args.run(args)

if __name__ == '__main__':
    run()
