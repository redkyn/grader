''' TODO: New package docs
'''
import logging

from grader.models import Grader
from grader.utils.config import require_grader_config

help = 'Create a new assignment'

logger = logging.getLogger(__name__)


def setup_parser(parser):
    parser.add_argument('name', help='Assignment name')
    parser.add_argument('repo', nargs='?', default=None,
                        help='Gradesheet repository')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    g.create_assignment(args.name, repo=args.repo)
