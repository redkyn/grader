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
        'GitPython>=2.1.8',
        'docker>=3.6.0',
        'PyYAML>=3.13',
        'jsonschema>=2.5.1',
        'PTable==0.9.2',
        'colorlog>=2.6,<3',
        'Jinja2>=2.10',
        'assigner>=1.1,<2'
    ],
    entry_points={
        'console_scripts': ['grader = grader:run'],
    },
)
