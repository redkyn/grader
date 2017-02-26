import datetime
import logging

from grader.models import Grader
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Remove student container(s)"


def setup_parser(parser):
    parser.add_argument('--exclude-listed', action='store_true', default=False,
                        help='Preserve the specified student_id\'s containers instead of removing them.')
    parser.add_argument('assignment',
                        help='Name of the assignment to delete containers from.')
    parser.add_argument('student_ids',
                        default=[], nargs='*',
                        help='Optionally delete just (a) specified student(s)\'s container.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)

    if args.student_ids != []:
        submissions_to_delete = {k: v for k, v in a.submissions_by_user.items()
                                 if (not args.exclude_listed and k in args.student_ids)
                                   or (args.exclude_listed and k not in args.student_ids)}
    else:
        submissions_to_delete = a.submissions_by_user

    if len(submissions_to_delete) == 0:
        logger.info("No submissions found.")
        return

    # Gather containers by student_id
    containers_to_delete = {}
    for student_id, submissions in submissions_to_delete.items():
        if len(submissions) == 0:
            continue

        containers = [submission.get_all_container_ids() for submission in submissions]
        containers = sum(containers, [])  # Flattens
        if len(containers) == 0:
            logger.debug("  No containers for {}".format(student_id))
            continue

        containers_to_delete[student_id] = containers

    if len(containers_to_delete) == 0:
        logger.info("No containers found.")
        return

    logger.info("Containers to delete: ")
    for student_id, containers in containers_to_delete.items():
        logger.info("  %s (%i container(s)):", student_id, len(containers))

        for container in containers:
            created = datetime.datetime.fromtimestamp(container['Created']).strftime('%Y-%m-%d %H:%M:%S')
            logger.info("    %s created on %s", container['Id'], created)

    answer = input("Are you sure you wish to remove the containers listed above [yes/no] (no): ")
    if answer != "yes":
        logger.info("Aborted")
        return

    for _, containers in containers_to_delete.items():
        for container in containers:
            logger.info("Removing container %s", container['Id'])
            a.docker_cli.stop(container=container['Id'])
            a.docker_cli.remove_container(container['Id'])
