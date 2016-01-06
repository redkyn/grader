import git
import logging
import os

from .config import AssignmentConfig

logger = logging.getLogger(__name__)


class GradeSheetException(Exception):
    pass


class GradeSheet(object):
    SUB_DIR = "gradesheet"

    @classmethod
    def from_repo(cls, gradesheet_path, repo_url):
        try:
            git.Repo.clone_from(repo_url, gradesheet_path)
            logger.info("Successfully cloned {}".format(repo_url))
        except git.exc.GitCommandError:
            raise GradeSheetException("Could not clone {}".format(repo_url))

        return None

    @classmethod
    def new(cls, gradesheet_path, assignment_name):
        path = gradesheet_path

        # Initialize a new gradesheet repo
        repo = git.Repo.init(path)

        # Create a default assignment config
        config = AssignmentConfig.new(path, assignment_name)

        # Create a default Dockerfile
        dockerfile_path = os.path.join(path, 'Dockerfile')
        with open(dockerfile_path, 'w') as dockerfile:
            dockerfile.write("# Dockerfile for {}".format(assignment_name))

        repo.index.add([config.file_path, dockerfile_path])
        repo.index.commit("Add default assignment.yml and Dockerfile")

        return None

    @property
    def dockerfile_path(self):
        return os.path.join(self.path, "Dockerfile")

    def __init__(self, assignment):
        self.path = assignment.gradesheet_path
        self.assignment = assignment
        self.config = AssignmentConfig(self.path)
        self.repository = git.Repo(self.path)

        # Verify that paths exist like we expect
        if not os.path.exists(self.dockerfile_path):
            raise GradeSheetException("GradeSheet repo has no Dockerfile!")
