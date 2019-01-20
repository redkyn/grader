import logging
import shutil
import subprocess

from grader.models import Grader
from grader.utils.config import require_grader_config
from grader.utils.interactive import submission_choice

logger = logging.getLogger(__name__)

help = "Inspect a graded submission's container."


def setup_parser(parser):
    parser.add_argument('assignment',
                        help='Name of the assignment which the user has a '
                             'graded submission for.')
    parser.add_argument('student_id',
                        help='Inspect submission belonging to this student.')
    parser.add_argument('--user',
                        help="Linux user to inspect as")
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)

    if args.student_id not in a.submissions_by_user:
        logger.error("User does not have a graded submission available.")
        return

    user_submissions = a.submissions_by_user[args.student_id]
    id = submission_choice(a, args.student_id, user_submissions).full_id

    inspect(a, id, args.user)

def inspect(a, id, user=None):
    shell = a.gradesheet.config.get('shell', '/bin/bash')

    # Start container, run exec, stop container
    logger.info("Starting container {0}".format(id))
    a.docker_cli.start(container=id)

    command = [shutil.which("docker"), "exec", "-it"]
    if user:
        command.extend(["-u", user])

    command.extend([id, shell])
    subprocess.call(command)

    logger.info("Stopping container {0}".format(id))
    a.docker_cli.stop(container=id)
