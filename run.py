import argparse

import image, grade
# This module delegates to submodules

submodules = [image, grade]

def run_module():
    parser = argparse.ArgumentParser(description='Grading script. Fix this desc.')
    subparsers = parser.add_subparsers(help="sub command help")
    for m in submodules:
        subparser = subparsers.add_parser(m.__name__, help=m.help)
        subparser.set_defaults(func=m.run.run_module)
        m.run.create_parser(subparser)

    args = parser.parse_args()
    args.func(args)

if __name__ == '__main__':
    run_module()
