'''TODO: List command docs
'''
import logging

from prettytable import PrettyTable

from grader.models import Grader
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "List student submission(s)"


def setup_parser(parser):
    parser.add_argument('--stat', action='store_true',
                        help="Show stats for each assignment")
    parser.add_argument('assignment', nargs='?',
                        help='Name of the assignment to list submissions for.')
    parser.set_defaults(run=run)


def stat(assignments):
    for assignment in assignments.values():
        print(assignment)


@require_grader_config
def run(args):
    g = Grader(args.path)
    assignments = g.assignments

    if args.stat:
        stat(assignments)
        return

    if args.assignment:
        try:
            assignments[args.assignment]
        except KeyError:
            assignments = []

    t = PrettyTable(["Assignment", "User ID", "Submission UUID"])

    for aname, assignment in assignments.items():
        for userid, submissions in assignment.submissions.items():
            for submission in submissions:
                t.add_row([
                    aname,
                    userid,
                    "{}...".format(submission.uuid[0:8]),
                ])

    print(t)
