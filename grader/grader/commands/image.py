'''TODO: Image package docs
'''

from grader.utils.config import require_grader_config

help = "Create images for grading."


def setup_parser(parser):
    parser.add_argument('--no-cache', default=False, action='store_true',
                        help='Rebuild the image from scratch; '
                             'don\'t use cached intermediary images.')
    parser.add_argument('target', metavar='target',
                        help='Source with Dockerfile and image.json.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    pass
