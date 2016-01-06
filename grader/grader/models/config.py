import os
import yaml


class GraderConfigException(Exception):
    """A general-purpose exception thrown by the GraderConfig class.
    """
    pass


class AssignmentConfigException(Exception):
    """A general-purpose exception thrown by the AssignmentConfig class.
    """
    pass


class Config(object):
    """A base class for configuration objects. Provides two vaguely-useful
    methods to subclasses.

    Requirements:

    * The class must have a class-wide ``CONFIG_FILE_NAME`` variable,
      which corresponds to the name of the configuration file (e.g.,
      ``"config.yml"``)

    * Instances of the class must have an attribute ``path``, which is
      the file path to the directory containing the corresponding
      configuration file.

    * Instances of the class must have an attribute ``data``, which is
      a dict. It should contain data loaded from the corresponding
      configuration file.

    """

    @property
    def file_path(self):
        """The full file path to the corresponding configuration file.

        :return: The path to the configuration file
        :rtype: str
        """
        return os.path.join(self.path, self.__class__.CONFIG_FILE_NAME)

    def __getitem__(self, name):
        """Returns the configuration item for key ``name``
        :param str name: The key to fetch
        """
        return self.data[name]


class GraderConfig(Config):
    """A class for creating, loading, and accessing grader-wide,
    YAML-formatted configuration files

    """

    CONFIG_FILE_NAME = "grader.yml"
    """The name of the configuration file on disk"""

    @classmethod
    def new(cls, path, course_name, course_id):
        """Creates a new GraderConfig object and corresponding config file on
        disk.

        :param str path: The path to the directory in which the config
            file will be saved

        :param str course_name: The name of the course

        :param str course_id: The unique ID of the course

        """
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
        """Instantiates a GraderConfig by reading a YAML file

        :param str path: The path to the directory containing the
            YAML-formatted configuration file.

        """
        self.path = path

        if not os.path.exists(self.file_path):
            raise GraderConfigException("Grader config file doesn't exist!")

        with open(self.file_path) as config_file:
            self.data = yaml.load(config_file)


class AssignmentConfig(Config):
    """A class for creating, loading, and accessing assignment-specific,
    YAML-formatted configuration files

    """

    CONFIG_FILE_NAME = "assignment.yml"
    """The name of the configuration file on disk"""

    @classmethod
    def new(cls, path, assignment_name):
        """Creates a new AssignmentConfig object and corresponding config file
        on disk.

        :param str path: The path to the directory in which the config
            file will be saved

        :param str assignment_name: The name of the assignment

        """
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
        """Instantiates an AssignmentConfig by reading a YAML file

        :param str path: The path to the directory containing the
            YAML-formatted configuration file.

        """
        self.path = path

        if not os.path.exists(self.file_path):
            raise AssignmentConfigException("Assignment config file "
                                            "doesn't exist!")

        with open(self.file_path) as config_file:
            self.data = yaml.load(config_file)
