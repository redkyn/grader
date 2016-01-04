import os
import yaml


class GraderConfigException(Exception):
    pass


class AssignmentConfigException(Exception):
    pass


class Config(object):

    @property
    def file_path(self):
        return os.path.join(self.path, self.__class__.CONFIG_FILE_NAME)

    def __getitem__(self, name):
        return self.data[name]


class GraderConfig(Config):
    CONFIG_FILE_NAME = "grader.yml"

    @classmethod
    def new(cls, path, course_name, course_id):
        config_path = os.path.join(path, cls.CONFIG_FILE_NAME)
        header = "# grader configuration for {}\n".format(course_name)
        config = {
            "course-id": course_id,
            "course-name": course_name,
        }

        with open(config_path, 'w') as config_file:
            config_file.write(header)
            config_file.write(yaml.dump(config, default_flow_style=False))

        return cls(path)

    def __init__(self, path):
        self.path = path

        if not os.path.exists(self.file_path):
            raise GraderConfigException("Grader configuration file doesn't exist!")

        with open(self.file_path) as config_file:
            self.data = yaml.load(config_file)


class AssignmentConfig(Config):
    CONFIG_FILE_NAME = "assignment.yml"

    @classmethod
    def new(cls, path, assignment_name):
        config_path = os.path.join(path, cls.CONFIG_FILE_NAME)
        header = "# assignment configuration for {}\n".format(assignment_name)
        config = {
            "assignment-name": assignment_name
        }

        with open(config_path, 'w') as config_file:
            config_file.write(header)
            config_file.write(yaml.dump(config, default_flow_style=False))

        return cls(path)

    def __init__(self, path):
        self.path = path

        if not os.path.exists(self.file_path):
            raise AssignmentConfigException("Assignment configuration file doesn't exist!")

        with open(self.file_path) as config_file:
            self.data = yaml.load(config_file)
