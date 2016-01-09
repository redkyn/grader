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

    try:
        g = Grader(args.path)
        a = g.get_assignment(args.assignment)
        a.build_image()

    except AssignmentError as e:
        logger.error(str(e))
        raise SystemExit(1)
    except AssignmentNotFoundError as e:
        logger.error(str(e))
        raise SystemExit(1)
    except FileNotFoundError as e:
        logger.error(str(e))
        raise SystemExit(1)
    except FileExistsError as e:
        logger.error(str(e))
        raise SystemExit(1)
