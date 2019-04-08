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
from configsuite import types

from . import data


class TestSchemaValidation(unittest.TestCase):
    def test_basis_schema(self):
        raw_config = data.candy_bag.build_story_config()
        config_suite = configsuite.ConfigSuite(
            raw_config, data.candy_bag.build_schema()
        )
        self.assertTrue(config_suite.valid)

    def test_missing_type_first_level(self):
        raw_config = data.candy_bag.build_story_config()
        schema = data.candy_bag.build_schema()
        schema.pop(MK.Type)
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_extra_key_first_level(self):
        raw_config = data.candy_bag.build_story_config()
        schema = data.candy_bag.build_schema()
        schema["unknown"] = "some value"
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_invalid_type_first_level(self):
        raw_config = data.candy_bag.build_story_config()
        schema = data.candy_bag.build_schema()
        schema[MK.Required] = "some value"
        with self.assertRaises(TypeError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_dict_missing_content(self):
        raw_config = data.candy_bag.build_story_config()
        schema = data.candy_bag.build_schema()
        schema[MK.Content][MK.Item].pop(MK.Content)
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_invalid_schema_dict_value(self):
        raw_config = data.candy_bag.build_story_config()
        schema = data.candy_bag.build_schema()
        schema[MK.Content][MK.Item][MK.Content]["color"].pop(MK.Type)
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_invalid_dict_keys(self):
        invalid_keys = ["1monkey", "monkey-donkey", "a b c"]
        raw_config = data.candy_bag.build_story_config()
        schema = data.candy_bag.build_schema()

        for inv_key in invalid_keys:
            schema[MK.Content][MK.Item][MK.Content][inv_key] = {MK.Type: types.String}
            with self.assertRaises(KeyError):
                configsuite.ConfigSuite(raw_config, schema)

    def test_list_missing_content(self):
        raw_config = data.candy_bag.build_story_config()
        schema = data.candy_bag.build_schema()
        schema.pop(MK.Content)
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_list_empty_content(self):
        raw_config = data.candy_bag.build_story_config()
        schema = data.candy_bag.build_schema()
        schema[MK.Content].pop(MK.Item)
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_list_dubious_content(self):
        raw_config = data.candy_bag.build_story_config()
        schema = data.candy_bag.build_schema()
        schema[MK.Content]["dubious"] = "content"
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)
