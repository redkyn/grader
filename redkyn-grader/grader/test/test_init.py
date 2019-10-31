import os
import pytest
import re
import yaml

from grader.models.config import ConfigValidationError

UUID_RE = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


def test_init(parse_and_run):
    """Test vanilla grader initialization
    """
    path = parse_and_run(["init", "cpl"])

    with open(os.path.join(path, "grader.yml")) as config_file:
        grader_config = yaml.safe_load(config_file)

    assert grader_config['course-name'] == "cpl"
    assert re.match(UUID_RE, grader_config['course-id']) is not None


def test_init_force(parse_and_run):
    """Test forced config overwrite
    """
    path = parse_and_run(["init", "cpl"])
    with open(os.path.join(path, "grader.yml")) as config_file:
        grader_config = yaml.safe_load(config_file)
        previous_id = grader_config['course-id']

    parse_and_run(["init", "--force", "cpl"])
    with open(os.path.join(path, "grader.yml")) as config_file:
        grader_config = yaml.safe_load(config_file)

    assert grader_config['course-id'] != previous_id


def test_init_noforce(parse_and_run):
    """Test that config is not overwritten without force
    """
    parse_and_run(["init", "cpl"])

    with pytest.raises(SystemExit):
        parse_and_run(["init", "cpl"])


def test_bad_course_name(parse_and_run):
    """Test enforcement of bad course names
    """
    with pytest.raises(ConfigValidationError):
        parse_and_run(["init", "NOOO%%%%OOPE!"])


def test_init_bad_config_file(parse_and_run):
    """Test that config is not overwritten without force when the config
    file is bad.

    """
    path = parse_and_run(["init", "cpl"])

    # Write unparsable YAML
    with open(os.path.join(path, "grader.yml"), 'w') as config_file:
        config_file.write("{ thing: ")

    with pytest.raises(SystemExit):
        parse_and_run(["init", "cpl"])

    parse_and_run(["init", "--force", "cpl"])

    # Write YAML that doesn't match the scheme
    with open(os.path.join(path, "grader.yml"), 'w') as config_file:
        config_file.write(yaml.dump("{1: 3}"))

    with pytest.raises(SystemExit):
        parse_and_run(["init", "cpl"])

    parse_and_run(["init", "--force", "cpl"])
