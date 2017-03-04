import git
import glob
import logging
import os

from .config import AssignmentConfig

logger = logging.getLogger(__name__)


class GradeSheetError(Exception):
    """A general-purpose exception thrown by the Assignment class.
    """
    pass


class GradeSheet(object):
    """A gradesheet for an assignment. Gradesheets are git
    repositories. They have the following attributes...

    A configuration file
        Assignment-specific configuration information (refer to
        :class:`AssignmentConfig`)

    A Dockerfile
        Used to build a docker image. That image will be used to
        create containers for running student submissions

    Grading scripts
        The assignment-specific configuration details how to run
        grading scripts. The gradesheet repository must have the
        scripts in order to run them.

    """

    SUB_DIR = "gradesheet"
    """The name to use when creating a new gradesheet directory on disk.

    """

    @classmethod
    def from_repo(cls, gradesheet_path, repo_url):
        """Clone a gradesheet from a remote git repository.

        :param str gradesheet_path: The path to the directory into
            which the gradesheet repository will be cloned.

        :param str repo_url: A URL pointing to a gradesheet repository
            to clone.

        :raises GradeSheetError: if there was a problem cloning
            the repo

        """
        try:
            git.Repo.clone_from(repo_url, gradesheet_path)
            logger.info("Successfully cloned {}".format(repo_url))
        except git.exc.GitCommandError as e:
            raise GradeSheetError("Could not clone {}".format(repo_url)) from e

        return None

    @classmethod
    def new(cls, gradesheet_path, assignment_name):
        """Initializes a new gradesheet repository with default files

        :param str gradesheet_path: The path to the directory into
            which the gradesheet repository will be cloned.

        :param str assignment_name: The name of the assignment.
        """
        path = gradesheet_path

        # Initialize a new gradesheet repo
        repo = git.Repo.init(path)

        # Create a default assignment config
        config = AssignmentConfig.new(path,
                                      {'assignment-name': assignment_name})

        # Create a default Dockerfile
        dockerfile_path = os.path.join(path, 'Dockerfile')
        with open(dockerfile_path, 'w') as dockerfile:
            dockerfile.write("# Dockerfile for {}".format(assignment_name))

        repo.index.add([config.file_path, dockerfile_path])
        repo.index.commit("Add default assignment.yml and Dockerfile")

        return None

    @property
    def dockerfile_path(self):
        """The path to this gradesheet's Dockerfile"""
        return os.path.join(self.path, "Dockerfile")

    @property
    def templates(self):
        """A dictionary of this gradesheet's optional report templates"""
        templates = glob.glob(os.path.join(self.path, '*.template'))
        return {os.path.basename(t).split('.')[0].lower(): t
                for t in templates}

    def __init__(self, assignment):
        """Instantiates a GradeSheet.

        :param Assignment assignment: The assignment to which this
            gradesheet belongs.

        :raises AssignmentConfigError: if the assignment-specific
            config file in the gradesheet cannot be loaded

        :raises GradeSheetError: if the Dockerfile can't be found

        """
        self.path = assignment.gradesheet_dir
        self.assignment = assignment
        self.config = AssignmentConfig(self.path)
        self.repository = git.Repo(self.path)

        # Verify that paths exist like we expect
        if not os.path.exists(self.dockerfile_path):
            raise FileNotFoundError("GradeSheet repo has no Dockerfile!")

    def pull(self):
        if self.repository is not None:
            logger.debug("Pulling gradesheet repo...")
            self.repository.git.pull('--rebase')
