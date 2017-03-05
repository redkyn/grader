import asyncio
import concurrent.futures
import logging
from threading import Lock

logger = logging.getLogger(__name__)


def grade(submission, print_lock, rebuild, suppress_output):
    """
    Grade a single submission asyncronously.
    """
    logger.info("Grading submission for %s", submission.user_id)
    output = submission.grade(
        rebuild_container=rebuild, show_output=(not suppress_output)
    )

    if not suppress_output:
        # Synchronously print
        logger.debug("Waiting for print lock.")
        with print_lock:
            print(output)


def async_grade(args, users):
    """
    Asynchronously grade submissions.

    :param argparse.Arguments args: the arguments from the grade
        comand.
    :param dict users: user_id: [Submission, ...], all
        submissions will be graded.
    """
    print_lock = Lock()

    async def run_blocking_tasks(executor):
        loop = asyncio.get_event_loop()
        blocking_tasks = []

        logger.debug("Creating work queue.")
        for user_id, submissions in users.items():
            for submission in submissions:
                blocking_tasks.append(
                    loop.run_in_executor(
                        executor, grade, submission,
                        print_lock, args.rebuild,
                        args.suppress_output))

        logger.debug("Waiting on pool to finish.")
        await asyncio.wait(blocking_tasks)

    logger.debug("Spawning a worker pool with %s workers.", args.j)
    executor = concurrent.futures.ThreadPoolExecutor(
        max_workers=int(args.j)
    )
    event_loop = asyncio.get_event_loop()

    try:
        event_loop.run_until_complete(
            run_blocking_tasks(executor)
        )
    finally:
        event_loop.close()
