''' TODO: New package docs
'''

from grader.new.create import create_assignment

help = 'Create a new assignment'
default_shell_repo = 'git://'


def setup_parser(parser):
    parser.add_argument('name', help='Assignment name')
    parser.add_argument('repo', nargs='?', default=default_shell_repo,
                        help='Payload repo')
    parser.set_defaults(run=run)


def run(args):
    create_assignment(args.name, args.path, repo=args.repo)
