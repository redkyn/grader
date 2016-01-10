import git
import hashlib
import logging
import os
import re
import shutil
import tarfile
import tempfile
import uuid

from contextlib import contextmanager
from datetime import datetime

from grader.utils.files import make_tarball

logger = logging.getLogger(__name__)


class SubmissionError(Exception):
    """A general-purpose exception thrown by the Submission class

    """
    pass


class SubmissionIDError(SubmissionError):
    """An exception thrown for errors related to Submission IDs

    """
    pass


class SubmissionImportError(SubmissionError):
    """An exception throws for errors related to Submission import

    """
    pass


class Submission(object):
    """An assignment submission.

    A Submission essentially represents a ``.tar.gz`` file on disk
    that contains a student assignment submission.

    """

    SUBMISSION_ID_RE = re.compile(
        r"^(?P<student_id>\w+)--(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$"  # NOQA
    )
    """Full submission IDs must match this pattern"""

    @classmethod
    def split_full_id(cls, full_id):
        """Splits a full Submission ID into the student's ID, and the
        submission's UUID

        :param str full_id: A full submission ID. See
            :data:`SUBMISSSION_ID_RE`

        :return: The student's id, and the submission's UUID
        :rtype: (str, str)

        """
        match = cls.SUBMISSION_ID_RE.match(full_id)
        if match is None:
            raise SubmissionIDError("Bad id: {}".format(full_id))
        return (match.group("student_id"), match.group("uuid"))

    @classmethod
    def get_full_id(cls, basename, sid=None, sid_pattern=r"(?P<id>.*)"):
        """Generates a full Submission ID based on the student's ID

        :param str basename: The basename of a file to use for
            generating the submisison id. This string should contain
            the student's ID in some way.

        :param str sid: If provided, this will be used as the
            student's ID.

        :param str sid_pattern: If provided, this will be used to pull
            the student's ID out of ``basename``. The match group
            named "id" (i.e., ``match.group('id')``) will be used as
            the student's id.

        :raises SubmissionError: If there was an issue with matching
            basename against ``sid_pattern``

        :return: The full submission id (for filenames)
        :rtype: str

        """
        match = re.match(sid_pattern, basename)
        if sid is None and match is not None:
            try:
                sid = match.group('id')
            except IndexError:
                raise SubmissionError(
                    "{} is missing 'id' group.".format(sid_pattern)
                )

        if sid is None:
            raise SubmissionError(
                'Submission ID pattern "{}" does not '
                'match file name "{}"'.format(sid_pattern, basename)
            )

        full_id = "{}--{}".format(sid, uuid.uuid4())
        cls.split_full_id(full_id)  # Make sure we don't raise an error
        return full_id

    @classmethod
    def _check_tarball(cls, assignment, path, student_id):
        with tempfile.TemporaryDirectory() as tmpdir:
            with tarfile.open(path, "r:gz") as tar:
                tar.extractall(tmpdir)

            try:
                # Try to unpack our single folder
                name, = os.listdir(tmpdir)
            except ValueError:
                raise SubmissionImportError(
                    'Expected exactly one item at the root. '
                    'Found {}.'.format(os.listdir(tmpdir))
                )

            if name != student_id:
                raise SubmissionImportError(
                    'Could not find "{}" in the roster.'.format(name)
                )

            if not os.path.isdir(os.path.join(tmpdir, name)):
                raise SubmissionImportError(
                    '"{}" in {} should be a directory, '
                    'not a file.'.format(name, path)
                )

    @classmethod
    def _check_submission_item(cls, assignment, path):
        """Checks whether the submission item meets the following
        requirements:

        * Its name (minus extensions) matches a student ID from the
          grader's roster.

        * If the submission item is a .tar.gz, it contains a single
          directory.

        :param str full_id: A full submission ID. See
            :data:`SUBMISSSION_ID_RE`

        :return: None

        :raises SubmissionError: if the submission item doesn't meet
            the requirements described above

        """
        # Check the name of the item
        basename = os.path.basename(path)
        match = re.match(r"(.*?)(?:\.tar\.gz)?$", basename)
        if match is None:
            raise SubmissionImportError(
                'Unsure how to handle basename "{}".'.format(basename)
            )

        student_id = match.group(1)
        if student_id not in assignment.grader.student_ids:
            raise SubmissionImportError(
                'Expected "{}" to match a student id.'.format(basename)
            )

        if os.path.isfile(path) and tarfile.is_tarfile(path):
            cls._check_tarball(assignment, path, student_id)

    @classmethod
    def import_blackboard_zip(cls, assignment, zip_path,
                              sid_pattern=r"(?P<id>.*)"):
        """Imports submissions from a ZIP downloaded from Blackboard

        :param str assignment: Assignment associated with this submission

        :param str zip_path: Path to the Blackboard ZIP to import

        :param str sid_pattern: An optional pattern to use to convert
            the name of a submission to a submission id

        :return: A list of Submissions

        """
        # TODO figure out how Blackboard names and organizes the items
        # in the assignment ZIP.
        raise NotImplementedError("Blackboard import isn't implemented yet :/")

    @classmethod
    def import_multiple(cls, assignment, source, sid_pattern=r"(?P<id>.*)"):
        """Imports multiple submissions from a folder of ``.tar.gz``'s or
        folders of submission material.

        By default, the names of the ``.tar.gz`` files (minus
        extensions) will be used as the ID for each submission. For
        example, if a folder contains ``hsimpson.tar.gz``, a new
        Submission with id ``hsimpson`` will be created.

        :param str assignment: Assignment associated with this submission

        :param str source: Path to the folder of
            ``.tar.gz``s/folders to import

        :param str sid_pattern: An optional pattern to use to convert
            the name of a submission to a submission id

        :return: A list of Submissions

        """
        # Make sure this is actually a folder
        if not os.path.isdir(source):
            raise NotADirectoryError(
                "{} is not a directory. Cannot import.".format(source)
            )

        # Make sure we can import all the items in this folder
        for item in os.listdir(source):
            item = os.path.join(source, item)
            if os.path.isfile(item) and tarfile.is_tarfile(item):
                logger.debug("%s is a tarfile", item)
                continue
            elif os.path.isdir(item):
                logger.debug("%s is a directory", item)
                continue
            else:
                raise SubmissionError(
                    "{} is neither a directory nor a tarball".format(item)
                )

        # Import the items
        def import_it(path):
            fullpath = os.path.join(source, path)
            try:
                submission, = cls.import_single(
                    assignment, fullpath, sid_pattern=sid_pattern
                )
                return submission
            except SubmissionError as e:
                logger.info("Could not import %s. %s", path, e)

        return [import_it(p) for p in os.listdir(source)]

    @classmethod
    def import_single(cls, assignment, source,
                      sid=None, sid_pattern=r"(?P<id>.*)"):
        """Imports a single submission.

        The submission may be:

        * A ``.tar.gz`` file.

        * A folder containing files to submit. The folder will be
          compressed as a ``.tar.gz`` then imported.

        By default the name of the submission (minus extensions) will
        be used as its ID. For example, if a folder is named
        ``hsimpson/``, the new Submission with id ``hsimpson`` will be
        created.

        :param str assignment: Assignment associated with this submission

        :param str source: Path to the submission item

        :param str sid: The submission id to use. If None, the
            basename of ``source`` will be used.

        :param str sid_pattern: An optional pattern to use to convert
            the name of a submission to a submission id

        :return: A list containing a single item: the new Submission

        """
        # Remove trailing slashes from the path
        source = os.path.normpath(source)

        # See if it's structured properly
        cls._check_submission_item(assignment, source)

        # Ditch all file extensions
        # NOTE: source filenames cannot contain '.'
        basename, *_ = os.path.basename(source).split('.')

        # Get a unique ID for this submission
        submission_id = cls.get_full_id(basename, sid, sid_pattern)

        # Compute the path to the completed .tar.gz
        tar_name = submission_id + ".tar.gz"
        dest = os.path.join(assignment.submissions_dir, tar_name)

        # Prepare the tarball (if necessary)
        tarball, temp_path = None, None
        if os.path.isdir(source):
            logger.debug("Importing a single directory: %s", source)
            tarball, temp_path = make_tarball(source, submission_id)
        elif os.path.isfile(source) and tarfile.is_tarfile(source):
            logger.debug("Importing a single tarball: %s", source)
            tarball = source
        else:
            logger.debug("Cannot import this thing.")
            raise SubmissionError(
                "{} is neither a directory nor a tarball.".format(source)
            )

        # Copy it
        shutil.copyfile(tarball, dest)

        # Clean up if necessary
        if temp_path:
            logger.debug("Removing %s", temp_path)
            shutil.rmtree(temp_path)

        return [cls(assignment, tar_name)]

    @classmethod
    def import_repo(cls, assignment, repo_url, sid=None,
                    sid_pattern=r"(?P<id>.*)"):
        """Imports a submission from a git repository

        :param str assignment: Assignment associated with this submission

        :param str repo_url: URL to a clone-able git repository.

        :param str sid: The submission ID for the new submission. If
            None, the name of the repository (sans ``.git``) will be
            used.

        :param str sid_pattern: An optional pattern to use to convert
            the name of a submission to a submission id

        :return: the new submission
        :rtype: Submission

        """
        raise NotImplementedError("Git import isn't implemented yet :/")

    @classmethod
    def get_importers(cls):
        """Returns a dict that maps nicknames for importers to classmethods.

        :rtype: dict
        """
        return {
            'blackboard': cls.import_blackboard_zip,
            'multiple': cls.import_multiple,
            'single': cls.import_single,
            'repo': cls.import_repo,
        }

    @classmethod
    def get_importer(cls, submission_type):
        """Returns an importer function for a given submission type. Refer to
            the definition of :meth:`Submission.get_importers` for a
            list of acceptable values for ``submission_type``.

        :param str submission_type: The type of submission to import.

        :return: a function that will import a submission into Grader

        :raises SubmissionError: if no importer can be found
        """
        try:
            return cls.get_importers()[submission_type]
        except KeyError as e:
            raise SubmissionError(
                'No importer for type "{}"'.format(submission_type)
            ) from e

    @property
    def import_time(self):
        """The time stamp on the Submission (as a datetime object)"""
        return datetime.fromtimestamp(int(os.path.getmtime(self.path)))

    @property
    def file_mtimes(self):
        """A dict mapping file names (from the submission archive) a datetime
        object indicating the last time that file was modified"""
        with tarfile.open(self.path, "r:gz") as tar:
            return {info.name: info.mtime for info in tar}

    @property
    def latest_mtime(self):
        """The time stamp of the most recently modified file in the submission
        archive (as a datetime object)

        """
        return datetime.fromtimestamp(max(self.file_mtimes.values()))

    @property
    def sha1sum(self):
        """The SHA1 sum of the submission archive"""
        sha1 = hashlib.sha1()
        with open(self.path, 'rb') as f:
            while True:
                buf = f.read(1024)
                if not buf:
                    break
                sha1.update(buf)
        return sha1.hexdigest()

    @property
    @contextmanager
    def unpacked_files(self):
        """A context manager for working with unpacked submissions. Returns
        the name of the directory where all files are unpacked. When
        the context is exited, the directory and its contents are
        deleted.

        """
        with tempfile.TemporaryDirectory() as tmpdir:
            with tarfile.open(self.path, "r:gz") as tar:
                tar.extractall(tmpdir)
            yield tmpdir

    @property
    @contextmanager
    def unpacked_repo(self):
        """A context manager for working with unpacked submission
        repositories. Returns a git.Repo object corresponding to the
        submission's repository.

        If the submission is not a git repository, then "None" is
        returned.

        """
        with self.unpacked_files as unpacked:
            try:
                subdir, = os.listdir(unpacked)
                yield git.Repo(os.path.join(unpacked, subdir))
            except ValueError:
                yield None
            except git.InvalidGitRepositoryError:
                yield None

    @property
    def latest_commit(self):
        """The time stamp of the default branch of the submission, or None if
        the submission isn't a git repository.

        """
        with self.unpacked_repo as repo:
            if repo:
                time = repo.heads[0].commit.committed_date
                return datetime.fromtimestamp(time)

    def __init__(self, assignment, tar_name):
        """Instantiates a new Submission.

        :param str assignment: The :class:`Assignment` object to which
            this assignment belongs.

        :param str tar_name: The name of the submission's .tar.gz file
            (including extension)

        """
        self.path = os.path.join(assignment.submissions_dir, tar_name)
        self.assignment = assignment

        if not os.path.isfile(self.path):
            logger.debug("Cannot find %s", self.path)
            raise FileNotFoundError("Submission doesn't exist.")
        if not tarfile.is_tarfile(self.path):
            logger.debug("%s is not a tarball", self.path)
            raise SubmissionError("Submission is screwed up...")

        self.basename = os.path.basename(self.path)
        full_id, *_ = self.basename.split('.')
        self.user_id, self.uuid = self.split_full_id(full_id)

    def __str__(self):
        """String representation of a Submission"""
        return "Submission {} ({})".format(self.user_id, self.uuid)
