'''TODO: Build command docs
'''
import logging

from grader.models import Grader
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Build an assignment's docker image"


def setup_parser(parser):
    parser.add_argument('assignment',
                        help='Name of the assignment to build.')
    parser.add_argument('--no-cache', action='store_true',
                        help='Do not use docker image cache when building.')
    parser.add_argument('--pull', action='store_true',
                        help='Pull the gradesheet repo before building')
    parser.add_argument('--silent', action='store_true',
                        help='Do not parse aor display output from docker.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)
    a.build_image(args.no_cache, args.pull, args.silent)
