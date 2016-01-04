Models
======

Grader consists of several classes that represent different apsects of
the grader. Namely:

* :class:`grader.models.Grader` - The whole shebang. This object has
  members that allow for all kinds of high-level assignment
  manipulation: creation, grading, etc. The grader can be configured
  with a YAML file (which is represented with a
  :class:`grader.models.GraderConfig`)
* :class:`grader.models.Assignment` - A single assignment
* :class:`grader.models.GradeSheet` - A grade sheet for a single
  assignment. Grade sheets describe how an assignment should be
  graded, which includes:
    * Grading scripts
    * A Dockerfile for building the execution environment
    * Assignment-specific configuration (via
      :class:`grader.models.AssignmentConfig`) for running and
      evaluating submitted assignments.


Grader
------

.. autoclass:: grader.models.Grader
   :members:


Assignment
----------

.. autoclass:: grader.models.Assignment
   :members:


GradeSheet
----------

.. autoclass:: grader.models.GradeSheet
   :members:


GraderConfig
------------

.. autoclass:: grader.models.GraderConfig




AssignmentConfig
----------------

.. autoclass:: grader.models.AssignmentConfig
