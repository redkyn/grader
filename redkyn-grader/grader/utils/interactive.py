
def submission_choice(assignment, user_id, subs):
    """
    If a student has multiple submissions, interactively prompt
    the user to choose one
    """

    # If they have multiple submissions, make them choose
    if len(subs) > 1:
        print("{0} submissions found for {1}, choose one:\n"
              .format(len(subs), user_id))
        i = 1
        print("Index\tCreated")
        for s in subs:
            info = assignment.docker_cli.inspect_container(s.full_id)
            print("{0}\t{1}".format(i, info['Created']))
            i += 1
        choice = -1
        while choice < 0 or choice >= len(subs):
            choice = input("Please enter your selection: ")
            try:
                choice = int(choice)-1
            except TypeError:
                pass

        return subs[choice]
    else:
        return subs[0]

def make_help_parser(parser, subparsers, help_text):
    def show_help(args):
        new_args = list(args.command)
        new_args.append("--help")
        parser.parse_args(new_args)

    help_parser = subparsers.add_parser("help", help=help_text)
    help_parser.add_argument("command", nargs="*",
                             help="Command to get help with")
    help_parser.set_defaults(run=show_help)
