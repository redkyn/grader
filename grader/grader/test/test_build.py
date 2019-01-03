import os
import pytest
import shutil

from grader.models import Grader
from grader.models.assignment import AssignmentBuildError


hasdocker = pytest.mark.skipif(shutil.which("docker") is None,
                               reason="Docker must be installed.")
"""A decorator to skip a test if docker is not installed."""


@hasdocker
def test_build(parse_and_run):
    """Test vanilla assignment build
    """
    path = parse_and_run(["init", "cpl"])
    parse_and_run(["new", "a1"])

    # Give it a buildable Dockerfile
    dockerfile_path = os.path.join(path, "assignments", "a1",
                                   "gradesheet", "Dockerfile")
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write("FROM busybox")

    # Build the image
    parse_and_run(["build", "a1"])

    # Remove the built image
    g = Grader(path)
    a, = g.assignments.values()
    a.delete_image()


@hasdocker
def test_build_bad_dockerfile(parse_and_run):
    """Test building an image that has a bad Dockerfile
    """
    path = parse_and_run(["init", "cpl"])
    parse_and_run(["new", "a1"])

    dockerfile_path = os.path.join(path, "assignments", "a1",
                                   "gradesheet", "Dockerfile")
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write("NOPE WHAT ubuntu:12.04")

    with pytest.raises(AssignmentBuildError):
        parse_and_run(["build", "a1"])


@hasdocker
def test_build_empty_dockerfile(parse_and_run):
    """Test building an image that has an empty Dockerfile
    """
    path = parse_and_run(["init", "cpl"])
    parse_and_run(["new", "a1"])

    dockerfile_path = os.path.join(path, "assignments", "a1",
                                   "gradesheet", "Dockerfile")
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write("")

    with pytest.raises(AssignmentBuildError):
        parse_and_run(["build", "a1"])


@hasdocker
def test_build_missing_assignment_dir(parse_and_run):
    """Test building an image without an assignments/ dir
    """
    parse_and_run(["init", "cpl"])

    with pytest.raises(FileNotFoundError):
        parse_and_run(["build", "a1"])


@hasdocker
def test_build_missing_assignment_specific_dir(parse_and_run):
    """Test building an image without an assignment-specific dir
    """
    path = parse_and_run(["init", "cpl"])
    parse_and_run(["new", "a1"])

    g = Grader(path)
    a = g.get_assignment("a1")
    shutil.rmtree(a.submissions_dir)

    with pytest.raises(FileNotFoundError):
        parse_and_run(["build", "a1"])
