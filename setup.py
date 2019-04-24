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


import setuptools


setuptools.setup(
    name="configsuite",
    packages=["configsuite"],
    author="Software Innovation Bergen, Statoil ASA and TNO",
    use_scm_version={"write_to": "configsuite/_version.py"},
    install_requires=['enum34==1.1.6 ; python_version<"3.4"'],
    setup_requires=[
        "pytest-runner",
        "pytest-pylint",
        "setuptools_scm",
        "setuptools_scm_about",
    ],
    tests_require=[
        "pytest",
        'black ; python_version>="3.6"',
        'click ; python_version>="3.6"',
        "pylint",
    ],
    test_suite="tests",
)
