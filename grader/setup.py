from setuptools import setup, find_packages

setup(name="grader",
      # http://semver.org/spec/v2.0.0.html
      version="0.0.1",
      url='https://github.com/brhoades/grader',
      description="A grading framework for evaluating programming assignments",
      packages=find_packages('src'),
      package_dir={'': 'src'},
      install_requires=[
          'setuptools',
          'GitPython==1.0.1',
          'docker-py==1.6.0',
      ],
      entry_points={
        'console_scripts': ['grader = grader:run'],
        },
      )
