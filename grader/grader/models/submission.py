import functools
import logging
import os
import re
import shutil
import tarfile
import uuid

from grader.utils.files import make_tarball

logger = logging.getLogger(__name__)


class SubmissionError(Exception):
    pass


class Submission(object):
    """An assignment submission.

    A Submission essentially represents a ``.tar.gz`` file on disk
    that contains a student assignment submission.

    """

    SUBMISSION_ID_RE = re.compile(
        r"^(?P<student_id>\w+)--(?P<uuid>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$"  # noqa
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
            raise SubmissionError("Bad id: {}".format(full_id))
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
    def import_blackboard_zip(cls, assignment, zip_path, sid_pattern=r"(?P<id>.*)"):
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
            raise SubmissionError(
                "{} is not a directory. Cannot import.".format(source)
            )

        # Make sure we can import all the items in this folder
        for item in os.listdir(source):
            item = os.path.join(source, item)
            print(item, os.path.isfile(item))
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
        import_it = functools.partial(cls.import_single, assignment,
                                      sid_pattern=sid_pattern)
        return [import_it(os.path.join(source, p))[0]
                for p in os.listdir(source)]

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

        # Ditch all file extensions
        basename, *_ = os.path.basename(source).split('.')

        # Get a unique ID for this submission
        submission_id = cls.get_full_id(basename, sid, sid_pattern)

        # Compute the path to the completed .tar.gz
        dest = os.path.join(assignment.submissions_path,
                            submission_id + ".tar.gz")

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

        return [cls(assignment, dest)]

    @classmethod
    def import_repo(cls, assignment, repo_url, sid=None, sid_pattern=r"(?P<id>.*)"):
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
        return {
            'blackboard': cls.import_blackboard_zip,
            'multiple': cls.import_multiple,
            'single': cls.import_single,
            'repo': cls.import_repo,
        }

    @classmethod
    def get_importer(cls, submission_type):
        try:
            return cls.get_importers()[submission_type]
        except KeyError as e:
            raise SubmissionError(
                'No importer for type "{}"'.format(submission_type)
            ) from e

    def __init__(self, assignment, tar_path):
        self.assignment = assignment
        self.path = tar_path

        if not os.path.isfile(self.path):
            logger.debug("Cannot find %s", self.path)
            raise SubmissionError("Submission doesn't exist.")
        if not tarfile.is_tarfile(self.path):
            logger.debug("%s is not a tarball", self.path)
            raise SubmissionError("Submission is screwed up...")

        self.basename = os.path.basename(self.path)
        full_id, *_ = self.basename.split('.')
        self.user_id, self.uuid = self.split_full_id(full_id)

    def __str__(self):
        return "Submission {} ({})".format(self.user_id, self.uuid)
