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


@configsuite.validator_msg("Name should not be empty")
def _non_empty_name(elem):
    return len(elem) > 0


def _build_candybag_schema():
    return {
        MK.Type: types.List,
        MK.Content: {
            MK.Item: {
                MK.Type: types.NamedDict,
                MK.Content: {
                    "color": {MK.Type: types.String},
                    "name": {
                        MK.Type: types.String,
                        MK.ElementValidators: (_non_empty_name,),
                    },
                    "price": {MK.Type: types.Number},
                    "story": {MK.Type: types.String, MK.Required: False},
                },
            }
        },
    }


def _build_valid_candibag_config():
    return [
        {
            "color": "green",
            "name": "Hulk",
            "price": 0.1,
            "story": "Created from the remains of the Hulk",
        },
        {"color": "red", "name": "crazy spicy", "price": 1},
    ]


class TestSchemaValidation(unittest.TestCase):
    def test_basis_schema(self):
        raw_config = _build_valid_candibag_config()
        config_suite = configsuite.ConfigSuite(raw_config, _build_candybag_schema())
        self.assertTrue(config_suite.valid)

    def test_missing_type_first_level(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema.pop(MK.Type)
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_extra_key_first_level(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema["unknown"] = "some value"
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_invalid_type_first_level(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema[MK.Required] = "some value"
        with self.assertRaises(TypeError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_dict_missing_content(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema[MK.Content][MK.Item].pop(MK.Content)
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_invalid_schema_dict_value(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema[MK.Content][MK.Item][MK.Content]["color"].pop(MK.Type)
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_invalid_dict_keys(self):
        invalid_keys = ["1monkey", "monkey-donkey", "a b c"]
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()

        for inv_key in invalid_keys:
            schema[MK.Content][MK.Item][MK.Content][inv_key] = {MK.Type: types.String}
            with self.assertRaises(KeyError):
                configsuite.ConfigSuite(raw_config, schema)

    def test_list_missing_content(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema.pop(MK.Content)
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_list_empty_content(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema[MK.Content].pop(MK.Item)
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)

    def test_list_dubious_content(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema[MK.Content]["dubious"] = "content"
        with self.assertRaises(KeyError):
            configsuite.ConfigSuite(raw_config, schema)
