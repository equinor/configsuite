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

import configsuite

from .data import numbers


class TestLayerTransformations(unittest.TestCase):
    def test_layer_transformation_valid(self):
        config = tuple(range(10))
        suite = configsuite.ConfigSuite(config, numbers.build_schema())
        self.assertTrue(suite.valid)
        self.assertEqual(tuple(config), suite.snapshot)

    def test_layer_transformation_valid_singletons(self):
        nums = tuple([x for x in range(10) if x % 2 == 1])
        config = ", ".join(map(str, nums))
        suite = configsuite.ConfigSuite(config, numbers.build_schema())
        self.assertTrue(suite.valid, suite.errors)
        self.assertEqual(nums, suite.snapshot)

    def test_layer_transformation_valid_ranges(self):
        config = "1, 6-6, 11-14, 1000,1-5"
        nums = (1, 6, 11, 12, 13, 14, 1000, 1, 2, 3, 4, 5)
        suite = configsuite.ConfigSuite(config, numbers.build_schema())
        self.assertTrue(suite.valid, suite.errors)
        self.assertEqual(tuple(sorted(set(nums))), suite.snapshot)

    def test_layer_transformation_layers(self):
        layers = ("1-6", "10, 14, 19", [11, 7, 18], "20-30, 100", [200])
        nums = [
            1,
            2,
            3,
            4,
            5,
            6,
            10,
            14,
            19,
            11,
            7,
            18,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            100,
            200,
        ]

        suite = configsuite.ConfigSuite([], numbers.build_schema(), layers=layers)
        self.assertTrue(suite.valid)
        self.assertEqual(tuple(sorted(set(nums))), suite.snapshot)

    def test_layer_transformation_exception(self):
        config = "1--100"
        suite = configsuite.ConfigSuite(config, numbers.build_schema())
        self.assertFalse(suite.readable)
        self.assertEqual(2, len(suite.errors))
        err = suite.errors[0]
        self.assertIsInstance(err, configsuite.TransformationError)
        self.assertEqual(
            "'{}' failed on input '{}' with error '{}'".format(
                "Convert ranges and singeltons into list",
                "1--100",
                "Expected at most one '-' in an element",
            ),
            err.msg,
        )
        self.assertEqual((), err.key_path)

        self.assertIsInstance(suite.errors[1], configsuite.InvalidTypeError)
