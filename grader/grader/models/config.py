import jsonschema
import logging
import os
import yaml

logger = logging.getLogger(__name__)


class ConfigValidationError(Exception):
    """An exception thrown when a config file cannot be validated
    """
    pass


class Config(object):
    """A base class for configuration objects. Provides two vaguely-useful
    methods to subclasses.

    Requirements:

    * The class must have a class-wide ``CONFIG_FILE_NAME`` variable,
      which corresponds to the name of the configuration file (e.g.,
      ``"config.yml"``)

    * The class must have a class-wide ``SCHEMA`` variable, which is a
      valid JSONSchema that can be used to validate the fields in the
      Config.

    * Instances of the class must have an attribute ``path``, which is
      the file path to the directory containing the corresponding
      configuration file.

    * Instances of the class must have an attribute ``data``, which is
      a dict. It should contain data loaded from the corresponding
      configuration file.

    """
    @classmethod
    def new(cls, path, config):
        """Creates a new GraderConfig object and corresponding config file on
        disk.

        :param str path: The path to the directory in which the config
            file will be saved

        :param dict config: A dict of default configurations to store
            in the new configuration file.

        :raises: if ``config`` doesn't meet the requirements of the
            Config's :data:`SCHEMA`

        """
        cls._validate(config)

        config_path = os.path.join(path, cls.CONFIG_FILE_NAME)
        with open(config_path, 'w') as config_file:
            config_file.write(yaml.dump(config, default_flow_style=False))

        return cls(path)

    @classmethod
    def _validate(cls, obj):
        try:
            jsonschema.validate(obj, cls.SCHEMA)
        except jsonschema.ValidationError as e:
            raise ConfigValidationError(
                "{} is invalid.\n{}".format(cls.CONFIG_FILE_NAME, str(e))
            )

    @property
    def file_path(self):
        """The full file path to the corresponding configuration file.

        :return: The path to the configuration file
        :rtype: str
        """
        return os.path.join(self.path, self.__class__.CONFIG_FILE_NAME)

    def __init__(self, path):
        """Instantiates a Config by reading a YAML file

        :param str path: The path to the directory containing the
            YAML-formatted configuration file.

        """
        self.path = path

        if not os.path.exists(path):
            raise FileNotFoundError("Cannot open {}".format(path))

        with open(self.file_path) as config_file:
            logger.debug("Loading {}.".format(self.file_path))
            self.data = yaml.safe_load(config_file)
            logger.debug("Validating {}.".format(self.file_path))
            self.__class__._validate(self.data)

    def __getitem__(self, name):
        """Returns the configuration item for key ``name``

        :param str name: The key to fetch
        """
        return self.data[name]

    def __contains__(self, name):
        return name in self.data

    def get(self, name, default=None):
        """Returns the configuration item for key ``name``, defaulting to
        ``default``

        :param str name: The key to fetch

        :param default: The item to return if the key is not found

        """
        return self.data.get(name, default)

    def save(self):
        config_path = os.path.join(self.path, self.__class__.CONFIG_FILE_NAME)
        with open(config_path, 'w') as config_file:
            config_file.write(yaml.dump(self.data, default_flow_style=False))


class GraderConfig(Config):
    """A class for creating, loading, and accessing grader-wide,
    YAML-formatted configuration files

    """

    CONFIG_FILE_NAME = "grader.yml"
    """The name of the configuration file on disk"""

    SCHEMA = {
        "$schema": "http://json-schema.org/schema#",

        "type": "object",
        "properties": {
            "course-id": {
                "type": "string",
                "pattern": r"^[\w-]+$"
            },
            "course-name": {
                "type": "string",
                "pattern": r"^[\w-]+$"
            },
            "roster": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "id": {
                            "type": "string",
                            "pattern": r"^\w+$",
                        },
                    },
                    "required": ["name", "id"],
                    "additionalProperties": False,
                },
            },
            # Canvas API token
            "canvas-token": {
                "type": "string",
            },
            # Canvas domain
            "canvas-host": {
                "type": "string",
            },
        },
        "required": ["course-id", "course-name"],
        "additionalProperties": False,
    }
    """The schema for a Grader-wide configuration file"""

    @property
    def roster(self):
        if 'roster' not in self.data:
            self.data['roster'] = []
        return self.data['roster']

    def get_student_name(self, student_id):
        d = {x['id']: x['name'] for x in self.roster}
        return d[student_id]


class AssignmentConfig(Config):
    """A class for creating, loading, and accessing assignment-specific,
    YAML-formatted configuration files

    """

    CONFIG_FILE_NAME = "assignment.yml"
    """The name of the configuration file on disk"""

    SCHEMA = {
        "$schema": "http://json-schema.org/schema#",

        "type": "object",
        "properties": {
            "assignment-name": {
                "type": "string",
                "pattern": r"^[\w-]+$"
            },
            "image-build-options": {"type": "object"},
            "shell": {
                "type": "string"
            },
            "review-editor": {"type": "string"}
        },
        "required": ["assignment-name"],
        "additionalProperties": False
    }
    """The schema for a Assignment-wide configuration file"""
