'''TODO: List command docs
'''
import itertools
import logging

from collections import OrderedDict
from functools import reduce
from prettytable import PrettyTable

from grader.models import Grader
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "List student submission(s)"


def setup_parser(parser):
    parser.add_argument('--submissions', action='store_true',
                        help="Show submissions for each assignment")
    parser.add_argument('--full', action='store_true',
                        help="Show full length of values")
    parser.add_argument('--sortby', choices=["time", "user"], default="user",
                        help="Show full length of values")
    parser.add_argument('assignment', nargs='?',
                        help='Name of the assignment to list submissions for.')
    parser.set_defaults(run=run)


def shorten(value, length=8, full=False):
    if full:
        return value
    return "{}...".format(value[0:length])


def get_sort_key(short_name):
    funcs = {
        'time': "Import Time",
        'user': "User ID",
    }
    return lambda x: x[funcs[short_name]]


def sort_by_assignment(rows, sortby):
    grouped = itertools.groupby(rows, key=lambda x: x['Assignment'])
    grouped = [(k, sorted(list(g), key=get_sort_key(sortby)))
               for k, g in grouped]
    grouped = sorted(grouped, key=lambda x: x[0])
    return reduce(lambda x, y: x + y[1], grouped, [])


def build_assignment_info(assignments, full=False):
    info = []
    for aname, assignment in assignments.items():
        count, graded, failed = 0, 0, 0
        for submission in assignment.submissions:
            count += 1
            # graded += ?
            # failed += ?
        info.append(OrderedDict([
            ("Assignment", aname),
            ("Total", count),
            ("Graded", graded),
            ("Failed", failed),
        ]))
    return info


def build_submission_info(assignments, full=False):
    info = []
    for aname, assignment in assignments.items():
        for userid, submissions in assignment.submissions_by_user.items():
            for submission in submissions:
                info.append(OrderedDict([
                    ("Assignment", aname),
                    ("User ID", userid),
                    ("Submission UUID", shorten(submission.uuid, full=full)),
                    ("Import Time", str(submission.import_time)),
                    ("Last File MTime", str(submission.latest_mtime)),
                    ("Last Commit", str(submission.latest_commit)),
                    ("SHA1", shorten(submission.sha1sum, full=full)),
                    ("Re-Grades", len(submission.results_files)),
                    ("Failed", "--"),
                ]))
    return info


@require_grader_config
def run(args):
    g = Grader(args.path)
    assignments = g.assignments
    a_info = build_assignment_info(assignments, full=args.full)
    s_info = build_submission_info(assignments, full=args.full)

    columns = [
        "Assignment", "Total", "Graded", "Failed"
    ]
    rows = a_info

    if args.submissions:
        columns = [
            "Assignment", "User ID", "Submission UUID", "Import Time",
            "Last File MTime", "Last Commit", "SHA1", "Re-Grades", "Failed"
        ]
        rows = s_info
        rows = sort_by_assignment(rows, args.sortby)

    if args.assignment:
        try:
            a = assignments[args.assignment]
            rows = [r for r in rows if r['Assignment'] == a.name]
        except KeyError:
            rows = []

    t = PrettyTable(columns)
    for row in rows:
        t.add_row([row[c] for c in columns])

    print(t)
