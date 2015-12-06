import tempfile
import tarfile
import os
import re
from git import Repo


def make_gzip(f, name=None):
    # Make a temporary (named) gzip file somewhere.
    file = tempfile.NamedTemporaryFile(delete=False)
    file.close()
    fn = file.name

    with tarfile.open(fn, "w:gz") as t:
        t.add(f, recursive=True, arcname='')

    if name is not None:
        fn = os.path.join(os.path.dirname(fn), name) + ".tar.gz"
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


def touch(fname, times=None):
    with open(fname, 'a'):
        os.utime(fname, times)


def is_grader_dir(path):
    return os.path.exists(os.path.join(path, "grader.yml"))
