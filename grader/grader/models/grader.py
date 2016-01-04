import logging
import os
import re
import shutil

from .assignment import Assignment, AssignmentException
from .config import GraderConfig
from .gradesheet import GradeSheetException


logger = logging.getLogger(__name__)


class GraderException(Exception):
    pass


class Grader(object):
    COURSE_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
    COURSE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")

    @classmethod
    def new(cls, path, course_name, course_id):
        # Check the course name
        if not cls.COURSE_NAME_RE.match(course_name):
            raise GraderException(
                "Bad course name {}. "
                "Must match {}".format(course_name, cls.COURSE_NAME_RE.pattern)
            )

        # Check the course id
        if not cls.COURSE_ID_RE.match(course_id):
            raise GraderException(
                "Bad course id {}. "
                "Must match {}".format(course_id, cls.COURSE_ID_RE.pattern)
            )

        GraderConfig.new(path, course_name, course_id)
        return cls(path)

    @property
    def assignment_dir(self):
        return os.path.join(self.path, Assignment.SUB_DIR)

    def __init__(self, path):
        self.path = path

        # Verify that paths exist like we expect
        if not os.path.exists(path):
            raise GraderException("Grader path doesn't exist!")

        self.config = GraderConfig(self.path)

    def create_assignment(self, name, repo=None):
        if not os.path.exists(self.assignment_dir):
            logger.info("Creating assignment directory.")
            os.mkdir(self.assignment_dir)

        try:
            logger.debug("Creating assignment")
            assignment = Assignment.new(self, name, repo)
            logger.info("Created '{}'.".format(name))

            if not repo:
                logger.info("Skipping build. Dockerfile needs to be completed.")
            else:
                logger.info("Building assignment...")
                assignment.build_image()
                logger.info("Build complete.")
            return
        except GradeSheetException as e:
            # If we couldn't clone the gradesheet properly, we have to
            # clean up the assignment folder.
            logger.info(str(e))
            logger.warning("Cannot construct assignment.")
            self.delete_assignment(name)
        except AssignmentException as e:
            logger.info(str(e))

    def delete_assignment(self, name):
        assignment_dir = os.path.join(self.assignment_dir, name)
        shutil.rmtree(assignment_dir, ignore_errors=True)
