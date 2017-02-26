_grader_completion() {
  if [[ -z "$GRADER_HOME" ]] || [[ ! -d "$GRADER_HOME" ]] || [[ ! -e "$GRADER_HOME/config.yml" ]]; then
    local -x GRADER_HOME=""

    # Guess GRADER_HOME if it's not set.
    if [[ -e "$(pwd)/grader.yml" ]]; then
      GRADER_HOME=`pwd`
    elif [[ ! -z "$(which grader)" ]]; then
      GRADER_HOME="$(which grader | rev | cut -d'/' -f3- | rev)"
    fi
  fi

  if [[ ! -e "$GRADER_HOME/grader.yml" ]]; then
    return
  fi
  ##### Get all assignments ####
  local -a assignments
  assignments=( $GRADER_HOME/assignments/* )
  # Now trim everything except for the folder names.
  assignments=( $( echo "$GRADER_HOME/assignments"/* | xargs -i -d' ' sh -c "echo -e \"{}\" | rev | cut -d'/' -f-1 | rev") )
  ##############################

  #### Get all students ####
  local -a students

  # Extract students from roster:
  students=( $(cat "$GRADER_HOME/grader.yml" | grep -P --color=never "\s+\-?\s*id:" | sed -e 's/\s*\-\?\s*id:\s*\([A-Za-z0-9_]\+\)$/\1/g') )
  ##########################

  local -a verbosity
  verbosity=( "DEBUG" "INFO" "WARNING" "ERROR" )

  _arguments \
             "(- 1 *)-h[display grader help and exit]" \
             "(- 1 *)--help[display grader help and exit]" \
             "--path[specify grader's root manually]: :" \
             "--tracebacks[show grader tracebacks when there is an error]" \
             "--verbosity[configure how verbose output]: :{_describe 'verbosity level' verbosity}" \
             "1: :->cmds" \
             '*:: :->args' && ret=0

  case $state in
    cmds)
      _values "grader command" \
              "init[initialize grader by creating grader.yml]" \
              "new[Create a new assignment]" \
              "build[Build an assignment's docker image]" \
              "import[Import student submission(s)]" \
              "list[List student submission(s)]" \
              "grade[Grade student submission(s)]" \
              "cat[Print an assignment's grade output to STDOUT]" \
              "report[Generate reports using a gradesheet template]" \
              "inspect[Inspect a graded submission's container]" \
              "help[Show help for grader and exit]"
      ret=0
      ;;
    args)

      # Trim assignment list to just have assignment names
      case $line[1] in
        init)
          _arguments \
            '--help[View help for init and exit]' \
            '--force[Overwrite an existing grader.yml]' \
            '--course-id[Unique course ID (for docker)]'
          ret=0
          ;;
        build)
          _arguments \
            '--help[View help for build and exit]' \
            "1: :{_describe 'assignments' assignments}"

          ret=0
          ;;
        import)
          local -a _kinds
          _kinds=("blackboard" "multiple" "single" "repo")

          _arguments \
            '--help[View help for import and exit]' \
            "--kind: :{_describe 'kind of import' _kinds}" \
            "1: :{_describe 'assignments' assignments}" \
            "2: *:_files"

          ret=0
          ;;
        list)
          local -a _sortby
          _sortby=("time" "name")

          _arguments \
            '--help[View help for list and exit]' \
            "--submissions[Show submissions for each assignment]" \
            "--full[Show full length of values]" \
            "--sortby[Sort by a specific field]: :{_describe 'sort import by' _sortby}" \
            "1: :{_describe 'assignments' assignments}"

          ret=0
          ;;
        grade)
          _arguments \
            '--help[View help for grade and exit]' \
            '--rebuild[Rebuild cointainers (if they exist)]' \
            "--suppress_output[Don't display output]" \
            "1: :{_describe 'assignments' assignments}" \
            "2: :{_describe 'students' students }"

          ret=0
          ;;
        cat)
          local -a _submissions
          _submissions=()
          # FUTURE: Ideally, this would only grab submissions from the assignment/student you specified...
          # http://stackoverflow.com/a/23357277/7065175
          while IFS=  read -r -d $'\0'; do
            # Trim to just the submission ID alone.
            _submissions+=($(echo "$REPLY" | rev | cut -d'/' -f-1 | rev))
          done < <(find "$GRADER_HOME/assignments/" -wholename '*/*{*}' -print0)

          _arguments \
            '--help[View help for cat and exit]' \
            "--submission_id[ID of a specific submission to cat]: :{_describe 'ALL submissions' _submissions}" \
            "1: :{_describe 'assignments' assignments}" \
            "2: :{_describe 'students' students }"

          ret=0
          ;;
        inspect)
          _arguments \
            '--help[View help for inspect and exit]' \
            "--user[username of a specific container user to inspect as]: :" \
            "1: :{_describe 'assignments' assignments}" \
            "2: :{_describe 'students' students }"

          ret=0
          ;;
        report)
          _arguments \
            '--help[View help for report and exit]' \
            '--template[Type of template to use]:' \
            "1: :{_describe 'assignments' assignments}" \
            "::OPTIONAL :{_describe 'students' students }"
          ret=0
          ;;
      esac
      ;;
  esac

  return ret
}

compdef _grader_completion grader
