import tempfile
import tarfile
import os
import re
from git import Repo
from subprocess import Popen, PIPE
from grader.lib.commandresult import CommandResult
import logging

def make_gzip(f, name=None):
    # Make a temporary (named) gzip file somewhere. 
    file = tempfile.NamedTemporaryFile(delete=False)
    file.close()
    fn = file.name

    with tarfile.open(fn, "w:gz") as t:
        t.add(f, recursive=True, arcname='')


    if name is not None:
        fn = os.path.join(os.path.dirname(fn),name) + ".tar.gz"
        os.rename(file.name, fn)

    return fn

def get_folder(source, **args):
    """
    Determines source and makes it a local folder on /tmp.
    Accepts: git repos (/\.git$/ ssh or https)
             folders
             tarballs (will extract)
             cifs share (//user(:pass)@host)
             ssh folder (anything that's not ^ and has user@host:/dir

    """
    folder = tempfile.mkdtemp(args.get('name', None))

    if os.path.exists(source):
        if not os.path.isdir(source):
            e = re.search(r'(gz|tar|bz2)+$', source).groups()
            if len(e) > 0:
                print("Extracting archive")
                type = ""
                if e[0] == "gz" or e[0] == "bz2":
                    # Automatically handles tars that are gzipped/bzipped
                    if not re.search(r'tar\.(gz|bz2)$', source):
                        type = e[0]
                with tarfile.open(source, "r:{0}".format(type)) as t:
                    t.extractall(folder)
            else:
                print("Unknown archive type \"{0}\"".format(source))
                return source
        else:
            return source
    elif re.search(r'\.git$', source):
        print("Cloning repository")
        repo = Repo.init(folder)
        origin = repo.create_remote('origin', source)
        origin.fetch()
        origin.pull(origin.refs[0].remote_head)
    elif re.search(r'^[\\\/]{2}', source):
        print("Copying from CIFS share")
        # :< this is hard
    else:
        print("Copying from ssh")
        r = os.system("scp -rq \"{0}\" \"{1}\"".format(source, folder))
        if r:
            print("  Error when copying (got code {0})".format(r))
    
    return folder

def get_logger(payload_dir, module_name, level=logging.INFO):
    filename = os.path.abspath(os.path.join(payload_dir, 'logs', 
        "{0}.log".format(module_name)))
    if not os.path.isdir(os.path.dirname(filename)):
        os.mkdir(os.path.dirname(filename))
    logging.basicConfig(filename=filename, level=level)
    return logging.getLogger(module_name)

def run_command(dir, command, log, file_diff=True, **kwargs):
    """
    Runs a command, command, and logs it to log if provided.

    Outputs what files changed if file_diff is True.

    Returns a CommandResult with appropriate details.
    """
    log = log.getChild('runcommand')
    file_diff = kwargs.get("file_diff", True)
    name = kwargs.get("name", "\"{0}\"".format(command))

    log.info("{0}BEGIN{0}".format('='*20))

    # Files before running
    (_, dirs, files) = next(os.walk(os.path.abspath(dir)))
    dirs.extend(files)
    combined_old = dirs

    # Run it
    log.info("Running: {0}".format(command))
    p = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, 
            close_fds=True)
    (stdout, stderr) = map(lambda x: x.decode("UTF-8"), p.communicate())

    # Complain if it's nonzero
    if p.returncode != 0:
        log.error("Command returned nonzero code {0}".format(p.returncode))

    log.info("{0}STDOUT{0}".format('='*20))
    for line in stdout.split('\n'):
        log.info(line)
    log.info("{0}STDERR{0}".format('='*20))
    for line in stderr.split('\n'):
        log.info(line)

    # Files after running
    (_, dirs, files) = next(os.walk(os.path.abspath(dir)))
    dirs.extend(files)
    combined = dirs

    new = [x for x in combined if x not in combined_old]
    missing = [x for x in combined_old if x not in combined]

    # print out file changes
    if file_diff:
        log.info("{0}New Files{0}".format('='*20))
        for line in new:
            log.info(line)
        log.info("{0}Missing Files{0}".format('='*20))
        for line in missing:
            log.info(line)

    log.info("{0} END {0}".format('='*20))

    return CommandResult(p, stdout, stderr, new, missing)

