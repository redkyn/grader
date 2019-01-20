import os
import pytest
import tarfile
import tempfile
import yaml

from grader.models.submission import SubmissionImportError


def init_and_build_roster(p_and_r):
    path = p_and_r(["init", "cpl"])
    config_path = os.path.join(path, "grader.yml")

    assert os.path.exists(path)

    with open(config_path) as config:
        content = yaml.safe_load(config)
        content['roster'] = [
            {'name': 'Finn Mertens', 'id': 'fmm000'},
            {'name': 'Jake the Dog', 'id': 'jtd111'},
        ]

    with open(config_path, 'w') as config:
        config.write(yaml.dump(content))

    return path


def make_student_folder(dest, student_id, filenames=["main.py"]):
    student_dir = os.path.join(dest, student_id)
    os.mkdir(student_dir)
    for filename in filenames:
        with open(os.path.join(student_dir, filename), 'w') as f:
            f.write("")
    return student_dir


def make_student_tarball(dest, student_id, filenames=["main.py"]):
    student_tarball = os.path.join(dest, student_id + ".tar.gz")

    with tempfile.TemporaryDirectory() as tempdir:
        student_dir = make_student_folder(tempdir, student_id, filenames)
        with tarfile.open(student_tarball, "w:gz") as tar:
            tar.add(student_dir, student_id)

    return student_tarball


def check_grader_tarfile(grader_path, student_id, filenames=["main.py"]):
    submission_dir = os.path.join(grader_path, "assignments",
                                  "a1", "submissions")
    tar_filename, = os.listdir(submission_dir)
    assert tar_filename.startswith(student_id)
    assert tar_filename.endswith(".tar.gz")
    assert len(tar_filename) == (45 + len(student_id))

    tar_path = os.path.join(submission_dir, tar_filename)
    with tempfile.TemporaryDirectory() as tempdir:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(tempdir)

        name, = os.listdir(tempdir)
        assert name == student_id

        inner_dir = os.path.join(tempdir, student_id)
        assert sorted(os.listdir(inner_dir)) == sorted(filenames)


def test_make_student_folder(clean_dir):
    """Test our utility function
    """
    student_dir = make_student_folder(clean_dir, "jtd111")

    # Check the folder we made
    assert os.path.join(clean_dir, "jtd111") == student_dir
    assert os.path.isdir(student_dir)

    # Make sure that's all we've got in there
    assert os.listdir(clean_dir) == ["jtd111"]

    # Look for filenames
    assert os.listdir(student_dir) == ["main.py"]


def test_make_student_tarball(clean_dir):
    """Test our utility function
    """
    student_tarball = make_student_tarball(clean_dir, "jtd111")

    assert tarfile.is_tarfile(student_tarball)

    # Make sure that's all we've got in there
    assert os.listdir(clean_dir) == ["jtd111.tar.gz"]

    with tempfile.TemporaryDirectory() as tempdir:
        with tarfile.open(student_tarball, "r:gz") as tar:
            tar.extractall(tempdir)

        # Look for folder
        assert os.listdir(tempdir) == ["jtd111"]

        # ... and files
        assert os.listdir(os.path.join(tempdir, "jtd111")) == ["main.py"]


def test_import_single_folder(clean_dir, parse_and_run):
    """Test importing a single folder
    """
    student_dir = make_student_folder(clean_dir, "jtd111")

    # Make sure that's all we've got in there
    assert os.listdir(clean_dir) == ["jtd111"]
    assert os.path.isdir(os.path.join(clean_dir, "jtd111"))

    path = init_and_build_roster(parse_and_run)
    parse_and_run(["new", "a1"])
    parse_and_run(["import", "--kind=single",  "a1", student_dir])

    check_grader_tarfile(path, "jtd111")


def test_import_single_tarball(clean_dir, parse_and_run):
    """Test importing a single tarball
    """
    student_tarball = make_student_tarball(clean_dir, "jtd111")

    # Make sure we're setting things up right...
    assert os.listdir(clean_dir) == ['jtd111.tar.gz']

    path = init_and_build_roster(parse_and_run)
    parse_and_run(["new", "a1"])
    parse_and_run(["import", "--kind=single",  "a1", student_tarball])

    check_grader_tarfile(path, "jtd111")


def test_import_tarball_with_file(clean_dir, parse_and_run):
    """Test importing a single tarball that contains a file instead of a
    directory.

    """
    # A place to store the tarball
    student_tarball = os.path.join(clean_dir, "jtd111.tar.gz")

    # Setup the grader
    init_and_build_roster(parse_and_run)
    parse_and_run(["new", "a1"])

    # Put a file in the .tar.gz instead of a directory
    _, temp = tempfile.mkstemp()
    with tarfile.open(student_tarball, "w:gz") as tar:
        tar.add(temp, "jtd111")
    os.remove(temp)

    with pytest.raises(SubmissionImportError) as err:
        parse_and_run(["import", "--kind=single",  "a1", student_tarball])

    assert "should be a directory" in str(err)


def test_import_tarball_bad_dirname(clean_dir, parse_and_run):
    """Test importing a single tarball that contains a directory with a
    bad name

    """
    # A place to store the tarball
    student_tarball = os.path.join(clean_dir, "jtd111.tar.gz")

    # Setup the grader
    init_and_build_roster(parse_and_run)
    parse_and_run(["new", "a1"])

    # Put a directory with a bad name in the tarball this time
    temp = tempfile.mkdtemp()
    with tarfile.open(student_tarball, "w:gz") as tar:
        tar.add(temp, "wrong")
    os.rmdir(temp)

    with pytest.raises(SubmissionImportError) as err:
        parse_and_run(["import", "--kind=single",  "a1", student_tarball])

    assert "Inner folder" in str(err)


def test_import_tarball_bad_name(clean_dir, parse_and_run):
    """Test importing a single tarball that has a bad name

    """
    # A place to store the tarball
    student_tarball = make_student_tarball(clean_dir, "nope")

    # Setup the grader
    init_and_build_roster(parse_and_run)
    parse_and_run(["new", "a1"])

    with pytest.raises(SubmissionImportError) as err:
        parse_and_run(["import", "--kind=single",  "a1", student_tarball])

    assert "match a student id." in str(err)


def test_import_tarball_name_mismatch(clean_dir, parse_and_run):
    """Test importing a single tarball that contains a folder whose name
    doesn't match the name of the tarball

    """
    student_tarball = make_student_tarball(clean_dir, "jtd111")

    # Setup the grader
    init_and_build_roster(parse_and_run)
    parse_and_run(["new", "a1"])

    # Put a directory with a mismatched student id in the tarball
    temp = tempfile.mkdtemp()
    with tarfile.open(student_tarball, "w:gz") as tar:
        tar.add(temp, "fmm000")
    os.rmdir(temp)

    with pytest.raises(SubmissionImportError) as err:
        parse_and_run(["import", "--kind=single",  "a1", student_tarball])

    assert "Inner folder" in str(err)
