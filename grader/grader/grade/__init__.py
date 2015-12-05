'''TODO: Grade package docs
'''
from grader.grade.main import grade
from docker import Client

help = "Grade assignments"

def setup_parser(parser):
    parser.add_argument('folder', metavar='folder',
                       help='Folder of tarballs or assignment folders.')
    parser.add_argument('--image', default='5201',
        help='Docker image for assignments.')
    #NOTE: This could be done with volumes. Is that better..?
    parser.add_argument('--extra',
        default=None, help='Extra files to copy into container (tarball).')
    parser.add_argument('--force', action='store_true', default=False,
        help='Force removal of conflicting containers even if their image doesn\'t match.')
    parser.set_defaults(run=run)


def run(args):
    # Connect up with docker
    cli = Client(base_url='unix://var/run/docker.sock')

    grade(args, cli)
