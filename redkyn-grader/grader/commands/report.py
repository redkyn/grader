'''TODO: Report command docs
'''
import itertools
import jinja2
import logging
import os
import yaml

from grader.models import Grader
from grader.utils.config import require_grader_config

logger = logging.getLogger(__name__)

help = "Generate reports using a gradesheet template"


def setup_parser(parser):
    parser.add_argument('--template', type=str, default="markdown",
                        help='Type of template to use')
    parser.add_argument('assignment',
                        help='Name of the assignment.')
    parser.add_argument('student_id', nargs='?',
                        help='ID of student to generate report for.')
    parser.set_defaults(run=run)


def load_data(user_id, content):
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError:
        logger.info(
            "Couldn't parse YAML for {}."
            " Passing to template as 'data'".format(user_id)
        )
        return {'data': content}


@require_grader_config
def run(args):
    g = Grader(args.path)
    a = g.get_assignment(args.assignment)

    if not a.gradesheet.templates:
        logger.critical("No available templates in gradesheet.")
        return

    # Find and load the Jinja2 template
    template = None
    try:
        with open(a.gradesheet.templates[args.template]) as template_file:
            template = jinja2.Template(template_file.read())
    except KeyError:
        logger.error("Couldn't find '%s' template", args.template)
        return

    # Narrow down users, if necessary
    users = a.submissions_by_user
    if args.student_id:
        try:
            users = {args.student_id: users[args.student_id]}
        except KeyError:
            logger.error("Cannot find student %s", args.student_id)
            return

    # Make a unique directory for the output
    output_dir = os.path.join(args.path, args.template)
    for i in itertools.count(1):
        if os.path.exists(output_dir):
            template_name = "{}.{}".format(args.template, i)
            output_dir = os.path.join(args.path, template_name)
        else:
            os.makedirs(output_dir)
            break

    # Generate reports
    for user_id, submissions in users.items():
        logger.info("Generating report for %s", user_id)
        for submission in submissions:
            # Load the report data
            with open(submission.latest_result) as result_file:
                data = load_data(user_id, result_file.read())
                data.update({
                    'student': {
                        'id': user_id,
                        'name': submission.student_name
                    },
                    'assignment': {
                        'name': submission.assignment.name
                    }
                })

            # Save it to a file
            filename = "{}.{}".format(submission.full_id, args.template)
            with open(os.path.join(output_dir, filename), 'w') as outfile:
                outfile.write(template.render(data))
