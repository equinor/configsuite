"""Copyright 2019 Equinor ASA and The Netherlands Organisation for
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
import subprocess
import sys
import unittest


DOCTEST_MINIMUM_PY_VERSION = (3, 6)


class TestDocumentationExamples(unittest.TestCase):
    def setUp(self):
        self._orig_cwd = os.getcwd()
        root_dir = os.path.dirname(os.path.dirname(__file__))
        doc_dir = os.path.join(root_dir, "docs")
        os.chdir(doc_dir)

    def tearDown(self):
        os.chdir(self._orig_cwd)

    @unittest.skipIf(
        sys.version_info < DOCTEST_MINIMUM_PY_VERSION,
        reason="requires python3.6 or higher",
    )
    def test_doc_examples(self):
        # The below is to disable pylint complaints when Python version <= 3.4
        # pylint: disable=bad-option-value,subprocess-run-check,no-member
        resp = subprocess.run(
            ["make doctest"],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        self.assertEqual(
            resp.returncode,
            0,
            msg="Documentation examples failed:\n{}".format(
                resp.stdout.decode("utf-8")
            ),
        )
