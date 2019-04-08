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


class TestKeys(unittest.TestCase):
    def test_plain_candidate_config(self):
        raw_config = data.candidate.build_config()
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candidate.build_schema()
        )
        self.assertTrue(config_suite.valid)

    def test_unknown_key(self):
        raw_config = data.candidate.build_config()
        raw_config["favourite_food"] = "bibimpap"
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candidate.build_schema()
        )

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.UnknownKeyError)
        self.assertEqual((), err.key_path)

    def test_missing_key(self):
        raw_config = data.candidate.build_config()
        raw_config.pop("name")
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candidate.build_schema()
        )

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.MissingKeyError)
        self.assertEqual((), err.key_path)

    def test_not_required(self):
        raw_config = data.candidate.build_config()
        raw_config.pop("weight")
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candidate.build_schema()
        )

        self.assertTrue(config_suite.valid)
        self.assertEqual(None, config_suite.snapshot.weight)

    def test_required_if_parent(self):
        raw_config = data.candidate.build_config()
        raw_config["current_job"].pop("company_name")
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candidate.build_schema()
        )

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.MissingKeyError)
        self.assertEqual(("current_job",), err.key_path)

    def test_optional_child_of_optional(self):
        raw_config = data.candidate.build_config()
        raw_config["current_job"].pop("position")
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candidate.build_schema()
        )

        self.assertTrue(config_suite.valid)
