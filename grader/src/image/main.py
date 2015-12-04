# Houses logic and functionality for creating images with payloads
import os
import sys

# Custom libraries
sys.path.append("..")
from lib.utils import get_folder

def run(target, no_cache=False):
    f = get_folder(target)
    print(f)

