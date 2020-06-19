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

import configsuite
from configsuite import MetaKeys as MK

from . import data


class TestContainers(unittest.TestCase):
    def test_invalid_base_dict(self):
        for raw_config in [14, None, [{"name": "Markus"}], ()]:
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())
            self.assertFalse(config_suite.valid)

            self.assertEqual(1, len(config_suite.errors))
            err = config_suite.errors[0]
            self.assertIsInstance(err, configsuite.InvalidTypeError)
            self.assertEqual((), err.key_path)

    def test_invalid_dict(self):
        for pet in [14, None, [{"name": "Markus"}], ()]:
            raw_config = data.pets.build_config()
            raw_config["pet"] = pet
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())
            self.assertFalse(config_suite.valid)

            self.assertEqual(1, len(config_suite.errors))
            err = config_suite.errors[0]
            self.assertIsInstance(err, configsuite.InvalidTypeError)
            self.assertEqual(("pet",), err.key_path)

    def test_list(self):
        playgrounds = [{"name": "superfun", "score": 1}, {"name": "Hell", "score": 99}]

        for end_idx, _ in enumerate(playgrounds):
            raw_config = data.pets.build_config()
            raw_config["playgrounds"] = playgrounds[:end_idx]
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

            self.assertTrue(config_suite.valid, "Errors: %r" % (config_suite.errors,))
            config = config_suite.snapshot
            self.assertEqual(end_idx, len(config.playgrounds))

            for idx, plgr in enumerate(playgrounds[:end_idx]):
                self.assertEqual(plgr["name"], config.playgrounds[idx].name)
                self.assertEqual(plgr["score"], config.playgrounds[idx].score)

    def test_containers_in_named_dicts(self):
        schema = {
            MK.Type: configsuite.types.NamedDict,
            MK.Content: {
                "list": {
                    MK.Type: configsuite.types.List,
                    MK.Content: {MK.Item: {MK.Type: configsuite.types.Number}},
                },
                "dict": {
                    MK.Type: configsuite.types.Dict,
                    MK.Content: {
                        MK.Key: {MK.Type: configsuite.types.String},
                        MK.Value: {MK.Type: configsuite.types.Number},
                    },
                },
                "named_dict": {
                    MK.Type: configsuite.types.NamedDict,
                    MK.Content: {
                        "a": {MK.Type: configsuite.types.Number, MK.Default: 0}
                    },
                },
            },
        }

        suite = configsuite.ConfigSuite({}, schema, deduce_required=True)
        self.assertTrue(suite.valid, suite.errors)
        self.assertEqual((), suite.snapshot.list)
        self.assertEqual((), suite.snapshot.dict)
        self.assertEqual(0, suite.snapshot.named_dict.a)

    def test_list_errors(self):
        raw_config = data.pets.build_config()
        raw_config["playgrounds"] = [{"name": "faulty grounds"}]
        config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.MissingKeyError)
        self.assertEqual(("playgrounds", 0), err.key_path)

    def test_list_cannot_spec_required(self):
        schema = {
            MK.Type: configsuite.types.List,
            MK.Content: {MK.Item: {MK.Type: configsuite.types.Integer}},
        }
        config_suite = configsuite.ConfigSuite([], schema)
        self.assertTrue(config_suite.valid)

        for req in (True, False):
            schema[MK.Required] = req
            with self.assertRaises(ValueError) as err:
                configsuite.ConfigSuite([], schema)
            self.assertIn("Required can only be used for BasicType", str(err.exception))

    def test_list_disallow_empty(self):
        schema = {
            MK.Type: configsuite.types.List,
            MK.AllowEmpty: False,
            MK.Content: {MK.Item: {MK.Type: configsuite.types.Integer}},
        }

        non_empty_suite = configsuite.ConfigSuite([1, 2, 3], schema)
        self.assertTrue(non_empty_suite.valid)

        empty_suite = configsuite.ConfigSuite([], schema)
        self.assertFalse(empty_suite.valid)
        self.assertEqual(1, len(empty_suite.errors))
        self.assertIn("Expected non-empty container", empty_suite.errors[0].msg)

    def test_list_disallow_empty_layers(self):
        schema = {
            MK.Type: configsuite.types.List,
            MK.AllowEmpty: False,
            MK.Content: {MK.Item: {MK.Type: configsuite.types.Integer}},
        }

        suite = configsuite.ConfigSuite([], schema, layers=([1, 2, 3],))
        self.assertTrue(suite.valid)

        suite = configsuite.ConfigSuite([1, 2, 3], schema, layers=([],))
        self.assertTrue(suite.valid)

    def test_named_dict_cannot_spec_required(self):
        schema = {
            MK.Type: configsuite.types.NamedDict,
            MK.Content: {"key": {MK.Type: configsuite.types.Integer}},
        }
        config_suite = configsuite.ConfigSuite({"key": 42}, schema)
        self.assertTrue(config_suite.valid)

        for req in (True, False):
            schema[MK.Required] = req
            with self.assertRaises(ValueError) as err:
                configsuite.ConfigSuite({"key": 42}, schema)
            self.assertIn("Required can only be used for BasicType", str(err.exception))

    def test_dict_cannot_spec_required(self):
        schema = {
            MK.Type: configsuite.types.Dict,
            MK.Content: {
                MK.Key: {MK.Type: configsuite.types.String},
                MK.Value: {MK.Type: configsuite.types.String},
            },
        }
        config_suite = configsuite.ConfigSuite({}, schema)
        self.assertTrue(config_suite.valid)

        for req in (True, False):
            schema[MK.Required] = req
            with self.assertRaises(ValueError) as err:
                configsuite.ConfigSuite({}, schema)
            self.assertIn("Required can only be used for BasicType", str(err.exception))

    def test_dict_disallow_empty(self):
        schema = {
            MK.Type: configsuite.types.Dict,
            MK.AllowEmpty: False,
            MK.Content: {
                MK.Key: {MK.Type: configsuite.types.String},
                MK.Value: {MK.Type: configsuite.types.Integer},
            },
        }

        non_empty_suite = configsuite.ConfigSuite({"a": 1, "b": 2}, schema)
        self.assertTrue(non_empty_suite.valid)

        empty_suite = configsuite.ConfigSuite({}, schema)
        self.assertFalse(empty_suite.valid)
        self.assertEqual(1, len(empty_suite.errors))
        self.assertIn("Expected non-empty container", empty_suite.errors[0].msg)

    def test_allow_empty_named_dict_invalid(self):
        for val in [True, False]:
            schema = {
                MK.Type: configsuite.types.NamedDict,
                MK.AllowEmpty: val,
                MK.Content: {"a": {MK.Type: configsuite.types.Integer}},
            }

            with self.assertRaises(ValueError) as err:
                configsuite.ConfigSuite("fdsfds", schema)
            self.assertIn(
                "Only variable length containers can specify AllowEmpty is false",
                str(err.exception),
            )
