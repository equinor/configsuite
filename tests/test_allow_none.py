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
from .data import computers


class TestNotAllowNoneContainers(unittest.TestCase):
    def test_not_allow_allownone_for_list(self):
        schema = computers.build_schema()
        config = computers.build_config()

        schema[MK.Content]["externals"][MK.AllowNone] = False

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite(config, schema)
        self.assertIn(
            "AllowNone can only be used for BasicType", str(error_context.exception)
        )

    def test_not_allow_allownone_for_dict(self):
        schema = computers.build_schema()
        config = computers.build_config()

        schema[MK.Content]["software"][MK.AllowNone] = False

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite(config, schema)
        self.assertIn(
            "AllowNone can only be used for BasicType", str(error_context.exception)
        )

    def test_not_allow_allownone_for_named_dict(self):
        schema = computers.build_schema()
        config = computers.build_config()

        schema[MK.Content]["components"][MK.AllowNone] = False

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite(config, schema)
        self.assertIn(
            "AllowNone can only be used for BasicType", str(error_context.exception)
        )


class TestAllowNoneBasicType(unittest.TestCase):
    def test_basictype_explicit_none(self):
        schema = computers.build_schema()
        config = computers.build_config()

        schema[MK.Content]["OS"][MK.AllowNone] = True
        schema[MK.Content]["OS"][MK.Required] = False

        config["OS"] = None
        config_suite = configsuite.ConfigSuite(config, schema)

        self.assertTrue(config_suite.valid)
        self.assertIsNone(config_suite.snapshot.OS)

    def test_basictype_implicit_none(self):
        schema = computers.build_schema()
        config = computers.build_config()

        schema[MK.Content]["OS"][MK.AllowNone] = True
        schema[MK.Content]["OS"][MK.Required] = False
        config.pop("OS")
        config_suite = configsuite.ConfigSuite(config, schema)

        self.assertTrue(config_suite.valid)
        self.assertIsNone(config_suite.snapshot.OS)


class TestNotAllowNoneBasicType(unittest.TestCase):
    def test_basictype_explicit_invalid_none(self):
        schema = computers.build_schema()
        config = computers.build_config()

        schema[MK.Content]["OS"][MK.AllowNone] = False
        config["OS"] = None
        config_suite = configsuite.ConfigSuite(config, schema)

        self.assertFalse(config_suite.valid)
        for err in config_suite.errors:
            self.assertTrue(
                isinstance(err, configsuite.validation_errors.InvalidTypeError)
            )
            self.assertTrue(
                err.msg.startswith("Is x a string is false on input 'None'")
            )

        self.assertTrue(config_suite.readable)
        self.assertIsNone(config_suite.snapshot.OS)
