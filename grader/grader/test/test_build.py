import os
import pytest

from subprocess import Popen, PIPE


def has_installed(program):
    """Checks to see if a program is installed using ``which``.

    :param str program: the name of the program we're looking for

    :rtype bool:

    :return: True if it's installed, otherwise False.

    """
    proc = Popen(["which", program], stdout=PIPE, stderr=PIPE)
    exit_code = proc.wait()
    return exit_code == 0


hasdocker = pytest.mark.skipif(not has_installed("docker"),
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
