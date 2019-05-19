"""Copyright 2018 Equinor ASA and The Netherlands Organisation for
Applied Scientific Research TNO.

Licensed under the MIT license.

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the conditions stated in the LICENSE file in the project root for
details.

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.
"""


import os
import setuptools


PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))


def _load_readme():
    readme = os.path.join(PROJECT_ROOT, "README.md")
    with open(readme) as f:
        return f.read()


setuptools.setup(
    name="configsuite",
    author="Software Innovation Bergen, Equinor ASA and TNO",
    url="https://github.com/equinor/configsuite",
    description=(
        "Config Suite is the result of recognizing the complexity of "
        "software configuration."
    ),
    long_description=_load_readme(),
    long_description_content_type="text/markdown",
    packages=["configsuite", "configsuite.docs"],
    use_scm_version={"write_to": "configsuite/_version.py"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Documentation",
        "Topic :: Utilities",
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    install_requires=[
        "enum34 >= 1.0 ; python_version<'3.4'",
        "six >= 1.0 ; python_version<'3'",
    ],
    setup_requires=[
        "setuptools_scm",
        "setuptools_scm_about",
    ],
    tests_require=[
        "pytest",
        "pytest-runner",
        "pytest-pylint",
        "black ; python_version>='3.6'",
        "click ; python_version>='3.6'",
        "pylint",
        "pytest-cov",
        "jinja2",
    ],
    test_suite="tests",
)
