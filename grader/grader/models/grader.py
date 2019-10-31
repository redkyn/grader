import logging
import os
import shutil

from .assignment import Assignment
from .config import GraderConfig

logger = logging.getLogger(__name__)


class GraderError(Exception):
    """A general-purpose exception thrown by the Assignment class.
    """
    pass


class AssignmentNotFoundError(GraderError):
    """An exception thrown when we can't find an assignment.
    """
    pass


class Grader(object):
    """A Grader.

    This object can be used to perform all of the actions that a
    Grader can perform.

    """

    @classmethod
    def new(cls, path, course_name, course_id, canvas_host=None, canvas_token=None):
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
        config = {'course-name': course_name,
                  'course-id': course_id,
                 }
        if canvas_host:
            config['canvas-host'] = canvas_host
            config['canvas-token'] = canvas_token

        GraderConfig.new(path, config)
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

    @property
    def student_ids(self):
        """All student IDs from the roster"""
        try:
            return [s['id'] for s in self.config['roster']]
        except KeyError:
            return []

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
            raise FileNotFoundError("{} doesn't exist.".format(path))

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

        logger.debug("Creating assignment")
        Assignment.new(self, name, repo)
        logger.info("Created '{}'.".format(name))

    def get_assignment(self, name):
        """Retrieves an assignment.

        :param str name: The name of the assignment to get

        :raises AssignmentNotFoundError: if no such assignment exists

        :return: The Assignment
        :rtype: :class:`Assignment`
        """
        try:
            return self.assignments[name]
        except KeyError:
            raise AssignmentNotFoundError("{} doesn't exist".format(name))

    def delete_assignment(self, name):
        """Deletes an assignment from the Grader's assignments directory.

        :param str name: The name of the assignment.
        """
        assignment_dir = os.path.join(self.assignment_dir, name)
        shutil.rmtree(assignment_dir, ignore_errors=True)
