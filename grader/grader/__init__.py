import argparse
import importlib
import sys

subcommands = {
    "image": "grader.image",
    "grade": "grader.grade"
}


def run():
    parser = argparse.ArgumentParser(description='Grading script. Fix this desc.')
    subparsers = parser.add_subparsers(title="subcommands")

    for name, path in subcommands.items():
        module = importlib.import_module(path)
        subparser = subparsers.add_parser(name, help=module.help)
        module.setup_parser(subparser)

    args = parser.parse_args()
    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        args.run(args)

if __name__ == '__main__':
    run()
