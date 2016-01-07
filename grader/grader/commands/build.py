'''TODO: Build command docs
'''

from grader.models import Grader
from grader.utils.config import require_grader_config

help = "Build an assignment's docker images."


def setup_parser(parser):
    parser.add_argument('assignment_name',
                        help='Name of the assignment to build.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    g.build_assignment(args.assignment_name)
