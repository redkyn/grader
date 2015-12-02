# This is the base grader file for the C++ docker instance. It does stuff.
import os

def grade():
    print("Hello world")

    with open("dongers", 'a'):
        os.utime("dongers")
