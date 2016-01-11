from setuptools import setup  # pragma: no cover

setup(  # pragma: no cover
    name="grader",
    version="0.0.1",  # http://semver.org/spec/v2.0.0.html
    url='https://github.com/brhoades/grader',
    description="A grading framework for evaluating programming assignments",
    packages=['grader'],
    package_dir={'grader': 'grader'},
    install_requires=[
        'setuptools',
        'GitPython==1.0.1',
        'docker-py==1.6.0',
        'PyYAML==3.11',
        'jsonschema==2.5.1',
        'prettytable==0.7.2',
        'colorlog',
    ],
    entry_points={
        'console_scripts': ['grader = grader:run'],
    },
)
