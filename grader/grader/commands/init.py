''' TODO: Init package docs
'''

import logging
import uuid

from grader.models import Grader
from grader.utils.config import is_grader_dir

logger = logging.getLogger(__name__)

help = 'Initialize grader by creating grader.yml'


def setup_parser(parser):
    parser.add_argument('--course-id', default=str(uuid.uuid4()),
                        help='Unique course ID (for docker\'s sake)')
    parser.add_argument('--force', action='store_true',
                        help='Overwrite an existing grader.yml')
    parser.add_argument('name', help='Name of the course')
    parser.set_defaults(run=run)


def run(args):
    logger.debug("Setting up grader in {}".format(args.path))

    # Check for existing config
    if is_grader_dir(args.path) and not args.force:
        logger.critical(
            "grader already configured in {}. Abort!".format(args.path)
        )
        raise SystemExit(1)

    # Create the new grader
    g = Grader.new(args.path, args.name, args.course_id)
    logger.info("Wrote {}".format(g.config.file_path))
