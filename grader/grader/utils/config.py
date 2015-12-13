import functools
import logging
import os
import sys


def is_grader_dir(path):
    return os.path.exists(os.path.join(path, "grader.yml"))


def require_grader_config(wrapped):
    """Wrap a function, so that it calls exit(1) if there's no grader.yml

    The first parameter of the function **must** be a populated
    argparse Namespace with a "path" field.
    """
    @functools.wraps(wrapped)
    def wrapper(parsed_args, *args, **kwargs):
        # Check whether we're in a valid path
        if not is_grader_dir(parsed_args.path):
            # TODO implement "grader config" command to set values in
            # the config.
            logging.critical("{} has no grader.yml. Run "
                             "'grader init' first.".format(parsed_args.path))
            sys.exit(1)
        return wrapped(parsed_args, *args, **kwargs)
    return wrapper
