import docker
import itertools
import json
import logging
import os
import shutil
import tempfile

from .gradesheet import GradeSheet
from .mixins import DockerClientMixin
from .submission import Submission

logger = logging.getLogger(__name__)


class AssignmentError(Exception):
    """A general-purpose exception thrown by the Assignment class.
    """
    pass


class AssignmentBuildError(AssignmentError):
    """An exception thrown when there's an issue building the docker
    image.

    """
    pass


class Assignment(DockerClientMixin):
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

        :raises GradeSheetError: if there was an error creating
            the GradeSheet

        :raises ConfigValidationError: if there was an error
            creating the GradeSheet's assignment-specific config file

        """
        logger.debug("Creating assignment %s.", assignment_name)
        path = os.path.join(grader.assignment_dir, assignment_name)

        # Make sure the parent directory exists
        if not os.path.exists(grader.assignment_dir) \
           or not os.path.isdir(grader.assignment_dir):
            raise FileNotFoundError(
                "{} does not exist. "
                "Cannot create assignment.".format(grader.assignment_dir)
            )

        # Make sure the target directory doesn't exist
        if os.path.exists(path):
            raise FileExistsError(
                "{} exists. Cannot create assignment.".format(path)
            )

        logger.debug("Creating assignment in temporary directory...")
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup all the files/folders for the assignment
            cls._setup_assignment(tmpdir, assignment_name, gradesheet_repo)

            # If we have succeeded so far, copy everything over
            shutil.copytree(tmpdir, path)

        return cls(grader, assignment_name)

    @classmethod
    def _setup_assignment(cls, path, assignment_name, gradesheet_repo=None):
        """Creates necessary assignment files and folders within the provided
        path. Does not check for correct setup and does clean up if
        something goes wrong.

        :param str path: The path of the directory in which to build
            the assignment

        :param str assignment_name: The name of the assignment

        :param str gradesheet_repo: An optional gradesheet git repo URL

        """
        os.mkdir(os.path.join(path, "submissions"))
        os.mkdir(os.path.join(path, "results"))

        # Create the GradeSheet
        logger.debug("Creating GradeSheet")
        gradesheet_dir = os.path.join(path, GradeSheet.SUB_DIR)
        if gradesheet_repo:
            GradeSheet.from_repo(gradesheet_dir, gradesheet_repo)
        else:
            GradeSheet.new(gradesheet_dir, assignment_name)

    @property
    def image_tag(self):
        """Unique tag for an assignment's docker image"""
        return "{}-{}-{}".format(self.grader.config['course-id'],
                                 self.grader.config['course-name'],
                                 self.name)

    @property
    def image_id(self):
        """Unique ID for an assignment's docker image"""
        try:
            return self.docker_cli.inspect_image(self.image_tag)['Id']
        except docker.errors.NotFound as e:
            logger.debug(str(e))
            raise AssignmentBuildError(
                "{}'s image was not built.".format(self.name)
            ) from e

    @property
    def submissions_dir(self):
        """File path to the assignment's submissions directory"""
        return os.path.join(self.path, "submissions")

    @property
    def submissions(self):
        """All submissions for this assignment"""
        tarballs = os.listdir(self.submissions_dir)
        return [Submission(self, p) for p in tarballs]

    @property
    def submissions_by_user(self):
        """All submissions for this assignment grouped by user"""
        submissions = sorted(self.submissions, key=lambda x: x.user_id)
        groups = itertools.groupby(submissions, key=lambda x: x.user_id)
        return {k: sorted(g, key=lambda x: x.import_time) for k, g in groups}

    @property
    def results_dir(self):
        """File path to the assignment's results directory"""
        return os.path.join(self.path, "results")

    @property
    def gradesheet_dir(self):
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
            raise FileNotFoundError(
                "%s has no assignment directory", self.name
            )
        if not os.path.exists(self.submissions_dir):
            raise FileNotFoundError(
                "%s has no submissions directory", self.name
            )
        if not os.path.exists(self.results_dir):
            raise FileNotFoundError(
                "%s has no results directory", self.name
            )
        if not os.path.exists(self.gradesheet_dir):
            raise FileNotFoundError(
                "%s has no gradesheet directory", self.name
            )

        self.gradesheet = GradeSheet(self)

    def __str__(self):
        """String representation of an Assignment (i.e., its name)"""
        return self.name

    def build_image(self, nocache=False, pull=False, silent=False):
        """Build's an assignment's docker image using the Dockerfile from its
        :class:`GradeSheet`.

        The docker image will be tagged, so that this assignment's
        image is unique from the rest of the assignment images on a
        given machine.

        :return: :obj:`None`

        """

        if pull:
            logger.debug("Attempting to pull gradesheet")
            self.gradesheet.pull()

        # Load build options from the config
        build_options = self.gradesheet.config.get('image-build-options', {})

        # Override required build options
        build_options.update({
            "path": self.gradesheet.path,
            "tag": self.image_tag,
            "decode": not silent,
            "nocache": nocache
        })

        logger.info("Building image...")
        logger.debug("Image options: {}".format(build_options))

        # Build
        try:
            output = self.docker_cli.build(**build_options)

            # Log output line-by-line to avoid running the build
            # asynchronously
            prompt = "building {}>".format(self.name)
            for line in output:
                if silent:
                    continue

                error = 'Error: "{}"\n'.format(line.get('error', ''))
                stream = line.get('stream', '')
                print(prompt, stream or error, end="")
        except docker.errors.APIError as e:
            logger.debug(str(e))
            raise AssignmentBuildError(
                "Unable to build: {}".format(e.explanation)
            ) from e

        return self.image_id

    def delete_image(self):
        """Deletes an assignment's docker image based on its tag.
        """
        self.docker_cli.remove_image(self.image_tag)

    def import_submission(self, path, submission_type, pattern):
        importer = Submission.get_importer(submission_type)
        submissions = importer(self, path, pattern)

        for submission in submissions:
            if submission:
                logger.info("Imported %s", submission)
