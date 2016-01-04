import logging
import os
import shutil

from .assignment import Assignment, AssignmentException
from .config import GraderConfig
from .gradesheet import GradeSheetException


logger = logging.getLogger(__name__)


class GraderException(Exception):
    pass


class Grader(object):

    @classmethod
    def new(cls, path, course_name, course_id):
        GraderConfig.new(path, course_name, course_id)
        return cls(path)

    @property
    def assignment_dir(self):
        return os.path.join(self.path, "assignments")

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
            a = Assignment.new(self, name, repo)
            logger.info("Created '{}'.".format(name))

            logger.info("Building assignment...")
            a.build_image()
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
