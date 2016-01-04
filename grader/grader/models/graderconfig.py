import os
import yaml


class GraderConfigException(Exception):
    pass


class GraderConfig(object):
    CONFIG_FILE_NAME = "grader.yml"

    @classmethod
    def new(cls, path, course_name, course_id):
        config_path = os.path.join(path, cls.CONFIG_FILE_NAME)
        header = "# grader configuration for {}\n\n".format(course_name)
        config = {
            "course-id": course_id,
            "course-name": course_name,
        }

        with open(config_path, 'w') as config_file:
            config_file.write(header)
            config_file.write(yaml.dump(config, default_flow_style=False))

    @property
    def file_path(self):
        return os.path.join(self.path, self.__class__.CONFIG_FILE_NAME)

    def __init__(self, path):
        self.path = path

        if not os.path.exists(self.path):
            raise GraderConfigException("Grader configuration file doesn't exist!")

        with open(self.file_path) as config_file:
            self.data = yaml.load(config_file)

    def __getattr__(self, name):
        return self.data[name]
