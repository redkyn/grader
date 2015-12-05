import os
import logging
import shutil

from grader.assignment.assignment import Assignment, AssignmentException
from grader.assignment.config import ConfigException

logger = logging.getLogger(__name__)


def delete_assignment(name, path):
    assignment_dir = os.path.join(path, "assignments", name)
    shutil.rmtree(assignment_dir, ignore_errors=True)


def create_assignment(name, path, repo=None):
    assignments_dir = os.path.join(path, "assignments")
    if not os.path.exists(assignments_dir):
        logger.info("Assignment directory not found. Creating one...")
        os.mkdir(assignments_dir)

    try:
        logger.debug("Creating assignment")
        Assignment.new(name, assignments_dir, repo)
        return
    except ConfigException as e:
        # If we couldn't clone the config properly, we have to clean
        # up the assignment folder.
        logger.info(str(e))
        logger.info("Cannot construct assignment.")
        delete_assignment(name, path)
    except AssignmentException as e:
        logger.info(str(e))
