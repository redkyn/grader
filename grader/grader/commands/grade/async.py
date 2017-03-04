import asyncio
import concurrent.futures
import logging

logger = logging.getLogger(__name__)


def grade(assignment, submission, user_id, rebuild=False,
          suppress_output=False):
    """
    Grade a single submission asyncronously.
    """
    logger.info("Grading submission for %s", user_id)
    output = submission.grade(assignment, rebuild_container=rebuild,
                              show_output=False)
    if not suppress_output:
        print(output)


def async_grade(args, assignment, users):
    """
    Asynchronously grade submissions.

    :param argparse.Arguments args: the arguments from the grade
        comand.
    :param Assignment assignment: the assignment for which to grade
        submissions.
    :param dict users: user_id: [Submission, ...], all
        submissions will be graded.
    """
    async def run_blocking_tasks(executor):
        loop = asyncio.get_event_loop()
        blocking_tasks = []

        logger.debug("Creating work queue.")
        for user_id, submissions in users.items():
            for submission in submissions:
                blocking_tasks.append(
                    loop.run_in_executor(
                        executor, grade, assignment, submission, user_id,
                        args.rebuild, args.suppress_output))

        logger.debug("Waiting on pool to finish.")
        await asyncio.wait(blocking_tasks)

    logger.debug("Spawning a worker pool with %s workers.", args.j)
    executor = concurrent.futures.ProcessPoolExecutor(
        max_workers=int(args.j)
    )
    event_loop = asyncio.get_event_loop()

    try:
        event_loop.run_until_complete(
            run_blocking_tasks(executor)
        )
    finally:
        event_loop.close()
