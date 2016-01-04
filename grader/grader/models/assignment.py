import logging
import os
import re

from docker import Client

from .gradesheet import GradeSheet

logger = logging.getLogger(__name__)


class AssignmentException(Exception):
    pass


class Assignment(object):
    """An Assignment

    """
    SUB_DIR = "assignments"
    NAME_RE = re.compile(r"^[A-Za-z0-9_.-]+$")

    @classmethod
    def new(cls, grader, assignment_name, gradesheet_repo=None):
        """Creates a new Assignment for a Grader. This includes...

        * Creating a directory to hold assignments, if necessary.

        * Creating a directory within the assignments directory to
          hold the new assignment.

        * Creating subdirectories for submissions and grading results
          within the assignment directory

        * Creating a gradesheet repository by...

            * Cloning from a URL, if provided

            * Initializing a repository with default files

        :param grader: The Grader this assignment belongs to
        :type grader: :class:`grader.models.Grader`

        :param assignment_name: The name of this assignment
        :type assignment_name: str

        :param gradesheet_repo: The URL of a git repository to clone
                                for the gradesheet. If set to None, a
                                repository with default values will be
                                created.

        :type gradesheet_repo: str

        :rtype: :class:`grader.models.Assignment`

        """
        path = os.path.join(grader.assignment_dir, assignment_name)

        # Make sure the parent directory exists
        if not os.path.exists(grader.assignment_dir):
            raise AssignmentException(
                "{} does not exist".format(grader.assignment_dir)
            )

        # Make sure the target directory doesn't exist
        if os.path.exists(path):
            raise AssignmentException("{} exists".format(path))

        # Check the assignment name
        if not cls.NAME_RE.match(assignment_name):
            raise AssignmentException(
                "Bad assignment name {}. "
                "Must match {}".format(assignment_name, cls.NAME_RE.pattern)
            )

        # Make assignment root and subdirs
        os.mkdir(path)
        os.mkdir(os.path.join(path, "submissions"))
        os.mkdir(os.path.join(path, "results"))

        gradesheet_path = os.path.join(path, GradeSheet.SUB_DIR)
        if gradesheet_repo:
            GradeSheet.from_repo(gradesheet_path, gradesheet_repo)
        else:
            GradeSheet.new(gradesheet_path, assignment_name)

        return cls(grader, assignment_name)

    @property
    def image_tag(self):
        return "{}-{}-{}".format(self.grader.config['course-id'],
                                 self.grader.config['course-name'],
                                 self.name)

    @property
    def submissions_path(self):
        return os.path.join(self.path, "submissions")

    @property
    def results_path(self):
        return os.path.join(self.path, "results")

    @property
    def gradesheet_path(self):
        return os.path.join(self.path, GradeSheet.SUB_DIR)

    def __init__(self, grader, assignment_name):
        self.path = os.path.join(grader.assignment_dir, assignment_name)
        self.name = assignment_name
        self.grader = grader

        # Verify that paths exist like we expect
        if not os.path.exists(self.path):
            raise AssignmentException("Assignment path doesn't exist")
        if not os.path.exists(self.submissions_path):
            raise AssignmentException("Submission path doesn't exist")
        if not os.path.exists(self.results_path):
            raise AssignmentException("Results path doesn't exist")
        if not os.path.exists(self.gradesheet_path):
            raise AssignmentException("GradeSheet path doesn't exist")

        self.gradesheet = GradeSheet(self)

    def build_image(self):
        cli = Client(base_url="unix://var/run/docker.sock", version="auto")
        output = cli.build(
            path=self.gradesheet.path,
            tag=self.image_tag,
            decode=True
        )

        for line in output:
            logger.debug(line)
