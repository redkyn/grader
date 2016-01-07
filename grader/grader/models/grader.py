import logging
import os
import re
import shutil

from .assignment import Assignment, AssignmentException
from .config import GraderConfig
from .gradesheet import GradeSheetException

logger = logging.getLogger(__name__)


class GraderException(Exception):
    """A general-purpose exception thrown by the Assignment class.
    """
    pass


class Grader(object):
    """A Grader.

    This object can be used to perform all of the actions that a
    Grader can perform.

    """

    COURSE_NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
    """Regular expression for course names"""

    COURSE_ID_RE = re.compile(r"^[A-Za-z0-9_.-]+$")
    """Regular expression for course IDs"""

    @classmethod
    def new(cls, path, course_name, course_id):
        """Creates a new Grader instance and sets up its operating
        environment. This includes creating associated files on disk.

        :param str path: The path to the directory that will contain
            the Grader

        :param str course_name: The name of the course. It must match
            :data:`Grader.COURSE_NAME_RE`

        :param str course_id: The unique ID for the course. It must
            match :data:`Grader.COURSE_ID_RE`

        :raises GraderException: if ``course_name`` or ``course_id``
            don't match the required regular expression

        """
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

        GraderConfig.new(path, {'course-name': course_name,
                                'course-id': course_id})
        return cls(path)

    @property
    def assignment_dir(self):
        """The path to the Grader's assignment directory."""
        return os.path.join(self.path, Assignment.SUB_DIR)

    def __init__(self, path):
        """Instantiate a Grader.

        :param str path: The path to the grader on disk. The path
            should contain the configuration file for the grader.

        :raises GraderException: if the provided path doesn't exist

        :raises GraderConfigException: if the grader config file
            cannot be read

        """
        self.path = path

        # Verify that paths exist like we expect
        if not os.path.exists(path):
            raise GraderException("Grader path doesn't exist!")

        self.config = GraderConfig(self.path)

    def create_assignment(self, name, repo=None):
        """Creates a new assignment directory on disk as well as an associated
        gradesheet and subdirectories.

        :param str name: The name of the assignment. Must match
            :data:`Assignment.NAME_RE`

        :param str repo: An optional URL to a gradesheet
            repository. Read more about it in :meth:`Assignment.new`

        :return: None

        """
        if not os.path.exists(self.assignment_dir):
            logger.info("Creating assignment directory.")
            os.mkdir(self.assignment_dir)

        try:
            logger.debug("Creating assignment")
            Assignment.new(self, name, repo)
            logger.info("Created '{}'.".format(name))
        except GradeSheetException as e:
            # If we couldn't clone the gradesheet properly, we have to
            # clean up the assignment folder.
            self.delete_assignment(name)
            raise GraderException("Cannot construct assignment.") from e
        except AssignmentException as e:
            raise GraderException("Cannot construct assignment.") from e

    def build_assignment(self, name):
        """Builds an assignment's docker image using its Dockerfile

        """
        logger.debug("Loading assignment.")
        assignment = Assignment(self, name)
        assignment.build_image()

    def delete_assignment(self, name):
        """Deletes an assignment from the Grader's assignments directory.

        :param str name: The name of the assignment.
        """
        assignment_dir = os.path.join(self.assignment_dir, name)
        shutil.rmtree(assignment_dir, ignore_errors=True)
