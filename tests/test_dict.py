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


import numbers
import unittest


import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


@configsuite.validator_msg('Price should be non-negative')
def _non_negative_price(elem):
    return elem > 0


def _build_store_schema():
    return {
        MK.Type: types.NamedDict,
        MK.Content: {
            'employees': {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: { MK.Type: types.String },
                    MK.Value: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            'salary': { MK.Type: types.Number },
                            'shift_leader': { MK.Type: types.String },
                        },
                    },
                },
            },
            'prices': {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: { MK.Type: types.String },
                    MK.Value: {
                        MK.Type: types.Number,
                        MK.ElementValidators: (_non_negative_price,),
                        },
                },
            }
        },
    }


def _build_valid_store_config():
    return {
        'employees': {
            'Are': {
                'salary': 4,
                'shift_leader': 'Jonny',
            },
            'Knut': {
                'salary': 1,
                'shift_leader': 'Are',
            }
        },
        'prices': {
            'flour': 2.3,
            'pig': 10,
        },
    }


def _build_advanced_store_schema():
    return {
        MK.Type: types.NamedDict,
        MK.Content: {
            'employees': {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: { MK.Type: types.String },
                    MK.Value: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            'salary': { MK.Type: types.Number },
                            'shift_leader': { MK.Type: types.String },
                        },
                    },
                },
            },
            'prices': {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: { MK.Type: types.String },
                    MK.Value: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            'kilo': { MK.Type: types.Number },
                            'gram': { MK.Type: types.Number },
                            'unit': { MK.Type: types.Number, MK.Required: False },
                        }
                    },
                },
            }
        },
    }


def _build_valid_advanced_store_config():
    return {
        'employees': {
            'Are': {
                'salary': 4,
                'shift_leader': 'Jonny',
            },
            'Knut': {
                'salary': 1,
                'shift_leader': 'Are',
            }
        },
        'prices': {
            'flour': { 'kilo': 4.5, 'gram': 30 },
            'pig': { 'unit': 100, 'kilo': 20, 'gram': 3 },
        },
    }



class TestDict(unittest.TestCase):

    def test_valid_store_config(self):
        raw_config = _build_valid_store_config()
        store_schema = _build_store_schema()
        config_suite = configsuite.ConfigSuite(raw_config, store_schema)

        self.assertTrue(config_suite.valid)
        prices = [
            (elem.key, elem.value)
            for elem in config_suite.snapshot.prices
        ]
        self.assertEqual(
                sorted(tuple(raw_config['prices'].items())),
                sorted(tuple(prices))
                )

    def test_invalid_schema_no_key(self):
        raw_config = _build_valid_store_config()
        store_schema = _build_store_schema()
        store_schema[MK.Content]['prices'][MK.Content].pop(MK.Key)

        with self.assertRaises(KeyError):
            config_suite = configsuite.ConfigSuite(raw_config, store_schema)

    def test_invalid_schema_no_value(self):
        raw_config = _build_valid_store_config()
        store_schema = _build_store_schema()
        store_schema[MK.Content]['prices'][MK.Content].pop(MK.Value)

        with self.assertRaises(KeyError):
            config_suite = configsuite.ConfigSuite(raw_config, store_schema)

    def test_invalid_schema_extra_spec(self):
        raw_config = _build_valid_store_config()
        store_schema = _build_store_schema()
        store_schema[MK.Content]['prices'][MK.Content]['monkey'] = 'patch'

        with self.assertRaises(KeyError):
            config_suite = configsuite.ConfigSuite(raw_config, store_schema)

    def test_valid_store_config_faulty_key(self):
        raw_config = _build_valid_store_config()
        raw_config['prices'][123] = 1
        store_schema = _build_store_schema()
        config_suite = configsuite.ConfigSuite(raw_config, store_schema)

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.InvalidTypeError)

    def test_valid_store_config_faulty_value(self):
        raw_config = _build_valid_store_config()
        raw_config['prices']['pig'] = 'very expensive'
        store_schema = _build_store_schema()
        config_suite = configsuite.ConfigSuite(raw_config, store_schema)

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.InvalidTypeError)

    def test_valid_advanded_store_config(self):
        raw_config = _build_valid_advanced_store_config()
        store_schema = _build_advanced_store_schema()
        config_suite = configsuite.ConfigSuite(raw_config, store_schema)

        self.assertTrue(config_suite.valid)
        # Map all not listed values to None
        raw_prices = [
            (
                key,
                {
                    key: value.get(key)
                    for key in ('unit', 'kilo', 'gram') 
                }
            )
            for (key, value) in raw_config['prices'].items()
        ]

        # Extract and format prices from config
        prices = [
            (elem.key, {
                'unit': elem.value.unit,
                'kilo': elem.value.kilo,
                'gram': elem.value.gram,
            })
            for elem in config_suite.snapshot.prices
        ]
        self.assertEqual(raw_prices, prices)

    def test_advanced_store_config_faulty_schema(self):
        raw_config = _build_valid_advanced_store_config()
        store_schema = _build_advanced_store_schema()
        store_schema[MK.Content]['prices'][MK.Content][MK.Value][MK.Content]['kilo'].pop(MK.Type)

        with self.assertRaises(KeyError):
            config_suite = configsuite.ConfigSuite(raw_config, store_schema)
