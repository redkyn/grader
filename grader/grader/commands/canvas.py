'''TODO: Import command docs
'''
import logging

from grader.models import Grader, Submission
from grader.utils.config import require_grader_config
from grader.utils.interactive import make_help_parser

from redkyn.canvas import CanvasAPI

from prettytable import PrettyTable

logger = logging.getLogger(__name__)

help = "Import student submission(s)"

def setup_parser(parser):
    subparsers = parser.add_subparsers(title='Canvas commands')

    list_parser = subparsers.add_parser(
        "list", help="List published Canvas courses where you are a teacher, TA, or grader"
    )
    list_parser.set_defaults(run=print_canvas_courses)

    import_parser = subparsers.add_parser(
        "import", help="Import the roster from a specific Canvas course"
    )
    import_parser.add_argument("id", help="Canvas ID for course to import from")
    import_parser.add_argument(
        "--force", action="store_true", help="Import duplicate students anyway"
    )
    import_parser.set_defaults(run=import_from_canvas)

    make_help_parser(
        parser, subparsers, "Show help for roster or one of its commands"
    )


@require_grader_config
def import_from_canvas(args):
    """Imports students from a Canvas course to the roster.
    """

    g = Grader(args.path)
    if 'canvas-token' not in g.config:
        logger.error(
            "canvas-token configuration is missing! Please set the Canvas API access "
            "token before attempting to import users from Canvas"
        )
        print("Import from canvas failed: missing Canvas API access token.")
        return

    course_id = args.id
    force = args.force

    canvas = CanvasAPI(g.config["canvas-token"], g.config["canvas-host"])

    students = canvas.get_course_students(course_id)

    for s in students:
        if 'sis_user_id' not in s:
            logger.error("Could not get username for %s", s['sortable_name'])

        if not force:
            for student in g.config.roster:
                if student['name'] == s['sortable_name']:
                    logger.warning("User %s is already in the roster, skipping", s['sis_user_id'])
                    break
            else:
                g.config.roster.append({'name': s['sortable_name'], 'id': s['sis_user_id']})
        else:
            g.config.roster.append({'name': s['sortable_name'], 'id': s['sis_user_id']})

    print("Imported {} students.".format(len(students)))
    g.config.save()

@require_grader_config
def print_canvas_courses(args):
    """Show a list of current teacher's courses from Canvas via the API.
    """

    g = Grader(args.path)
    if 'canvas-token' not in g.config:
        logger.error("canvas-token configuration is missing! Please set the Canvas API access "
                     "token before attempting to use Canvas API functionality")
        print("Canvas course listing failed: missing Canvas API access token.")
        return

    canvas = CanvasAPI(g.config["canvas-token"], g.config["canvas-host"])

    courses = canvas.get_instructor_courses()

    if not courses:
        print("No courses found where current user is a teacher.")
        return

    output = PrettyTable(["#", "ID", "Name"])
    output.align["Name"] = "l"

    for ix, c in enumerate(sorted(courses, key=lambda c: c['id'], reverse=True)):
        output.add_row((ix+1, c['id'], c['name']))

    print(output)

