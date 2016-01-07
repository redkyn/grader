''' TODO: New package docs
'''

from grader.models import Grader
from grader.utils.config import require_grader_config

help = 'Create a new assignment'


def setup_parser(parser):
    parser.add_argument('name', help='Assignment name')
    parser.add_argument('repo', nargs='?', default=None,
                        help='Payload repo')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    g.create_assignment(args.name, repo=args.repo)
