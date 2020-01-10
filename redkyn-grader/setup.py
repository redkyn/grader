from setuptools import setup, find_packages # pragma: no cover
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, '../README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(  # pragma: no cover
    name="redkyn-grader",
    description="A grading framework for evaluating programming assignments",
    long_description=long_description,
    long_description_content_type="text/markdown",

    # Derive version from git tags
    use_scm_version={"root": "..", "relative_to": __file__},

    url='https://github.com/redkyn/grader',

    author='B. Rhoades, N. Jarus, M. Wisely, & T. Morrow',

    author_email='jarus@mst.edu',

    # For a list of valid classifiers, see
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Education',
        'Topic :: Education',
        'Topic :: Software Development :: Version Control :: Git',
        'Environment :: Console',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],

    packages = find_packages(),

    install_requires=[
        'setuptools',
        'GitPython>=2.1.8',
        'docker>=3.6.0',
        'PyYAML>=3.13',
        'jsonschema>=2.5.1',
        'PTable==0.9.2',
        'colorlog>=2.6,<3',
        'Jinja2>=2.10',
        'redkyn-common>=1.0.1'
    ],

    python_requires='>=3.4',
    setup_requires=[
        'setuptools_scm>=1.15',
        'setuptools>=12'
    ],

    data_files=[
        ('share/grader', ['../misc/completions/_grader.zsh'])
    ],

    entry_points={
        'console_scripts': ['grader = grader:run'],
    },
)
