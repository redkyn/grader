import os
import tarfile
import tempfile


def make_tarball(source, tar_basename, extension=".tar.gz", compression="gz"):
    dest = tempfile.mkdtemp()
    tar_name = "{}{}".format(tar_basename, extension)
    tar_path = os.path.join(dest, tar_name)
    mode = "w:{}".format(compression or "")

    with tarfile.open(tar_path, mode) as tar:
        tar.add(source, recursive=True)

    return (tar_path, dest)
