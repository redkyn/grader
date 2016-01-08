'''TODO: Import command docs
'''
import logging

from grader.models import Grader, Submission, AssignmentError, SubmissionError
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Import student submission(s)"


def setup_parser(parser):
    parser.add_argument('--kind', required=True,
                        choices=Submission.get_importers().keys())
    parser.add_argument('assignment',
                        help='Name of the assignment to add submission(s) to.')
    parser.add_argument('submission_path',
                        help='Path to the submission(s) to add.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)

    try:
        g.import_submission(args.assignment, args.submission_path, args.kind)
    except AssignmentError as e:
        logger.error(
            "Couldn't find assignment: {}".format(e)
        )
        raise SystemExit(1)
    except SubmissionError as e:
        logger.error(
            "Couldn't import submission(s): {}".format(e)
        )
        raise SystemExit(1)
