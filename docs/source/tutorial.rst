Tutorial
========

Setup
-----

Depending on your distribution, you will need the following packages:
  * python3-dev
  * libcurses-dev
  * python3-dev
  * git

And, of course, you'll want Docker if you plan to do anything interesting at all. Grader requires docker with **API version >= 1.20**. We use put_archive (PUT /containers/(id)/archive) from docker-py.

Grab the repository and run buildout to set up your local grader install:

.. code-block:: bash

  git clone https://github.com/grade-it/grader.git
  cd grader

  # Bootstrap buildout
  python3 bin/bootstrap-buildout.py

  # Setup your development environment with buildout... this can take a bit.
  bin/buildout

  # Add to path
  export PATH=$PATH:$(pwd)/bin 

You now have a functioning grader installation. Change to your desired working directory before continuing.

Preparing Working Directory
---------------------------

In your working directory, begin by creating an assignments folder with :ref:`init`. You must specify
a course name.

.. code-block:: bash

  grader init course-name

This creates a template grader.yml file which contains a course name and a unique course UUID. Now, 
create an assignment using :ref:`new`. You should pass it a :ref:`gradesheet`, an example gradesheet is 
used below.

.. code-block:: bash
  
  grader new hw1 https://github.com/grade-it/python-gradesheet.git

Which should yield::

  INFO     Creating assignment directory.
  INFO     Successfully cloned https://github.com/grade-it/python-gradesheet.git
  INFO     Created 'hw1'.

This creates an assignments folder with your specified homework::

  .
  ├── assignments
  │   └── hw1
  │       ├── gradesheet
  │       │   ├── assignment.yml
  │       │   ├── Dockerfile
  │       │   ├── README.md
  │       │   └── scripts
  │       │       └── grade-it
  │       ├── results
  │       └── submissions
  └── grader.yml

You should now add students to your roster in grader.yml. Every assignment imported must have a matching id
(think: username) within your config. Here is an example::

  course-id: 80efce90-cb8b-460f-9f4b-fbfde0f4ec48
  course-name: '5201'
  roster:
    - id: admb23
      name: Admiral Akbar
    - id: bjrdo4
      name: Billy Rhoades
    - id: mww4t6
      name: Mike Wisely

Using Grader
------------

Start by building your new docker image, this is done by simply running :ref:`build`.

.. code-block:: bash

  grader build hw1

Next, you should :ref:`import` your assignments. There are :ref:`many ways to do this <import>`, in this example, a directory with *multiple* tarballs is imported.

.. code-block:: bash

  grader import --kind multiple hw1 /tmp/packed

Which yields::

  INFO     Imported Submission mww4t6 (350f2bd0-c36e-48ec-9af4-17a99f6665e4)
  INFO     Imported Submission bjrdo4 (5004487a-8055-43c4-9c4f-8c2b744257b2)
  INFO     Imported Submission admb23 (db83a1b9-6a07-4848-bb76-7d1a810a56af)

These assignments have now been imported into your working directory.

Now you can run your gradesheet with :ref:`grade`.

.. code-block:: bash

  grader grade hw1

