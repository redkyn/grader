import tempfile
import tarfile
import os

def make_gzip(f, name=None):
    # Make a temporary (named) gzip file somewhere. 
    file = tempfile.NamedTemporaryFile(delete=False)
    file.close()
    fn = file.name

    with tarfile.open(fn, "w:gz") as t:
        t.add(f)

    if name is not None:
        fn = os.path.join(os.path.dirname(fn),name) + ".tar.gz"
        os.rename(file.name, fn)
                
    return fn
