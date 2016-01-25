'''TODO: Build command docs
'''
import logging
import os
from docker import Client

from grader.models import Grader
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Inspect a graded submission container."


def setup_parser(parser):
    parser.add_argument('assignment',
                        help='Name of the assignment which the user has a \
                                graded submission for.')
    parser.add_argument('username',
                        help='Username of the submission to inspect.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)
    
    submissions = a.submissions_by_user

    if args.username not in submissions:
        logger.error("User does not have a graded submission available.")
        return

    user_submissions = submissions[args.username]
    if len(user_submissions) > 1:
        logger.error("FIXME: Only supporting one submission (there are {0})."\
                .format(len(user_submissions)))
        return

    shell = a.gradesheet.config.get('shell', '/bin/bash')
    id = user_submissions[0].full_id

    # Start the container
    cli = Client(base_url='unix://var/run/docker.sock')
    cli.start(container=id)
    os.execl("/usr/bin/docker", "", "exec", "-it", id, shell)
    #os.execv?

