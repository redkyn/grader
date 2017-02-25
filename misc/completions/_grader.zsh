# You must set GRADER_HOME in you zshrc for this to work

_grader_completion() {
  if [[ -z "$GRADER_HOME" ]] || [[ ! -d "$GRADER_HOME" ]]; then
    echo "GRADER_HOME is not set"
    return
  fi

  ##### Get all assignments ####
  local -a assignments
  assignments=( $GRADER_HOME/assignments/* )
  # Now trim everything except for the folder names.
  assignments=$(printf "%s\n" "${assignments[@]}" | xargs -i echo "{}" | rev | cut -d'/' -f-1 | rev)
  ##############################

  #### Get all students ####
  local -a students

  # Extract students from roster:
  students=( $(cat "$GRADER_HOME/grader.yml" | grep -P --color=never "\s+\-?\s*id:" | sed -e 's/\s*\-\?\s*id:\s*\([A-Za-z0-9_]\+\)$/\1/g') )
  ##########################

  _arguments -C -A "-h" -A "--path" -A "--tracebacks" -A "--verbosity" \
             '(- 1 *)-h[display grader help and exit]' \
             "(- 1 *)--path[specify grader's root manually]" \
             '(- 1 *)--tracebacks[show grader tracebacks when there is an error]' \
             '(- 1 *)--verbosity[configure how verbose output is {DEBUG,INFO,WARNING,ERROR}]' \
             '1: :->cmds' \
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
          # TODO: submission_Id requires 1 and 2 to look up, so I'm not sure zsh can complete that.
          # best thing may be a list of all submissions... but that is nontrivial and would incur

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
