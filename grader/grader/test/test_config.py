import os
import pytest
import uuid
import yaml

from grader.models import Grader, ConfigValidationException


def write_config(path, name, config):
    with open(os.path.join(path, name), 'w') as config_file:
        config_file.write(yaml.dump(config))


def test_correct_config(clean_dir):
    """Test loading Grader with a correct config
    """
    write_config(clean_dir, "grader.yml", {
        "course-name": "cs2001",
        "course-id": str(uuid.uuid4()),
        "roster": [
            {"name": "Finn Mertens", "id": "fmmmm4"},
            {"name": "Jake the Dog", "id": "jtdbb9"}
        ],
    })

    Grader(clean_dir)


def test_bad_course_name_value(clean_dir):
    """Test loading Grader config with a bad course name
    """
    write_config(clean_dir, "grader.yml", {
        "course-name": "Noooo%%%pe",
        "course-id": str(uuid.uuid4())
    })

    with pytest.raises(ConfigValidationException):
        Grader(clean_dir)


def test_bad_course_name_key(clean_dir):
    """Test loading Grader config with a bad course name key
    """
    write_config(clean_dir, "grader.yml", {
        "course-wrong": "cs2001",
        "course-id": str(uuid.uuid4())
    })

    with pytest.raises(ConfigValidationException):
        Grader(clean_dir)


def test_missing_course_name(clean_dir):
    """Test loading Grader config with a missing course name
    """
    write_config(clean_dir, "grader.yml", {
        "course-id": str(uuid.uuid4())
    })

    with pytest.raises(ConfigValidationException):
        Grader(clean_dir)


def test_bad_course_id_value(clean_dir):
    """Test loading Grader config with a bad course id
    """
    write_config(clean_dir, "grader.yml", {
        "course-name": "cs2001",
        "course-id": "invalid %%% key"
    })

    with pytest.raises(ConfigValidationException):
        Grader(clean_dir)


def test_bad_course_id_key(clean_dir):
    """Test loading Grader config with a bad course id key
    """
    write_config(clean_dir, "grader.yml", {
        "course-name": "cs2001",
        "course-id-wrong": str(uuid.uuid4())
    })

    with pytest.raises(ConfigValidationException):
        Grader(clean_dir)


def test_missing_course_id(clean_dir):
    """Test loading Grader config with a missing course id
    """
    write_config(clean_dir, "grader.yml", {
        "course-name": "cs2001"
    })

    with pytest.raises(ConfigValidationException):
        Grader(clean_dir)


def test_missing_roster_items(clean_dir):
    """Test loading Grader config with missing roster items
    """

    # Forgot the name
    write_config(clean_dir, "grader.yml", {
        "course-name": "cs2001",
        "course-id": str(uuid.uuid4()),
        "roster": [
            {"id": "fmmmm4"},
            {"name": "Jake the Dog", "id": "jtdbb9"}
        ],
    })

    with pytest.raises(ConfigValidationException):
        Grader(clean_dir)

    # Forgot the id
    write_config(clean_dir, "grader.yml", {
        "course-name": "cs2001",
        "course-id": str(uuid.uuid4()),
        "roster": [
            {"name": "Finn Mertens"},
            {"name": "Jake the Dog", "id": "jtdbb9"}
        ],
    })

    with pytest.raises(ConfigValidationException):
        Grader(clean_dir)


def test_bad_roster_id(clean_dir):
    """Test loading Grader config with a bad course id
    """
    write_config(clean_dir, "grader.yml", {
        "course-name": "cs2001",
        "course-id": str(uuid.uuid4()),
        "roster": [
            {"name": "Finn Mertens", "id": "NOOOO%%%OPE!"},
            {"name": "Jake the Dog", "id": "jtdbb9"}
        ],
    })

    with pytest.raises(ConfigValidationException):
        Grader(clean_dir)
