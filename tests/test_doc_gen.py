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


import unittest
import sys

import configsuite

from . import data


class TestDocGen(unittest.TestCase):
    @unittest.skipIf(sys.version_info < (3, 6), reason="requires python3.6 or higher")
    def test_doc_generate(self):
        """This test is skipped for Python versions prior to 3.6 due to those
        not preserving the order of a dictionary (it is technically not a part
        of the API of 3.6 either, but it is how it is implemented) and hence
        not the output of the doc.generate either.
        """
        schema = data.pets.build_schema()
        docs = configsuite.docs.generate(schema)

        exp_docs = data.pets.build_docs()
        self.assertEqual(exp_docs, docs)

    def test_doc_generate_weak(self):
        """This is a much weaker version of the test_doc_generate. It still
        checks that the generator gives output that could possibly be the same
        as the proper test.
        """
        schema = data.pets.build_schema()
        docs = configsuite.docs.generate(schema)

        exp_docs = data.pets.build_docs()
        self.assertEqual(sorted(exp_docs), sorted(docs))
