Commands
========

.. _init:

``init``
--------


.. _new:

``new``
-------

.. _build:

``build``
---------

.. _import:

``import``
----------

.. _list:

``list``
--------

.. _grade:

``grade``
---------

.. _inspect:

``inspect``
---------
Inspects a student's submission's docker container by launching an interactive shell
within it. Handles both starting and stopping the container behind the scenes.

Configuration
*************

Gradesheet Configuration Keys:
    shell (*/bin/bash/*): The shell command to run interactively within the submission's container.

Usage
*****

.. code-block:: bash

  grader inspect [--user user] assignment student_id

Grader inspect interactively launches into a specified program on a container.
When the program termiantes, the container is stopped implicitly by Docker.

An optional user can be specified for the process to be launched as. This is particularly
useful when gradesheets restrict the container's default user's access to
submission files that need to be modified.

Examples
********

.. code-block:: bash

  $ grader inspect 1 bjrq48
  INFO Starting container bjrq48--eb86a392-a9f5-464b-a70e-15b9366e8550
  student@9338726 ~ $ echo "Hello!"
  Hello!
  student@9338726 ~ $ exit
  INFO Stopping container bjrq48--eb86a392-a9f5-464b-a70e-15b9366e8550
  $
