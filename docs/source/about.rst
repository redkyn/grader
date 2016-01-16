About Grader
============

This program uses Docker and Python to easily grade many assignments in an encapsulated, safe manner. The general process starts by creating an image for a class or an assignment. That image can be given a payload, a protected grading script, which has a grading hooks. The grade module, when ran, creates an individual container for each student's assignment and runs a payload hook. The payload then returns a JSON response with stdin, stdout, and additional response information depending on the image ran.
