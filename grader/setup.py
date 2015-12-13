from setuptools import setup

setup(
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
    ],
    entry_points={
        'console_scripts': ['grader = grader:run'],
    },
)
