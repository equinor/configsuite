Introduction
============

Philosophy
----------

*Config Suite* is the result of recognizing the complexity of software configuration, both from a user and developer perspective. And our main goal is to be transparent about this complexity. In particular we aim at providing the user with confirmation when a valid configuration is given, concrete assistance when the configuration is not valid and up-to-date documentation to assist in this work. For a developer we aim at providing a suite that will handle configuration validity with multiple sources of data in a seamless manner, completely remove the burden of special casing and validity checking and automatically generate documentation that is up to date. We also believe that dealing with the complexity of formally verifying a configuration early in development leads to a better design of your configuration.

Features
--------
- Validate configurations.
- Provide an extensive list of errors when applicable.
- Output a single immutable configuration object where all values are provided.
- Support for multiple data sources, yielding the possibility of default values as well as user and workspace configurations on top of the current configuration.
- Generating documentation that adheres to the technical requirements.
- No exceptions are thrown based on user-input (this is currently not true for
  validatiors).
- Context based validators and transformations.

Installation
------------
The simplest way to fetch the newest version of *Config Suite* is via `PyPI <https://pypi.python.org/pypi/configsuite/>`_::

    >>> pip install configsuite

License
-------

MIT License

Copyright (c) 2018 Equinor ASA and The Netherlands Organisation for Applied
Scientific Research TNO

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
