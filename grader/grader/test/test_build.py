import os
import pytest
import shutil


hasdocker = pytest.mark.skipif(shutil.which("docker") is None,
                               reason="Docker must be installed.")
"""A decorator to skip a test if docker is not installed."""


@hasdocker
def test_build(parse_and_run):
    """Test vanilla assignment build
    """
    path = parse_and_run(["init", "cpl"])
    parse_and_run(["new", "a1"])

    dockerfile_path = os.path.join(path, "assignments", "a1",
                                   "gradesheet", "Dockerfile")
    with open(dockerfile_path, 'w') as dockerfile:
        dockerfile.write("FROM ubuntu:12.04")

    parse_and_run(["build", "a1"])
