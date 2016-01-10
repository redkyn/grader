'''TODO: Build command docs
'''
import logging

from grader.models import Grader, AssignmentError, AssignmentNotFoundError
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Build an assignment's docker image"


def setup_parser(parser):
    parser.add_argument('assignment',
                        help='Name of the assignment to build.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)
    a.build_image()
