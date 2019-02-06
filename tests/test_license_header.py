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

import datetime
import unittest
import os
import configsuite


class TestLicenseHeaders(unittest.TestCase):

    header_fmt = """\"\"\"Copyright {year} Equinor ASA and The Netherlands Organisation for
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
\"\"\"
"""

    def setUp(self):
        ignore_extensions = (".pyc",)

        source_dirs = (os.path.dirname(configsuite.__file__), os.path.dirname(__file__))

        source_files = [os.path.join(os.path.dirname(__file__), "..", "setup.py")]
        for sdir in source_dirs:
            for path, _, filenames in os.walk(sdir):
                source_files += [os.path.join(path, fn) for fn in filenames]

        def is_source_file(filename):
            return (
                os.path.splitext(filename)[1] not in ignore_extensions
                and os.path.basename(filename) != "_version.py"
            )

        self.source_files = filter(is_source_file, map(os.path.realpath, source_files))
        self.valid_years = range(2018, datetime.datetime.now().year + 1)

    def test_license_headers(self):
        header_length = self.header_fmt.count("\n")

        for sfile in self.source_files:
            with open(sfile) as f:
                file_header = "".join(f.readlines()[:header_length])
                err_msg = "{} missing correct header".format(sfile)
                valid_header = any(
                    [
                        self.header_fmt.format(year=year) == file_header
                        for year in self.valid_years
                    ]
                )

                self.assertTrue(valid_header, err_msg)
