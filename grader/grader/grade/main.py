'''Basic logic for running the assignment grading.
'''
import mimetypes
import os
import re
import gzip

from grader.utils.utils import make_gzip


def grade(args, cli):
    cleanup = []

    if not os.path.isdir(args.folder):
        print("Must provide a valid folder of assignments")
        return

    if args.extra is not None and not os.path.isfile(args.extra):
        print("Extra argument must be a valid file.")
        return
    elif args.extra is not None:
        # if it's not a gzipped tarball, make it one
        if os.path.isdir(args.extra) or \
           mimetypes.guess_type(args.extra)[1] != 'gzip':
            print("Creating temporary gzip file for extra")
            args.extra = make_gzip(args.extra)
            cleanup.append(args.extra)

    # Scrape the top level files and folders
    (dirpath, dirnames, filenames) = next(os.walk(args.folder))
    dirnames = map(lambda x: os.path.join(dirpath, x), dirnames)
    filenames = map(lambda x: os.path.join(dirpath, x), filenames)

    targets = list(dirnames)+list(filenames)

    # Create a container for a file/folder
    for f in targets:
        if os.path.isdir(f):
            # cleanup name
            name = re.sub(r'_submit$', '', os.path.basename(f))
            cleanup.append(make_gzip(f, name))
            f = cleanup[-1]
        id = create_container(cli, dirpath, f, args.image,
                              args.extra, args.force)
        if id is not None:
            run_grader(cli, id)

    print("Cleaning up temporary files")
    for f in cleanup:
        os.remove(f)


def create_container(cli, folder, file, image, extra=None, force=False):
    """
    Pass in a docker connection, a the folder source name (ie HW8), a filename
    (can be a folder name, supports stripping _submit), and a imagefile name.
    """
    user = os.path.basename(file)
    # Strip extension or filetype, if any
    user = re.sub(r'(_submit|\.[^\/]+)$', '', user)

    print("{0}:".format(user))
    # Get the name from the target folder (ie HW8) + username
    name = "{0}_{1}".format(os.path.basename(folder), user)

    # Check if container exists
    containers = cli.containers(all=True)
    for c in containers:
        for container_name in c['Names']:
            if container_name[1:] == name:  # prefixed with /?
                # Try not to clobber images that aren't this
                if c['Image'] != image:
                    if not force:
                        print(("  Container already exists for \"{0}\" and it "
                               "doesn't appear to match the provided image. "
                               "Skipping assignment").format(name))
                        return None
                    else:
                        print("  Forcing removal of "
                              "old container \"{0}\"".format(name))
                else:
                    print("  Removing old container")

                try:
                    cli.remove_container(c['Id'], force=True)
                except Exception as e:
                    print("  Failed to remove: \"{0}\".\n "
                          " Skipping assignment.".format(str(e)))
                    return None
                break

    hostconf = cli.create_host_config(mem_limit='64m')
    # Create container
    id = cli.create_container(image=image, host_config=hostconf,
                              network_disabled=False, name=name, detach=True,
                              stdin_open=True, command="/bin/bash")
    # Copy provided file
    print("  Extracting assignment")
    with gzip.open(os.path.abspath(file)) as g:
        cli.put_archive(container=id, path="/home/grader/", data=g.read())

    # Copy extra file
    if extra is not None:
        print("  Extracting extra file")
        with gzip.open(os.path.abspath(extra)) as g:
            cli.put_archive(container=id, path="/home/grader/", data=g.read())
    cli.start(container=id)
    # Rechown /home/grader after copying stuff over
    cli.exec_start(exec_id=cli.exec_create(
        cmd="chown grader.grader /home/grader", container=id, user="root")
    )
    print("  Container created")

    return id


def run_grader(cli, id):
    """
    Delegates away to the run.py on /home/ in the container.
    """
    cli.start(container=id)
    info = cli.exec_create(container=id, stdout=True, stderr=True,
                           cmd="python3 /home/grader/grader/run.py",
                           user="grader", tty=True)
    print("  Running suite")
    ret = cli.exec_start(info['Id']).decode('utf-8')
    if re.match(r'^Traceback', ret):
        print("  Payload failed to run: ")
        for l in ret.split('\r\n'):
            print("    {0}".format(l))
