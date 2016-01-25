'''TODO: Build command docs
'''
import logging
from subprocess import call

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
    sub = None
    if len(user_submissions) > 0:
        i = 1 
        print("Index\tCreated")
        for s in user_submissions:
            info = a.docker_cli.inspect_container(s.full_id)
            print("{0}\t{1}".format(i, info['Created']))
            i += 1
        choice = -1
        while choice < 0 or choice >= len(user_submissions):
            choice = input("Please enter your selection: ")
            try:
                choice = int(choice)-1
            except:
                choice = -1

        sub = user_submissions[choice]
    else:
        sub = user_submissions[0]

    shell = a.gradesheet.config.get('shell', '/bin/bash')

    logger.info("Starting container {0}".format(sub.id))
    a.docker_cli.start(container=sub.id)

    call(["/usr/bin/docker", "exec", "-it", sub.id, shell])

    logger.info("Stopping container {0}".format(sub.id))
    a.docker_cli.stop(container=id)
