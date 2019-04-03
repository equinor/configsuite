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


import unittest
import sys
import os


class TestCodeFormat(unittest.TestCase):
    @unittest.skipIf(sys.version_info < (3, 6), reason="requires python3.6 or higher")
    def test_code_style(self):
        # pylint: disable=import-error
        import black

        # pylint: disable=import-error
        from click.testing import CliRunner

        root_dir = os.path.dirname(os.path.dirname(__file__))
        runner = CliRunner()
        resp = runner.invoke(
            black.main,
            [
                "--check",
                os.path.join(root_dir, "configsuite"),
                os.path.join(root_dir, "tests"),
                "-v",
                "--exclude",
                r".*_version.py",
            ],
        )

        self.assertEqual(
            resp.exit_code,
            0,
            msg="Black would still reformat one or ore files:\n{}".format(resp.output),
        )
