class SubmissionError(Exception):
    pass


class Submission(object):

    @classmethod
    def import_blackboard_zip(cls, assignment, zip_path, sid_pattern=None):
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
    def import_folder(cls, assignment, folder_path, sid_pattern=None):
        """Imports submissions from a folder of ``.tar.gz``s

        The names of the ``.tar.gz`` files (minus extensions) will be
        used as the ID for each submission. For example, if a folder
        contains ``hsimpson.tar.gz``, a new Submission with id
        ``hsimpson`` will be created.

        :param str assignment: Assignment associated with this submission

        :param str folder_path: Path to the folder of `.tar.gz``s to
            import

        :param str sid_pattern: An optional pattern to use to convert
            the name of a submission to a submission id

        :return: A list of Submissions

        """
        raise NotImplementedError("Folder import isn't implemented yet :/")

    @classmethod
    def import_file(cls, assignment, submission_path, sid=None):
        """Imports a submission.

        The submission may be:

        * A ``.tar.gz`` file.

        * A folder containing files to submit. The folder will be
          compressed as a ``.tar.gz`` then imported.

        The name of the submission (minus extensions) will be used as
        its ID. For example, if a folder is named ``hsimpson/``, the
        new Submission with id ``hsimpson`` will be created.

        :param str assignment: Assignment associated with this submission

        :param str submission_path: Path to the submission item

        :return: the new submission
        :rtype: Submission

        """
        raise NotImplementedError("Folder import isn't implemented yet :/")

    @classmethod
    def import_repo(cls, assignment, repo_url, sid=None):
        """Imports a submission from a git repository

        :param str assignment: Assignment associated with this submission

        :param str repo_url: URL to a clone-able git repository.

        :param str sid: The submission ID for the new submission. If
            None, the name of the repository (sans ``.git``) will be
            used.

        :return: the new submission
        :rtype: Submission

        """
        raise NotImplementedError("Git import isn't implemented yet :/")

    @classmethod
    def get_importers(cls):
        return {
            'blackboard': cls.import_blackboard_zip,
            'multiple': cls.import_folder,
            'single': cls.import_file,
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

    def __init__(self, assignment):
        self.assignment = assignment
        self.path = self.assignment.submissions_path
