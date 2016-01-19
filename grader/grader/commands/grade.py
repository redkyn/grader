'''TODO: Grade command docs
'''
import logging

from grader.models import Grader
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Grade assignment submission(s)"


def setup_parser(parser):
    parser.add_argument('--student_id', required=False,
                        help='Grade submission belonging to this student.')
    parser.add_argument('--submission_id', required=False,
                        help='Grade submission with this UUID.')
    parser.add_argument('assignment',
                        help='Name of the assignment to grade.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)
    for user_id, submissions in a.submissions_by_user.items():
        logger.info("Grading submissions for %s", user_id)
        for submission in submissions:
            submission.grade(a)
