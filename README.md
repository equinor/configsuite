# Config Suite #

[![Build Status](https://travis-ci.org/equinor/configsuite.svg?branch=master)](https://travis-ci.org/equinor/configsuite)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)
[![MIT license](http://img.shields.io/badge/license-MIT-brightgreen.svg)](http://opensource.org/licenses/MIT)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/042d23ea22084a1c8c7396edc6d1709f)](https://www.codacy.com/app/markusdregi/configsuite?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=equinor/configsuite&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/042d23ea22084a1c8c7396edc6d1709f)](https://www.codacy.com/app/markusdregi/configsuite?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=equinor/configsuite&amp;utm_campaign=Badge_Coverage)
[![Requirements Status](https://requires.io/github/equinor/configsuite/requirements.svg?branch=master)](https://requires.io/github/equinor/configsuite/requirements/?branch=master)
[![Documentation Status](https://readthedocs.org/projects/configsuite/badge/?version=latest)](https://configsuite.readthedocs.io/en/latest/?badge=latest)

## Introduction ##
_Config Suite_ is the result of recognizing the complexity of software configuration, both from a user and developer perspective. And our main goal is to be transparent about this complexity. In particular we aim at providing the user with confirmation when a valid configuration is given, concrete assistance when the configuration is not valid and up-to-date documentation to assist in this work. For a developer we aim at providing a suite that will handle configuration validity with multiple sources of data in a seamless manner, completely remove the burden of special casing and validity checking and automatically generate documentation that is up to date. We also believe that dealing with the complexity of formally verifying a configuration early in development leads to a better design of your configuration.

## Features ##
-   Validate configurations.
-   Provide an extensive list of errors when applicable.
-   Output a single immutable configuration object where all values are provided.
-   Support for multiple data sources, yielding the possibility of default values as well as user and workspace configurations on top of the current configuration.
-   Generating documentation that adheres to the technical requirements.
-   No exceptions are thrown based on user-input (this is currently not true for validatiors).
-   Context based validators and transformations.

## Documentation ##
Check out the [documentation](https://configsuite.readthedocs.io/en/latest).

## Future ##
Have a look at the epics and issues in the _GitHub_ [repository](https://github.com/equinor/configsuite/issues).

## Installation ##
The simplest way to fetch the newest version of _Config Suite_ is via [PyPI](https://pypi.python.org/pypi/configsuite/).

`pip install configsuite`

## Developer guidelines ##
Contributions to _Config Suite_ is very much welcome! Bug reports, feature requests and improvements to the documentation or code alike. However, if you are planning a bigger chunk of work or to introduce a concept, initiating a discussion in an issue is encouraged.

### Running the tests ###
The tests can be executed with `python setup.py test`. Note that the code formatting tests will only be executed with Python `3.6` or higher.

### Code formatting ###
The entire code base is formatted with [black](https://black.readthedocs.io/en/stable/).

### Pull request expectations ###
We expect a well-written explanation for smaller PR's and a reference to an issue for larger contributions. In addition, we expect the tests to pass on all commits and the commit messages to be written in imperative style. For more on commit messages read [this](https://chris.beams.io/posts/git-commit/).

## License ##
_Config Suite_ is licensed under the MIT License. For more information we refer
the reader to the [LICENSE file](https://github.com/equinor/configsuite/blob/master/LICENSE).
