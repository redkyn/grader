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
submission files which need modification.

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

.. _remove::

``remove``
---------
Remove submission Docker containers for an assignment, using an optional filter by student ids

Usage
*****

.. code-block:: bash

  grader remove [--negate] assignment [student_id student_id2 ...]

Grader remove allows the removal of all submission's Docker containers per assignment. It
optionally allows selecting specific student ids submissions for removal if desired.
Containers to be removed are listed, confirmed, and then stopped before removal.

args:
  --negate: instead of the student ids provided being removed, they are
            explicitly excluded from removal.


Examples
********

.. code-block:: bash

   $ grader remove hw1
   INFO     Containers to delete:
   INFO       bjrq48 (1 container(s)):
   INFO         1661d79d7a88cd6c47268bbc45fcd021d45b450276261b3fa3b19cf83580e73f created on 2017-02-25 21:01:58
   INFO       nmjxc9 (1 container(s)):
   INFO         5a75dc16334a393d9ac6cc70980c7a53599aa73db2f8766affa290151748116b created on 2017-02-25 21:02:01
   INFO       mwcp2 (1 container(s)):
   INFO         ba4e4a891f69023359d312149629f05cf1f36a63694cb77a31c3f23514974469 created on 2017-02-25 21:02:06
   Are you sure you wish to remove the containers listed above [yes/no] (no): yes
   INFO     Removing container 1661d79d7a88cd6c47268bbc45fcd021d45b450276261b3fa3b19cf83580e73f
   INFO     Removing container 5a75dc16334a393d9ac6cc70980c7a53599aa73db2f8766affa290151748116b
   INFO     Removing container ba4e4a891f69023359d312149629f05cf1f36a63694cb77a31c3f23514974469

.. code-block:: bash

   $ grader remove hw1 bjrq48
   INFO     Containers to delete:
   INFO       bjrq48 (1 container(s)):
   INFO         1661d79d7a88cd6c47268bbc45fcd021d45b450276261b3fa3b19cf83580e73f created on 2017-02-25 21:01:58
   Are you sure you wish to remove the containers listed above [yes/no] (no): yes
   INFO     Removing container 1661d79d7a88cd6c47268bbc45fcd021d45b450276261b3fa3b19cf83580e73f

.. code-block:: bash

   $ grader remove --negate hw1 bjrq48
   INFO     Containers to delete:
   INFO       nmjxc9 (1 container(s)):
   INFO         5a75dc16334a393d9ac6cc70980c7a53599aa73db2f8766affa290151748116b created on 2017-02-25 21:02:01
   INFO       mwcp2 (1 container(s)):
   INFO         ba4e4a891f69023359d312149629f05cf1f36a63694cb77a31c3f23514974469 created on 2017-02-25 21:02:06
   Are you sure you wish to remove the containers listed above [yes/no] (no): yes
   INFO     Removing container 5a75dc16334a393d9ac6cc70980c7a53599aa73db2f8766affa290151748116b
   INFO     Removing container ba4e4a891f69023359d312149629f05cf1f36a63694cb77a31c3f23514974469
