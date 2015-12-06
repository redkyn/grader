import git
import logging
import os

from grader.utils.utils import touch

logger = logging.getLogger(__name__)


class ConfigException(Exception):
    pass


class Config(object):

    @classmethod
    def from_repo(cls, path, repo_url):
        config_path = os.path.join(path, "config")

        try:
            git.Repo.clone_from(repo_url, config_path)
            logger.info("Successfully cloned {}".format(repo_url))
            return cls(config_path)
        except git.exc.GitCommandError:
            raise ConfigException("Could not clone {}".format(repo_url))

    @classmethod
    def new(cls, path):
        config_path = os.path.join(path, "config")
        repo = git.Repo.init(config_path)

        def touch_and_stage(name):
            f = os.path.join(repo.working_tree_dir, name)
            touch(f)
            repo.index.add([f])

        touch_and_stage("assignment.yml")
        touch_and_stage("Dockerfile")
        repo.index.commit("Add empty assignment.yml and Dockerfile")

        return cls(config_path)

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
            raise ConfigException("Config repo path doesn't exist")
        if not os.path.exists(self.dockerfile_path):
            raise ConfigException("Config repo is missing a Dockerfile!")
        if not os.path.exists(self.config_file_path):
            raise ConfigException("Assignment config doesn't exist!")

        self.repository = git.Repo(path)
