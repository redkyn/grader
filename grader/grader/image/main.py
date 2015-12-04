# Houses logic and functionality for creating images with payloads
import os
import sys

# Custom libraries
from grader.lib.utils import get_folder

def run(target, no_cache=False):
    f = get_folder(target)
    print(f)
