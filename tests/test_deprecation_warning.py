"""Copyright 2020 Equinor ASA and The Netherlands Organisation for
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
import warnings

import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


class TestRequiredDeprecated(unittest.TestCase):
    def test_explicit_required_is_deprecated(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {"some_key": {MK.Type: types.String, MK.Required: True}},
        }
        with warnings.catch_warnings(record=True) as wc:
            configsuite.ConfigSuite({}, schema)
            self.assertEqual(1, len(wc))
            self.assertEqual(__file__, wc[0].filename)
            self.assertIn(
                "Use `ConfigSuite(..., deduce_required=True)`", str(wc[0].message)
            )

    def test_specifying_required_is_deprecated_when_deducing(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {"some_key": {MK.Type: types.String, MK.Required: True}},
        }
        with warnings.catch_warnings(record=True) as wc:
            configsuite.ConfigSuite({}, schema, deduce_required=True)
            self.assertEqual(1, len(wc))
            self.assertEqual(__file__, wc[0].filename)
            self.assertIn("Please remove them from your schema", str(wc[0].message))

    def test_no_deprecation_warning_when_deducing(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {"some_key": {MK.Type: types.String}},
        }
        with warnings.catch_warnings(record=True) as wc:
            suite = configsuite.ConfigSuite({}, schema, deduce_required=True)
            self.assertFalse(suite.valid)
            self.assertEqual(0, len(wc))

    def test_no_error_when_deducing_from_allow_none(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {"some_key": {MK.Type: types.String, MK.AllowNone: True}},
        }
        with warnings.catch_warnings(record=True) as wc:
            suite = configsuite.ConfigSuite({}, schema, deduce_required=True)
            self.assertTrue(suite.valid)
            self.assertEqual(0, len(wc))

    def test_no_error_when_deducing_from_default(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {"some_key": {MK.Type: types.String, MK.Default: "A string"}},
        }
        with warnings.catch_warnings(record=True) as wc:
            suite = configsuite.ConfigSuite({}, schema, deduce_required=True)
            self.assertTrue(suite.valid)
            self.assertEqual(0, len(wc))

    def test_no_error_when_deducing_with_push(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "not_required": {MK.Type: types.Integer, MK.AllowNone: True},
                "a_required_string": {MK.Type: types.String},
            },
        }
        config = {"a_required_string": "a_string"}

        with warnings.catch_warnings(record=True) as wc:
            basic_config = configsuite.ConfigSuite(config, schema, deduce_required=True)
            self.assertTrue(basic_config.valid)

            basic_config = basic_config.push({"not_required": 10})
            self.assertTrue(basic_config.valid)
            self.assertEqual(0, len(wc))
