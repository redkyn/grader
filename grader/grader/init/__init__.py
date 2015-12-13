''' TODO: Init package docs
'''

import logging
import os
import sys
import uuid

from grader.init.setup_grader import setup

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
    config_path = os.path.join(args.path, "grader.yml")
    logger.debug("Setting up grader in {}".format(args.path))

    # Check for existing config
    if os.path.exists(config_path) and not args.force:
        logger.critical("grader.yml exists in {}. Abort!".format(config_path))
        sys.exit(1)

    setup(config_path, args.name, args.course_id)
    logger.info("Wrote {}".format(config_path))
