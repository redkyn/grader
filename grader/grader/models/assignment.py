import docker
import logging
import os

from .gradesheet import GradeSheet
from .submission import Submission

logger = logging.getLogger(__name__)


class AssignmentError(Exception):
    """A general-purpose exception thrown by the Assignment class.
    """
    pass


class Assignment(object):
    """An Assignment with several neato attributes:

    * A place (directory) for storing student submissions for the
      assignment

    * A place (directory) for storing the grade reports for graded
      submissions

    * A place (git repository) for storing grading scripts and
      configuration files

    This class makes dealing with all those files and folders just a
    little easier. Creating new assignments, grading them, etc.

    """

    SUB_DIR = "assignments"
    """Name of the subdirectory for assignments"""

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

        .. note::

           If you provide a repository URL, the Assignment will
           attempt to clone the repo. You will need pull access to it.

        :param grader: The Grader this assignment belongs to
        :type grader: :class:`Grader`

        :param assignment_name: The name of this assignment. Must
               comply with :data:`AssignmentConfig.SCHEMA`
        :type assignment_name: str

        :param gradesheet_repo: The URL of a git repository to clone
               for the gradesheet. If set to None, a repository with
               default values will be created.
        :type gradesheet_repo: str

        :return: The newly created Assignment
        :rtype: :class:`Assignment`

        :raises AssignmentError: if the "assignments" directory
            doesn't exist, if the directory for the new assignment
            already exists, or if the name of the assignment.

        :raises GradeSheetError: if there was an error creating
            the GradeSheet

        :raises ConfigValidationError: if there was an error
            creating the GradeSheet's assignment-specific config file

        """
        path = os.path.join(grader.assignment_dir, assignment_name)

        # Make sure the parent directory exists
        if not os.path.exists(grader.assignment_dir):
            raise AssignmentError(
                "{} does not exist".format(grader.assignment_dir)
            )

        # Make sure the target directory doesn't exist
        if os.path.exists(path):
            raise AssignmentError("{} exists".format(path))

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
        """Unique tag for an assignment's docker image"""
        return "{}-{}-{}".format(self.grader.config['course-id'],
                                 self.grader.config['course-name'],
                                 self.name)

    @property
    def submissions_path(self):
        """File path to the assignment's submissions directory"""
        return os.path.join(self.path, "submissions")

    @property
    def results_path(self):
        """File path to the assignment's results directory"""
        return os.path.join(self.path, "results")

    @property
    def gradesheet_path(self):
        """File path to the assignment's gradesheet repository"""
        return os.path.join(self.path, GradeSheet.SUB_DIR)

    def __init__(self, grader, assignment_name):
        """Instantiate a new Assignment

        :param grader: The grader with which this assignment is associated
        :type grader: :class:`Grader`

        :param assignment_name: The name of the assignment
        :type assignment_name: str

        :raises AssignmentError: if the assignment path
            (``Assignment.SUB_DIR/assignment_name``) doesn't exist, if
            the submission path doesn't exist with in the assignment
            path, if the results path doesn't exist within the
            assignment path, or if the directory for the gradesheet
            repository doesn't exist

        :raises GradeSheetError: if there was an error
            constructing the Assignment's :class:`GradeSheet`

        """
        logger.debug("Loading assignment.")
        self.path = os.path.join(grader.assignment_dir, assignment_name)
        self.name = assignment_name
        self.grader = grader

        # Verify that paths exist like we expect
        if not os.path.exists(self.path):
            raise AssignmentError("Assignment path doesn't exist")
        if not os.path.exists(self.submissions_path):
            raise AssignmentError("Submission path doesn't exist")
        if not os.path.exists(self.results_path):
            raise AssignmentError("Results path doesn't exist")
        if not os.path.exists(self.gradesheet_path):
            raise AssignmentError("GradeSheet path doesn't exist")

        self.gradesheet = GradeSheet(self)

    def build_image(self):
        """Build's an assignment's docker image using the Dockerfile from its
        :class:`GradeSheet`.

        The docker image will be tagged, so that this assignment's
        image is unique from the rest of the assignment images on a
        given machine.

        .. todo::

           Use configuration from grader.yml and assignment.yml to
           pass additional options to ``docker build``

        :return: :obj:`None`

        """
        cli = docker.Client(base_url="unix://var/run/docker.sock",
                            version="auto")

        # Load build options from the config
        build_options = self.gradesheet.config.get('image-build-options', {})

        # Override required build options
        build_options.update({
            "path": self.gradesheet.path,
            "tag": self.image_tag,
            "decode": True
        })

        logger.info("Building image...")
        logger.debug("Image options: {}".format(build_options))

        # Build
        output = cli.build(**build_options)

        # Log output line-by-line to avoid running the build
        # asynchronously
        for line in output:
            logger.debug(line)

    def import_submission(self, path, submission_type):
        importer = Submission.get_importer(submission_type)
        submission = importer(self, path)
