'''TODO: Build command docs
'''
import logging

from grader.models import Grader, AssignmentError
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Build an assignment's docker image"


def setup_parser(parser):
    parser.add_argument('assignment_name',
                        help='Name of the assignment to build.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)

    try:
        g.build_assignment(args.assignment_name)
    except AssignmentError as e:
        logger.error(str(e))
        raise SystemExit(1)
    except FileNotFoundError as e:
        logger.error(str(e))
        raise SystemExit(1)
    except FileExistsError as e:
        logger.error(str(e))
        raise SystemExit(1)
