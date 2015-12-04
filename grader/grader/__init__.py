import argparse
import re
import sys

from grader import image, grade
# This module delegates to submodules

submodules = [image, grade]

def run():
    parser = argparse.ArgumentParser(description='Grading script. Fix this desc.')
    subparsers = parser.add_subparsers(help="additional help", 
            description="valid subcommands", title="subcommands")
    for m in submodules:
        subparser = subparsers.add_parser(re.sub(r'^[^\.]+\.', '', m.__name__),
                help=m.help)
        subparser.set_defaults(func=m.run.run_module)
        m.run.create_parser(subparser)

    args = parser.parse_args()
    if len(sys.argv) <= 1:
        parser.print_help()
    else:
        args.func(args)

if __name__ == '__main__':
    run()
