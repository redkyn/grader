import argparse
import importlib
import logging
import os

from collections import OrderedDict
from colorlog import ColoredFormatter

logger = logging.getLogger(__name__)

description = "An automated grading tool for programming assignments."

subcommands = OrderedDict([
    ("init", "grader.commands.init"),
    ("new", "grader.commands.new"),
    ("build", "grader.commands.build"),
    ("import", "grader.commands.import"),
    ("list", "grader.commands.list"),
    ("grade", "grader.commands.grade"),
    ("inspect", "grader.commands.inspect"),
    ("cat", "grader.commands.cat"),
    ("report", "grader.commands.report"),
    ("review", "grader.commands.review"),
    ("canvas", "grader.commands.canvas"),
])


def configure_logging():
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Create console handler. It'll write everything that's DEBUG or
    # better. However, it's only going to write what the logger passes
    # to it.
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)

    # Create a colorized formatter
    formatter = ColoredFormatter(
        "%(log_color)s%(levelname)-8s%(reset)s %(blue)s%(message)s",
        datefmt=None,
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    # Add the formatter to the console handler, and the console
    # handler to the root logger.
    console.setFormatter(formatter)
    root_logger.addHandler(console)


def make_parser():
    """Construct and return a CLI argument parser.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--path', default=os.getcwd(),
                        help='Path to the root of a grader')
    parser.add_argument('--tracebacks', action='store_true',
                        help='Show full tracebacks')
    parser.add_argument('--verbosity', default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
                        help='Desired log level')
    # If no arguments are provided, show the usage screen
    parser.set_defaults(run=lambda x: parser.print_usage())

    # Set up subcommands for each package
    subparsers = parser.add_subparsers(title="subcommands")
    for name, path in subcommands.items():
        module = importlib.import_module(path)
        subparser = subparsers.add_parser(name, help=module.help)
        module.setup_parser(subparser)

    # The 'help' command shows the help screen
    help_parser = subparsers.add_parser("help",
                                        help="Show this help screen and exit")
    help_parser.set_defaults(run=lambda x: parser.print_help())

    return parser


def run():                      # pragma: no cover
    """Script entry point
    """
    # Configure logging (obvi)
    configure_logging()

    # Parse CLI args
    parser = make_parser()
    args = parser.parse_args()

    # Set logging verbosity
    logging.getLogger().setLevel(args.verbosity)

    # Do it
    try:
        args.run(args)
    except Exception as e:
        if args.tracebacks:
            raise e
        logger.error(str(e))
        raise SystemExit(1) from e

if __name__ == '__main__':      # pragma: no cover
    run()
