'''TODO: Image package docs
'''

from grader.image.main import build_image

help = "Create images for grading."


def setup_parser(parser):
    parser.add_argument('--no-cache', default=False, action='store_true',
                        help='Rebuild the image from scratch; '
                             'don\'t use cached intermediary images.')
    parser.add_argument('target', metavar='target',
                        help='Source with Dockerfile and image.json.')
    parser.set_defaults(run=run)


def run(args):
    build_image(args.target, args.no_cache)
