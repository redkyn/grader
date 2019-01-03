<img src="docs/grader.png" alt="Grader"/>

[![PyPi](https://badge.fury.io/py/redkyn-grader.svg)](https://badge.fury.io/py/redkyn-grader)
[![Build Status](https://travis-ci.org/redkyn/grader.svg?branch=master)](https://travis-ci.org/redkyn/grader)

This program uses Docker and Python to easily grade many assignments in an encapsulated, safe manner. The general process starts by creating an image for a class or an assignment. That image can be given a payload, a protected grading script, which has a grading hooks. The grade module, when ran, creates an individual container for each student's assignment and runs a payload hook. The payload then returns a JSON response with stdin, stdout, and additional response information depending on the image ran.

Getting Started
---------------

See [the tutorial](TUTORIAL.md) for an idea of how to get started using `grader`.

Setup
-----

This project is setup using [buildout](http://www.buildout.org/en/latest/). It's super easy to get `grader` up and running:

You'll probably need the following libraries...

- build-essential
- libncurses-dev
- python3-dev

And, of course, you'll want Docker if you plan to do anything interesting at all. Grader requires docker with **API version >= 1.20**. We use `put_archive` (`PUT /containers/(id)/archive`) from docker-py.

```shell
# Bootstrap buildout
python3 bin/bootstrap-buildout.py

# Setup your development environment with buildout
bin/buildout
```

Now you're done! When it sets up your environment, buildout creates a couple of executables and places them in `bin/` for you. They are:

- **buildout** : That's buildout. Run it whenever you add eggs to `grader/setup.py` or modify `buildout.cfg`
- **grader** : That's `grader`!
- **python** : "What? Another Python!?" Yeah... This is an ipython interpreter. It's handy because it has access to all the same packages that were installed for `grader`.

Check your style
----------------

It's important to keep our code looking consistent. There's a tool installed by buildout called `flake8` that will check your Python source for issues in style. Simply run it like this:

```shell
  # Make sure you run this in your grader directory. flake8 will recursively check source files for style issues.
  bin/flake8 grader/
```
