# Grader
This program uses Docker and Python to easily grade many assignments in an encapsulated, safe manner. The general process starts by creating an image for a class or an assignment. That image can be given a payload, a protected grading script, which has a grading hooks. The grade module, when ran, creates an individual container for each student's assignment and runs a payload hook. The payload then returns a JSON response with stdin, stdout, and additional response information depending on the image ran.

## Setup

This project is setup using [buildout](http://www.buildout.org/en/latest/). It's super easy to get `grader` up and running:

```shell
# Bootstrap buildout
python3 bin/bootstrap-buildout.py

# Setup your development environment with buildout
bin/buildout
```

Now you're done! When it sets up your environment, buildout creates a couple of executables and places them in `bin/` for you. They are:

* **buildout** : That's buildout. Run it whenever you add eggs to `grader/setup.py` or modify `buildout.cfg`
* **grader** : That's `grader`!
* **python** : "What? Another Python!?" Yeah... This is an ipython interpreter. It's handy because it has access to all the same packages that were installed for `grader`.
