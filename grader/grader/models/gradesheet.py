import git
import logging
import os

from grader.utils.utils import touch

logger = logging.getLogger(__name__)


class GradeSheetException(Exception):
    pass


class GradeSheet(object):

    @classmethod
    def from_repo(cls, path, repo_url):
        gradesheet_path = os.path.join(path, "gradesheet")

        try:
            git.Repo.clone_from(repo_url, gradesheet_path)
            logger.info("Successfully cloned {}".format(repo_url))
            return cls(gradesheet_path)
        except git.exc.GitCommandError:
            raise GradeSheetException("Could not clone {}".format(repo_url))

    @classmethod
    def new(cls, path):
        gradesheet_path = os.path.join(path, "gradesheet")
        repo = git.Repo.init(gradesheet_path)

        def touch_and_stage(name):
            f = os.path.join(repo.working_tree_dir, name)
            touch(f)
            repo.index.add([f])

        touch_and_stage("assignment.yml")
        touch_and_stage("Dockerfile")
        repo.index.commit("Add empty assignment.yml and Dockerfile")

        return cls(gradesheet_path)

    @property
    def dockerfile_path(self):
        return os.path.join(self.path, "Dockerfile")

    @property
    def config_file_path(self):
        return os.path.join(self.path, "assignment.yml")

    def __init__(self, path):
        self.path = path

        # Verify that paths exist like we expect
        if not os.path.exists(path):
            raise GradeSheetException("GradeSheet repo path doesn't exist")
        if not os.path.exists(self.dockerfile_path):
            raise GradeSheetException("GradeSheet repo has no Dockerfile!")
        if not os.path.exists(self.config_file_path):
            raise GradeSheetException("Assignment gradesheet doesn't exist!")

        self.repository = git.Repo(path)
