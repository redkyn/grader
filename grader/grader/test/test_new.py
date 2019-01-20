import os
import pytest
import yaml

from grader.models.gradesheet import GradeSheetError
from grader.models.config import ConfigValidationError


def test_new_without_repo(parse_and_run):
    """Test vanilla assignment initialization
    """
    path = parse_and_run(["init", "cpl"])
    parse_and_run(["new", "assignment1"])

    a_path = os.path.join(path, "assignments", "assignment1")
    gs_path = os.path.join(a_path, "gradesheet")

    # Assignment directory exists
    assert os.path.exists(a_path)

    # Assignment directory's contents exist
    assert os.path.exists(gs_path)
    assert os.path.exists(os.path.join(a_path, "submissions"))
    assert os.path.exists(os.path.join(a_path, "results"))

    # Gradesheet directory's contents exist
    assert os.path.exists(os.path.join(gs_path, "assignment.yml"))
    assert os.path.exists(os.path.join(gs_path, "Dockerfile"))

    with open(os.path.join(gs_path, "assignment.yml")) as f:
        config = yaml.safe_load(f)

    assert config['assignment-name'] == 'assignment1'


def test_new_with_repo(parse_and_run):
    """Test assignment initialization from existing repository
    """
    path = parse_and_run(["init", "cpl"])
    parse_and_run(["new", "assignment1",
                   "https://github.com/michaelwisely/python-gradesheet.git"])

    a_path = os.path.join(path, "assignments", "assignment1")
    gs_path = os.path.join(a_path, "gradesheet")

    # Assignment directory exists
    assert os.path.exists(a_path)

    # Assignment directory's contents exist
    assert os.path.exists(gs_path)
    assert os.path.exists(os.path.join(a_path, "submissions"))
    assert os.path.exists(os.path.join(a_path, "results"))

    # Gradesheet directory's contents exist
    assert os.path.exists(os.path.join(gs_path, "assignment.yml"))
    assert os.path.exists(os.path.join(gs_path, "Dockerfile"))

    with open(os.path.join(gs_path, "assignment.yml")) as f:
        config = yaml.safe_load(f)

    # Now it's equal to the value from the repo
    assert config['assignment-name'] == 'new-python-assignment'


def test_new_existing_assignment(parse_and_run):
    """Test overwriting an existing an assignment
    """
    parse_and_run(["init", "cpl"])
    parse_and_run(["new", "assignment1"])

    with pytest.raises(FileExistsError):
        parse_and_run(["new", "assignment1"])


def test_new_failed_clone(parse_and_run):
    """Test cloning a bogus repository
    """
    path = parse_and_run(["init", "cpl"])

    with pytest.raises(GradeSheetError):
        parse_and_run(["new", "assignment1",
                       "git://github.com/michaelwisely/nope.git"])

    a_path = os.path.join(path, "assignments", "assignment1")
    assert not os.path.exists(a_path)


def test_new_bad_assignment_name(parse_and_run):
    """Test creating an assignment with a bad name
    """
    path = parse_and_run(["init", "cpl"])

    with pytest.raises(ConfigValidationError):
        parse_and_run(["new", "NOOO%%%OPE!"])

    a_path = os.path.join(path, "assignments", "assignment1")
    assert not os.path.exists(a_path)


def test_new_without_init(parse_and_run):
    """Test creating an assignment without a grader-wide config
    """
    path = parse_and_run(["init", "cpl"])

    os.remove(os.path.join(path, "grader.yml"))
    assert os.listdir(path) == []

    with pytest.raises(SystemExit):
        parse_and_run(["new", "a1"])

    a_path = os.path.join(path, "assignments", "assignment1")
    assert not os.path.exists(a_path)
