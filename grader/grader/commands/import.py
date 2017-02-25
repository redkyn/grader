'''TODO: Import command docs
'''
import logging

from grader.models import Grader, Submission
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Import student submission(s)"


def setup_parser(parser):
    parser.add_argument('--kind', required=True,
                        choices=Submission.get_importers().keys())
    parser.add_argument('--pattern',
                        help='Regular expression to match student ID'
                        ' in submission filename')
    parser.add_argument('assignment',
                        help='Name of the assignment to add submission(s) to.')
    parser.add_argument('submission_path',
                        help='Path to the submission(s) to add.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)

    pattern = args.pattern if args.pattern else r"(?P<id>.*)"
    a.import_submission(args.submission_path, args.kind, pattern)
