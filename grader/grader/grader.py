import logging
import os
import shutil
import yaml

from grader.assignment.assignment import Assignment, AssignmentException
from grader.assignment.gradesheet import GradeSheetException


logger = logging.getLogger(__name__)


class GraderException(Exception):
    pass


class Grader(object):
    CONFIG_FILE_NAME = "grader.yml"

    @classmethod
    def new(cls, name, path, course_id):
        # Setup the configuration
        config_path = os.path.join(path, cls.CONFIG_FILE_NAME)
        header = "# grader configuration for {}\n\n".format(name)
        config = {
            "course-id": course_id,
            "course-name": name,
        }

        with open(config_path, 'w') as config_file:
            config_file.write(header)
            config_file.write(yaml.dump(config, default_flow_style=False))

        return cls(path)

    @property
    def config_path(self):
        return os.path.join(self.path, self.CONFIG_FILE_NAME)

    @property
    def assignment_dir(self):
        return os.path.join(self.path, "assignments")

    def __init__(self, path):
        self.path = path

        # Verify that paths exist like we expect
        if not os.path.exists(path):
            raise GraderException("Grader path doesn't exist!")
        if not os.path.exists(self.config_path):
            raise GraderException("Grader configuration file doesn't exist!")

    def create_assignment(self, name, repo=None):
        if not os.path.exists(self.assignment_dir):
            logger.info("Creating assignment directory.")
            os.mkdir(self.assignment_dir)

        try:
            logger.debug("Creating assignment")
            Assignment.new(name, self.assignment_dir, repo)
            logger.info("Created '{}'.".format(name))
            return
        except GradeSheetException as e:
            # If we couldn't clone the gradesheet properly, we have to
            # clean up the assignment folder.
            logger.info(str(e))
            logger.warning("Cannot construct assignment.")
            self.delete_assignment(name)
        except AssignmentException as e:
            logger.info(str(e))

    def delete_assignment(self, name):
        assignment_dir = os.path.join(self.assignment_dir, name)
        shutil.rmtree(assignment_dir, ignore_errors=True)
