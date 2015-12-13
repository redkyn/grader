import yaml


def setup(config_path, course_name, course_id):
    header = "# grader configuration for {}\n\n".format(course_name)

    # Setup the configuration
    config = {
        "course-id": course_id,
        "course-name": course_name,
    }

    with open(config_path, 'w') as config_file:
        config_file.write(header)
        config_file.write(yaml.dump(config, default_flow_style=False))
