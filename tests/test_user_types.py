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

import configsuite

from . import data


class TestUserTypes(unittest.TestCase):
    def test_favourite_numbers_accepted(self):
        raw_config = data.favourite_numbers.build_config()
        schema = data.favourite_numbers.build_schema()
        config_suite = configsuite.ConfigSuite(raw_config, schema)

        self.assertTrue(config_suite.valid)

        config = config_suite.snapshot
        self.assertEqual(raw_config["favourite_uint4"], config.favourite_uint4)
        self.assertEqual(raw_config["favourite_uint8"], config.favourite_uint8)
        self.assertEqual(raw_config["favourite_int"], config.favourite_int)

    def test_favourite_numbers_too_big(self):
        raw_config = data.favourite_numbers.build_config()
        raw_config["favourite_uint4"] = 2 ** 4
        schema = data.favourite_numbers.build_schema()
        config_suite = configsuite.ConfigSuite(raw_config, schema)

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.InvalidTypeError)
        self.assertEqual(("favourite_uint4",), err.key_path)

        config = config_suite.snapshot
        self.assertEqual(raw_config["favourite_uint4"], config.favourite_uint4)
        self.assertEqual(raw_config["favourite_uint8"], config.favourite_uint8)
        self.assertEqual(raw_config["favourite_int"], config.favourite_int)
