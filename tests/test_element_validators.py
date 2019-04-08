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
from configsuite import MetaKeys as MK

from . import data


class TestElementValidators(unittest.TestCase):
    def test_element_validator_valid(self):
        raw_config = data.candy_bag.build_config()
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candy_bag.build_schema()
        )
        self.assertTrue(config_suite.valid)

    def test_element_validator_single_fail(self):
        raw_config = data.candy_bag.build_config()
        raw_config[0]["name"] = ""
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candy_bag.build_schema()
        )

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.InvalidValueError)
        self.assertEqual((0, "name"), err.key_path)
        self.assertEqual("Name should not be empty is false on input ", err.msg)

    def test_element_validator_double_fail(self):
        raw_config = data.candy_bag.build_config()
        raw_config[0]["name"] = ""
        raw_config[1]["name"] = ""
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candy_bag.build_schema()
        )

        self.assertFalse(config_suite.valid)
        self.assertEqual(2, len(config_suite.errors))
        for idx, err in enumerate(config_suite.errors):
            self.assertIsInstance(err, configsuite.InvalidValueError)
            self.assertEqual((idx, "name"), err.key_path)

    def test_element_validator_type_error(self):
        raw_config = data.candy_bag.build_config()
        raw_config[0]["name"] = 0
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candy_bag.build_schema()
        )

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.InvalidTypeError)
        self.assertEqual((0, "name"), err.key_path)

    def test_multiple_validators(self):
        @configsuite.validator_msg('Name should be "Hulk" or "crazy spicy"')
        def _valid_name(name):
            return name in ["Hulk", "crazy spicy"]

        schema = data.candy_bag.build_schema()
        schema[MK.Content][MK.Item][MK.Content]["name"][MK.ElementValidators] += (
            _valid_name,
        )

        raw_config = data.candy_bag.build_config()
        raw_config[0]["name"] = ""
        config_suite = configsuite.ConfigSuite(raw_config, schema)

        self.assertFalse(config_suite.valid)
        self.assertEqual(2, len(config_suite.errors))
        for err in config_suite.errors:
            self.assertIsInstance(err, configsuite.InvalidValueError)
            self.assertEqual((0, "name"), err.key_path)
