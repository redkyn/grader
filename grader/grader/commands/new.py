''' TODO: New package docs
'''
import logging

from grader.models import Grader, GraderException
from grader.utils.config import require_grader_config

help = 'Create a new assignment'

logger = logging.getLogger(__name__)


def setup_parser(parser):
    parser.add_argument('name', help='Assignment name')
    parser.add_argument('repo', nargs='?', default=None,
                        help='Payload repo')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    try:
        g = Grader(args.path)
        g.create_assignment(args.name, repo=args.repo)
    except GraderException as e:
        logger.warning(str(e))
        raise SystemExit(1)
