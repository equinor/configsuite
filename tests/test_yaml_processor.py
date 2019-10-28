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
from configsuite import ConfigSuite, types, MetaKeys as MK
from configsuite.yaml_processor import YamlProcessor, DuplicateKeyError

_yaml = """
---
- first: document
  second: still the same document
  hash:
    foo: 1
    bar: 2
    zip: zoop
"""


class TestYamlProcessor(unittest.TestCase):
    def test_init(self):
        YamlProcessor(_yaml)

    def test_duplicate(self):
        conf = "a: 1\nb: 2\na: 3\n"

        with self.assertRaises(DuplicateKeyError):
            YamlProcessor(conf)

    def test_key_lookup(self):
        schema = {
            MK.Type: types.List,
            MK.Content: {
                MK.Item: {
                    MK.Type: types.NamedDict,
                    MK.Content: {
                        "first": {MK.Type: types.String},
                        "second": {MK.Type: types.String},
                        "hash": {MK.Type: types.String},  # Correctly invalid schema
                    },
                }
            },
        }

        proc = YamlProcessor(_yaml)
        suite = ConfigSuite(proc.get_documents()[0], schema)

        self.assertFalse(suite.valid)
        self.assertEqual(len(suite.errors), 1)

        error, = suite.errors
        mark = proc.get_mark(error.key_path)

        # FIXME: This shows that the error occurs on `foo: 1`, instead of the previous line where it'd be correct.
        self.assertEqual(mark.line, 5)
        self.assertEqual(mark.column, 4)
