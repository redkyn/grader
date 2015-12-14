''' TODO: Init package docs
'''

import logging
import os
import sys
import uuid

from grader.grader import Grader, GraderException

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
    try:
        g = Grader(args.path)
        if not args.force:
            logger.critical("grader.yml exists in {}. Abort!".format(g.config_path))
            raise SystemExit(1)
    except GraderException:
        pass

    g = Grader.new(args.name, args.path, args.course_id)
    logger.info("Wrote {}".format(g.config_path))
