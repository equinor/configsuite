import unittest

import protoconf
from protoconf import MetaKeys as MK
from protoconf import types


@protoconf.validator_msg('Name should not be empty')
def _non_empty_name(elem):
    return len(elem) > 0


def _build_candybag_schema():
    return {
        MK.Type: types.List,
        MK.Content: {
            MK.Item: { MK.Type: types.Dict,
                MK.Content: {
                    'color': { MK.Type: types.String },
                    'name': {
                        MK.Type: types.String,
                        MK.ElementValidators: (_non_empty_name,),
                    },
                    'price': { MK.Type: types.Number },
                    'story': {
                        MK.Type: types.String,
                        MK.Required: False,
                    },
                },
            },
        },
    }


def _build_valid_candibag_config():
    return [
        {
            'color': 'green',
            'name': 'Hulk',
            'price': 0.1,
            'story': 'Created from the remains of the Hulk',
        },
        {
            'color': 'red',
            'name': 'crazy spicy',
            'price': 1,
        },
    ]



class TestSchemaValidation(unittest.TestCase):

    def test_basis_schema(self):
        raw_config = _build_valid_candibag_config()
        config_suite = protoconf.ConfigSuite(raw_config, _build_candybag_schema())
        self.assertTrue(config_suite.valid)

    def test_missing_type_first_level(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema.pop(MK.Type)
        with self.assertRaises(KeyError):
            config_suite = protoconf.ConfigSuite(raw_config, schema)

    def test_extra_key_first_level(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema['unknown'] = 'some value'
        with self.assertRaises(KeyError):
            config_suite = protoconf.ConfigSuite(raw_config, schema)

    def test_invalid_type_first_level(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema[MK.Required] = 'some value'
        with self.assertRaises(TypeError):
            config_suite = protoconf.ConfigSuite(raw_config, schema)

    def test_dict_missing_content(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema[MK.Content][MK.Item].pop(MK.Content)
        with self.assertRaises(KeyError):
            config_suite = protoconf.ConfigSuite(raw_config, schema)

    def test_invalid_schema_dict_value(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema[MK.Content][MK.Item][MK.Content]['color'].pop(MK.Type)
        with self.assertRaises(KeyError):
            config_suite = protoconf.ConfigSuite(raw_config, schema)

    def test_invalid_dict_keys(self):
        invalid_keys = ['1monkey', 'monkey-donkey', 'a b c']
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()

        for inv_key in invalid_keys:
            schema[MK.Content][MK.Item][MK.Content][inv_key] = {
                MK.Type: types.String
            }
            with self.assertRaises(KeyError):
                config_suite = protoconf.ConfigSuite(raw_config, schema)

    def test_list_missing_content(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema.pop(MK.Content)
        with self.assertRaises(KeyError):
            config_suite = protoconf.ConfigSuite(raw_config, schema)

    def test_list_empty_content(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema[MK.Content].pop(MK.Item)
        with self.assertRaises(KeyError):
            config_suite = protoconf.ConfigSuite(raw_config, schema)

    def test_list_dubious_content(self):
        raw_config = _build_valid_candibag_config()
        schema = _build_candybag_schema()
        schema[MK.Content]['dubious'] = 'content'
        with self.assertRaises(KeyError):
            config_suite = protoconf.ConfigSuite(raw_config, schema)
