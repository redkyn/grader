import logging
import os

from grader.assignment.gradesheet import GradeSheet

logger = logging.getLogger(__name__)


class AssignmentException(Exception):
    pass


class Assignment(object):

    @classmethod
    def new(cls, name, dest, gradesheet_repo=None):
        path = os.path.join(dest, name)

        # Make sure the parent directory exists
        if not os.path.exists(dest):
            raise AssignmentException("{} does not exist".format(dest))

        if os.path.exists(path):
            raise AssignmentException("{} exists".format(path))

        # Make assignment root and subdirs
        os.mkdir(path)
        os.mkdir(os.path.join(path, "submissions"))
        os.mkdir(os.path.join(path, "results"))

        if gradesheet_repo:
            GradeSheet.from_repo(path, gradesheet_repo)
        else:
            GradeSheet.new(path)

        return cls(path)

    @property
    def submissions_path(self):
        return os.path.join(self.path, "submissions")

    @property
    def results_path(self):
        return os.path.join(self.path, "results")

    @property
    def gradesheet_path(self):
        return os.path.join(self.path, "gradesheet")

    def __init__(self, path):
        self.path = path

        # Verify that paths exist like we expect
        if not os.path.exists(path):
            raise AssignmentException("Assignment path doesn't exist")
        if not os.path.exists(self.submissions_path):
            raise AssignmentException("Submission path doesn't exist")
        if not os.path.exists(self.results_path):
            raise AssignmentException("Results path doesn't exist")
        if not os.path.exists(self.gradesheet_path):
            raise AssignmentException("GradeSheet path doesn't exist")

        self.gradesheet = GradeSheet(self.gradesheet_path)
