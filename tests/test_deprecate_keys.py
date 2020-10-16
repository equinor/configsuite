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
import warnings

import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


class TestDeprecateKeys(unittest.TestCase):
    def test_deprecate_keys(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "deprecated_key": {
                    MK.Deprecated: "new_shiny_key"
                },
                "new_shiny_key": {
                    MK.Type: types.Integer,
                },
            },
        }
        config_suite = configsuite.ConfigSuite({"new_shiny_key": 1}, schema)
        assert config_suite.valid

        with warnings.catch_warnings(record=True) as wc:
            config_suite = configsuite.ConfigSuite({"deprecated_key": 1}, schema)
            assert config_suite.valid
            assert config_suite.snapshot.new_shiny_key == 1

            self.assertEqual(1, len(wc))
            self.assertEqual(__file__, wc[0].filename)
            self.assertIn(
                "DeprecationWarning: deprecated_key is deprecated, use new_shiny_key: Deprecation message", str(wc[0].message)
            )

    def test_referenced_key_missing(self):
        schema = {
            MK.Type: types.NamedDict,
            MK.Content: {
                "deprecated_key": {
                    MK.Deprecated: "non_existing_key"
                },
                "new_shiny_key": {
                    MK.Type: types.Integer,
                },
            },
        }

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite({"new_shiny_key": 1}, schema)
        self.assertTrue(
            str(error_context.exception).startswith("MK.Deprecated must refer to a valid key")
        )
