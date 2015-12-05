import argparse
import importlib
import sys

description = "An automated grading tool for programming assignments."

subcommands = {
    "image": "grader.image",
    "grade": "grader.grade"
}


def run():
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(title="subcommands")

    # If no arguments are provided, show the usage screen
    parser.set_defaults(run=lambda x: parser.print_usage())

    # The 'help' command shows the help screen
    help_parser = subparsers.add_parser("help", help="Show this help screen")
    help_parser.set_defaults(run=lambda x: parser.print_help())

    # Set up subcommands for each package
    for name, path in subcommands.items():
        module = importlib.import_module(path)
        subparser = subparsers.add_parser(name, help=module.help)
        module.setup_parser(subparser)

    # Do it
    args = parser.parse_args()
    args.run(args)

if __name__ == '__main__':
    run()
