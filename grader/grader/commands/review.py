'''TODO: Build command docs
'''
import logging
from subprocess import call
import os

from grader.models import Grader
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Opens results for each submission along with submission code in an \
        editor."


def setup_parser(parser):
    parser.add_argument('assignment',
                        help='Name of the assignment to cycle through results \
                                for.')
    parser.add_argument('--start-at', nargs='?',
                        help='Begin the cycle at this student username.')
    parser.set_defaults(run=run)


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)

    if len(a.submissions_by_user) == 0:
        logger.error("There are no graded submissions for this assignment.")
        return

    if args.start_at and args.start_at not in a.submissions_by_user:
        logger.error("User does not have a graded submission available.")
        return

    review_loop(a, args.start_at)


def review_loop(assignment, start_at):
    # Figure out where to start at (index)
    user_ids = sorted(assignment.submissions_by_user.keys())
    editor = assignment.gradesheet.config \
        .get("review-editor", "/usr/bin/vim -O2 {0} {1} {2} {3}")

    i = 0
    if start_at:
        i = user_ids.index(start_at)

    while i < len(user_ids):
        user = user_ids[i]
        subs = assignment.submissions_by_user[user]
        sub = submission_choice(assignment, user, subs)

        review_files(sub, editor)

        if i != len(user_ids)-1:
            print("Finished grading {0}, {1} more remain.".format(user,
                  len(user_ids)-i-1))
            print("{0} is next.\n".format(user_ids[i+1]))

            choice = "A"
            while choice.upper() not in ["C", "Q", ""]:
                print("C) Continue (default)")
                print("Q) Quit")

                choice = input("\nSelect a command: ")

            if choice.upper() == "Q":
                break
            i += 1  # continue


def submission_choice(assignment, user_id, subs):
    # FIXME: Combine code with inspect

    # If they have multiple submissions, make them choose
    if len(subs) > 1:
        print("{0} submissions found for {1}, choose one:\n"
              .format(len(subs), user_id))
        i = 1
        print("Index\tCreated")
        for s in subs:
            info = assignment.docker_cli.inspect_container(s.full_id)
            print("{0}\t{1}".format(i, info['Created']))
            i += 1
        choice = -1
        while choice < 0 or choice >= len(subs):
            choice = input("Please enter your selection: ")
            try:
                choice = int(choice)-1
            except:
                pass

        return subs[choice]
    else:
        return subs[0]


def review_files(sub, editor):
    # Get all submitted files
    with sub.unpacked_files as sub_dir:
        # gross... the idea is to get all files in the submission
        # directory into a list.
        sub_files_by_dir = [[x[0], x[2]] for x in os.walk(sub_dir) if
                            len(x[2]) > 0]
        sub_files = []

        for dir in sub_files_by_dir:
            for f in dir[1]:
                sub_files.append(os.path.join(dir[0], f))

        results = sub.results_files
        com_args = []

        # Smash all of our files into a list so it looks like:
        # [first submission file, first result file, other submission
        #   files, other result files]
        for type in [sub_files, results]:
            if len(type) > 0:
                com_args.append(type[0])
            else:
                com_args.append("")

        for type in [sub_files, results]:
            if len(type) > 1:
                com_args.append(' '.join(type[1:]))
            else:
                com_args.append("")

        # Call with first file, second file, then all other files
        call(list(filter(lambda x: x != "",
             editor.format(*com_args).split(' '))))
