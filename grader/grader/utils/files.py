import os
import tarfile
import tempfile


def make_tarball(source, tar_basename, extension=".tar.gz", compression="gz"):
    """Create a tarball from a source directory, and store it in a
    temporary directory.

    :param str source: The directory (or file... whatever) that we're
        compressing into a tarball. The source will be added
        recursively.

    :param str tar_basename: The basename to use for the tarball. If
        you want the tarball to be named ``hsimpson.tar.gz``, then
        ``tar_basename`` should be ``hsimpson``.

    :param str extension: The extension to use for the tarball.

    :param str compression: The compression algorithm to use to
        compress the tar.

    :return: A tuple: (Path to the tarball, temp directory that
        contains the tarball)

    :rtype: (str, str)

    """
    source = os.path.normpath(source)
    dest = tempfile.mkdtemp()
    tar_name = "{}{}".format(tar_basename, extension)
    tar_path = os.path.join(dest, tar_name)
    mode = "w:{}".format(compression or "")

    with tarfile.open(tar_path, mode) as tar:
        arcname = os.path.basename(source)
        tar.add(source, arcname, recursive=True)

    return (tar_path, dest)
