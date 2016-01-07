import pytest
import shutil
import tempfile
import os

from grader import make_parser


@pytest.fixture
def clean_dir(request):
    oldpath = os.getcwd()
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)

    def cleanup():
        os.chdir(oldpath)
        shutil.rmtree(newpath)

    request.addfinalizer(cleanup)
    return newpath


@pytest.fixture
def parse_and_run(request):
    oldpath = os.getcwd()
    newpath = tempfile.mkdtemp()
    os.chdir(newpath)

    def cleanup():
        os.chdir(oldpath)
        shutil.rmtree(newpath)

    def _parse_and_run(cli_args):
        parser = make_parser()
        args = parser.parse_args(['--path={}'.format(newpath)] + cli_args)
        args.run(args)
        return newpath

    request.addfinalizer(cleanup)
    return _parse_and_run
