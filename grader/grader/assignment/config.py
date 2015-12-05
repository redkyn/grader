import git
import logging
import os

from grader.utils.utils import touch

logger = logging.getLogger(__name__)


class ConfigException(Exception):
    pass


class Config(object):

    @classmethod
    def from_repo(path, repo_url):
        config_path = os.path.join(path, "config")

        try:
            git.Repo.clone_from(repo_url, config_path)
            logger.info("Successfully cloned {}".format(repo_url))
        except git.exc.GitCommandError:
            logger.warning("Could not clone {}".format(repo_url))
            logger.info("Initializing shell config")
            Config.new(config_path)

        return Config(path)

    @classmethod
    def new(path):
        config_path = os.path.join(path, "config")
        repo = git.Repo.init(config_path)

        def touch_and_stage(name):
            f = os.path.join(repo.working_tree_dir, name)
            touch(f)
            repo.add(f)

        touch_and_stage("grader.yml")
        touch_and_stage("Dockerfile")

        repo.commit("Add empty grader.yml and Dockerfile")


    def __init__(self, path):
        self.repository = git.Repo(path)
