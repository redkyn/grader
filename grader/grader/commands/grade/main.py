'''TODO: Grade command docs
'''
import logging

from grader.models import Grader
from grader.utils.config import require_grader_config
from grader.commands.grade.async import async_grade

logger = logging.getLogger(__name__)

help = "Grade assignment submission(s)"


def setup_parser(parser):
    parser.add_argument('--rebuild', action='store_true',
                        help='Rebuild containers (if they exist).')
    parser.add_argument('--suppress_output', action='store_true',
                        help='Don\'t display output.')
    parser.add_argument('-j',  default="1",
                        help='How many concurrent containers to grade.')
    parser.add_argument('assignment',
                        help='Name of the assignment to grade.')
    parser.add_argument('student_id', nargs='?',
                        help='Grade submission belonging to this student.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)

    users = a.submissions_by_user

    if args.student_id:
        try:
            users = {args.student_id: users[args.student_id]}
        except KeyError:
            logger.error("Cannot find student %s", args.student_id)
            return

    if args.j != "1":
        return async_grade(args, users)

    for user_id, submissions in users.items():
        logger.info("Grading submissions for %s", user_id)

        for submission in submissions:
            submission.grade(rebuild_container=args.rebuild,
                             show_output=(not args.suppress_output))
