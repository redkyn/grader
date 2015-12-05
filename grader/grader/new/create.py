import os
import logging
from grader.assignment.assignment import Assignment

logger = logging.getLogger(__name__)


def create_assignment(name, path, repo=None):
    assignment_dir = os.path.join(path, "assignments")
    if not os.path.exists(assignment_dir):
        os.mkdir(assignment_dir)

    logger.debug("Creating assignment")
    Assignment.new(name, path, repo)
    logger.info("Created assignment {}".format(name))
