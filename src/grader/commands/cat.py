'''TODO: Cat command docs
'''
import logging
import os

from grader.models import Grader
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Print an assignment's grade output to STDOUT"


def setup_parser(parser):
    parser.add_argument('--submission_id', type=str,
                        help='ID of specific submission to cat.')
    parser.add_argument('assignment',
                        help='Name of the assignment.')
    parser.add_argument('student_id',
                        help='ID of the student.')
    parser.set_defaults(run=run)


def last_graded(submission):
    return os.stat(submission.latest_result).st_mtime


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)

    try:
        submissions = a.submissions_by_user[args.student_id]
    except KeyError:
        logger.error("Cannot find student %s", args.student_id)
        return

    latest_submission = max(submissions, key=last_graded)
    logger.debug("Catting %s", latest_submission.latest_result)
    with open(latest_submission.latest_result) as f:
        print(f.read())
