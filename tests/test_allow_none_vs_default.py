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
from configsuite import MetaKeys as MK
from configsuite import types


class TestNotAllowNoneVsDefault(unittest.TestCase):
    def test_allow_none_default_not_required(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "my_value": {
                    MK.Type: types.Integer,
                    MK.AllowNone: True,
                    MK.Required: False,
                    MK.Default: 0,
                },
            },
        }

        for value in (-1, 4, 1000, None):
            suite = configsuite.ConfigSuite({"my_value": value}, schema)
            self.assertTrue(suite.valid)
            self.assertEqual(value, suite.snapshot.my_value)

        suite = configsuite.ConfigSuite({}, schema)
        self.assertTrue(suite.valid)
        self.assertEqual(0, suite.snapshot.my_value)

    def test_allow_none_no_default_not_required(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "my_value": {
                    MK.Type: types.Integer,
                    MK.AllowNone: True,
                    MK.Required: False,
                },
            },
        }

        for value in (-1, 4, 1000, None):
            suite = configsuite.ConfigSuite({"my_value": value}, schema)
            self.assertTrue(suite.valid)
            self.assertEqual(value, suite.snapshot.my_value)

        suite = configsuite.ConfigSuite({}, schema)
        self.assertTrue(suite.valid)
        self.assertEqual(None, suite.snapshot.my_value)

    def test_disallow_none_default_not_required(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "my_value": {
                    MK.Type: types.Integer,
                    MK.AllowNone: False,
                    MK.Default: 0,
                    MK.Required: False,
                },
            },
        }

        for value in (-1, 4, 1000):
            suite = configsuite.ConfigSuite({"my_value": value}, schema)
            self.assertTrue(suite.valid, suite.errors)
            self.assertEqual(value, suite.snapshot.my_value)

            suite = configsuite.ConfigSuite({}, schema)
            self.assertTrue(suite.valid)
            self.assertEqual(0, suite.snapshot.my_value)

        suite = configsuite.ConfigSuite({"my_value": None}, schema)
        self.assertFalse(suite.valid)
        self.assertEqual(None, suite.snapshot.my_value)

    def test_disallow_none_no_default_not_required(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "my_value": {
                    MK.Type: types.Integer,
                    MK.AllowNone: False,
                    MK.Required: False,
                },
            },
        }

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite({}, schema)
        self.assertIn("A schema element can be required", str(error_context.exception))

    def test_allow_none_default_required(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "my_value": {
                    MK.Type: types.Integer,
                    MK.AllowNone: True,
                    MK.Default: 0,
                    MK.Required: True,
                },
            },
        }

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite({}, schema)
        self.assertIn("Required can not have Default", str(error_context.exception))

    def test_allow_none_no_default_required(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "my_value": {
                    MK.Type: types.Integer,
                    MK.AllowNone: True,
                    MK.Required: True,
                },
            },
        }

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite({}, schema)
        self.assertIn("A schema element can be required", str(error_context.exception))

    def test_disallow_none_default_required(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "my_value": {
                    MK.Type: types.Integer,
                    MK.AllowNone: False,
                    MK.Default: 0,
                    MK.Required: True,
                },
            },
        }

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite({}, schema)
        self.assertIn("Required can not have Default", str(error_context.exception))

    def test_disallow_none_no_default_required(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "my_value": {
                    MK.Type: types.Integer,
                    MK.AllowNone: False,
                    MK.Required: True,
                },
            },
        }

        for value in (-1, 4, 1000):
            suite = configsuite.ConfigSuite({"my_value": value}, schema)
            self.assertTrue(suite.valid)
            self.assertEqual(value, suite.snapshot.my_value)

        for config in ({}, {"my_value": None}):
            suite = configsuite.ConfigSuite(config, schema)
            self.assertFalse(suite.valid)
            self.assertEqual(None, suite.snapshot.my_value)
