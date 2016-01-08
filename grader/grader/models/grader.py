import logging
import os
import shutil

from .assignment import Assignment, AssignmentError
from .config import GraderConfig, ConfigValidationError
from .gradesheet import GradeSheetError

logger = logging.getLogger(__name__)


class GraderError(Exception):
    """A general-purpose exception thrown by the Assignment class.
    """
    pass


class Grader(object):
    """A Grader.

    This object can be used to perform all of the actions that a
    Grader can perform.

    """

    @classmethod
    def new(cls, path, course_name, course_id):
        """Creates a new Grader instance and sets up its operating
        environment. This includes creating associated files on disk.

        :param str path: The path to the directory that will contain
            the Grader

        :param str course_name: The name of the course. It must comply with
            :data:`GraderConfig.SCHEMA`

        :param str course_id: The unique ID for the course. It must
            comply with :data:`GraderConfig.SCHEMA`

        :raises GraderConfigError: if ``course_name`` or
            ``course_id`` don't comply with the configuration schema

        """
        GraderConfig.new(path, {'course-name': course_name,
                                'course-id': course_id})
        return cls(path)

    @property
    def assignment_dir(self):
        """The path to the Grader's assignment directory."""
        return os.path.join(self.path, Assignment.SUB_DIR)

    @property
    def assignments(self):
        """All assignments associated with this grader"""
        names = os.listdir(self.assignment_dir)
        return {name: Assignment(self, name) for name in names}

    def __init__(self, path):
        """Instantiate a Grader.

        :param str path: The path to the grader on disk. The path
            should contain the configuration file for the grader.

        :raises GraderError: if the provided path doesn't exist

        :raises GraderConfigError: if the grader config file
            cannot be read

        """
        self.path = path

        # Verify that paths exist like we expect
        if not os.path.exists(path):
            raise GraderError("Grader path doesn't exist!")

        self.config = GraderConfig(self.path)

    def create_assignment(self, name, repo=None):
        """Creates a new assignment directory on disk as well as an associated
        gradesheet and subdirectories.

        :param str name: The name of the assignment. Must comply with
            :data:`AssignmentConfig.SCHEMA`

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
        except GradeSheetError as e:
            # If we couldn't clone the gradesheet repo, we have to
            # delete the assignment folder.
            self.delete_assignment(name)
            raise GraderError(
                "Could not clone assignment: {}".format(str(e))
            )
        except ConfigValidationError as e:
            # If we couldn't create gradesheet config file properly,
            # we have to delete the assignment folder.
            self.delete_assignment(name)
            raise GraderError(
                "Cannot create configuration: {}".format(str(e))
            )
        except AssignmentError as e:
            raise GraderError(
                "Cannot construct assignment: {}".format(str(e))
            )

    def build_assignment(self, name):
        """Builds an assignment's docker image using its Dockerfile

        :param str name: The name of the assignment to build
        """
        assignment = Assignment(self, name)
        assignment.build_image()

    def delete_assignment(self, name):
        """Deletes an assignment from the Grader's assignments directory.

        :param str name: The name of the assignment.
        """
        assignment_dir = os.path.join(self.assignment_dir, name)
        shutil.rmtree(assignment_dir, ignore_errors=True)

    def import_submission(self, name, path, submission_type):
        """Imports an submission for an assignment

        :param str name: The name of the assignment to associate the
            submission with

        """
        assignment = Assignment(self, name)
        assignment.import_submission(path, submission_type)
