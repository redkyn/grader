from .main import run
import argparse

def create_parser(parser):
    parser.add_argument('--no-cache', default=False, action='store_true', 
           help='Rebuild the image from scratch; don\'t use cached intermediary'
           + ' images.')
    parser.add_argument('target', metavar='target', 
                       help='Source with Dockerfile and image.json.')
    return parser

def run_module(args):
    run(args.target, args.no_cache)

if __name__ == '__main__':
    parser = create_parser(argparse.ArgumentParser(description=help))
    run_module(parser.parse_args())
