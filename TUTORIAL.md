# Getting started with Grader

## Installation

### The easy way

Use `pip`: `pip3 install redkyn-grader`

You'll also need to have docker installed and be in the `docker` group so you can do dockery things.
Plan to have a lot of free hard drive space -- docker is not exactly frugal with its bytes.

If you use `zsh`, you may want to source the [`zsh` completion script](misc/completions/_grader.zsh) too.

### If you want to hack on Grader

The easiest way to do this is to clone the [grader repository](https://github.com/redkyn/grader.git).
Inside the cloned repository, run `pip3 install --user -e redkyn-grader/`.
This will install a `grader` executable to `~/.local/bin` and make the install "editable" -- this way, changes made in the Grader repository apply anywhere you run Grader.

## Setting up a new class

The first thing you should do when setting Grader up for a course is to create a directory to hold student submissions, gradesheets, and the like.

### Configuring Grader (`grader init`)

In your course directory, run `grader init <course name>`.
This will create a `grader.yml` file in the current directory.

The `grader.yml` file contains some basic metadata about the class as well as the class roster.

### Adding students to the roster

Right now, the only way to do this is to manually edit the `grader.yml` file.
(Canvas import support is coming shortly, though!)

Here is an example of how a roster might look:
```yaml
course-id: bf27b22f-e365-43eb-bd24-1a79f0228b1d
course-name: test
roster:
        - name: Nat
          id: nmjxv3
        - name: Wisely
          id: mwwcp2
```

This is not terribly different from Assigner's configuration; a bit of vim regex usually makes the conversion rather simple.

## Grading an assignment

### Configuring a gradesheet (`grader new`)

You'll want to make a git repository containing a dockerfile and associated grading scripts.
The resulting docker container should have an executable `grade-it` which does the actual grading work.
Grader will call it like so: `grade-it <directory containing student's submission>`.

For a simple example, see [the example Python gradesheet](https://github.com/redkyn/python-gradesheet).
For more complex examples, feel free to contact [Nat](mailto:jarus@mst.edu) or [Wisely](mailto:michael.wisely@mst.edu).

Once you have created your gradesheet, run `grader new <assignment name> <gradesheet git repository>`.
This will set up some metadata in the `assignments/` directory and clone the gradesheet git repository somewhere Grader can access it.

### Importing student assignments (`grader import`)

Grader knows how to import either multiple assignments or single student assignments.
(It claims to know how to import blackboard assignments or assignments from git repos, but that's merely wishful thinking.)

Importing multiple assignments is the most common use of this command.
Say you have a directory of directories, each containing a student's submission.
To import these into Grader, run `grader import --kind=multiple <assignment name> <subissions directory>`.

By default, it attempts to match directory names against student IDs from the roster.
For importing repositories fetched from Assigner, this is fine; for submissions from other sources, the `--pattern` flag can be used to describe the format of the directory name.
The flag takes a regular expression which has a named capture group with the name 'id'.
For example, if your submission directories are named something like `bob123_submit`, you would do something like
`grader import <assignment name> <submissions directory> --kind=multiple --pattern="(?P<id>.*)_submit"`.

Grader makes a copy of imported assignments to later create docker containers from.

### Building student docker containers (`grader build`)

Run `grader build <assignment name>` to create a docker container for each submission.
The initial build will be rather slow, but for later builds, docker can reuse cached containers.

Often, you will find that you need to fix something in your gradesheet.
After doing so, you can run `grader build <assignment name> --pull` to do a `git pull` in the gradesheet git repository and then rebuild submission containers with the updated gradesheet.

If you have trouble with docker caching too aggressively, you can use the `--no-cache` flag to force docker to rebuild submission containers from scratch.

### Grading assignments (`grader grade`)

After submission containers have been built, you can (finally) grade student submissions by running `grader grade <assignment name>`.

Grader will start each submission container, execute the `grade-it` script from your gradesheet, and log the output from that script in a file in the `assignments/` directory.

To grade a single student's submission, run `grader grade <assignment name> <student id>`.

### Reviewing graded assignments (`grader report` or `grader review`)

You can use `grader report` to generate nice PDF reports from the `grader grade` logs.
(Unfortunately, that is about all I know about this feature.)

You can interactively look at each submission one after another with `grader review`.
By default, it opens a vim session with two vertical panes, one containing the submission files and the other containing the grader log.
(This command can be configured [via a setting in `grader.yml`](https://github.com/redkyn/grader/blob/master/grader/grader/commands/review.py#L48-L49).)

Upon quitting the vim session, it displays the following menu:

```
Finished grading <student id>, <n> more remain.
<student id> is next.

C|N)   Continue (default)
H|P)   Previous
R)     Review current student's submission
I)     Inspect current student's assignment container
G)     Grade current student's submission
U)     User
Q)     Quit
```

- `C`, `N`, `L`, or just hitting `Ret` will advance to the next student's submission.
- `H` or `P` will rewind to the previous student's submission.
- `R` will take you back to reviewing the submission you were just looking at.
- `I` will drop you into a shell in the current submission's container, allowing you to run commands and edit the student's submission (perhaps to get it to compile so your tests will run).
- `G` will re-run `grader grade` on the current submission.
- `U` will show a menu of student ids, allowing you to jump to a specific student in the list.
- `Q` exits the review loop.

### Inspecting student submissions (`grader inspect`)

If you need to poke around inside a submission container, run `grader inspect <assignment name> <student id>`.
This will start the container and drop you into a shell running in it.

## Helpful docker knowledge

It would be really nice to document how to clean up the docker cache and various docker images as they can easily take up a lot of space.
