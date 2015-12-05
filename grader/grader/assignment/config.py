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

    def __init__(self, path):
        self.repository = git.Repo(path)
