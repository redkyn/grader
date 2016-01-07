import os
import pytest
import re
import yaml

UUID_RE = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"

def test_init(parse_and_run):
    """Test vanilla grader initialization
    """
    path = parse_and_run(["init", "cpl"])

    with open(os.path.join(path, "grader.yml")) as config_file:
        grader_config = yaml.load(config_file)

    assert grader_config['course-name'] == "cpl"
    assert re.match(UUID_RE, grader_config['course-id']) is not None


def test_init_force(parse_and_run):
    """Test forced config overwrite
    """
    path = parse_and_run(["init", "cpl"])
    with open(os.path.join(path, "grader.yml")) as config_file:
        grader_config = yaml.load(config_file)
        previous_id = grader_config['course-id']

    parse_and_run(["init", "--force", "cpl"])
    with open(os.path.join(path, "grader.yml")) as config_file:
        grader_config = yaml.load(config_file)

    assert grader_config['course-id'] != previous_id


def test_init_noforce(parse_and_run):
    """Test that config is not overwritten without force
    """
    parse_and_run(["init", "cpl"])

    try:
        parse_and_run(["init", "cpl"])
        pytest.fail("Overwrote grader.yml")
    except SystemExit:
        pass
