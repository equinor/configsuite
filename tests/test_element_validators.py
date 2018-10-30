import unittest


import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


@configsuite.validator_msg('Name should not be empty')
def _non_empty_name(elem):
    return len(elem) > 0


def _build_candybag_schema():
    return {
        MK.Type: types.List,
        MK.Content: {
            MK.Item: {
                MK.Type: types.Dict,
                MK.Content: {
                    'color': { MK.Type: types.String },
                    'name': {
                        MK.Type: types.String,
                        MK.ElementValidators: (_non_empty_name,),
                    },
                    'price': { MK.Type: types.Number },
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
        },
        {
            'color': 'red',
            'name': 'crazy spicy',
            'price': 1,
        },
    ]


class TestElementValidators(unittest.TestCase):

    def test_element_validator_valid(self):
        raw_config = _build_valid_candibag_config()
        config_suite = configsuite.ConfigSuite(raw_config, _build_candybag_schema())

    def test_element_validator_single_fail(self):
        raw_config = _build_valid_candibag_config()
        raw_config[0]['name'] = ''
        config_suite = configsuite.ConfigSuite(raw_config, _build_candybag_schema())

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.InvalidValueError)
        self.assertEqual((0, 'name'), err.key_path)
        self.assertEqual('Name should not be empty is false on input ', err.msg)

    def test_element_validator_double_fail(self):
        raw_config = _build_valid_candibag_config()
        raw_config[0]['name'] = ''
        raw_config[1]['name'] = ''
        config_suite = configsuite.ConfigSuite(raw_config, _build_candybag_schema())

        self.assertFalse(config_suite.valid)
        self.assertEqual(2, len(config_suite.errors))
        for idx, err in enumerate(config_suite.errors):
            self.assertIsInstance(err, configsuite.InvalidValueError)
            self.assertEqual((idx, 'name'), err.key_path)

    def test_element_validator_type_error(self):
        raw_config = _build_valid_candibag_config()
        raw_config[0]['name'] = 0
        config_suite = configsuite.ConfigSuite(raw_config, _build_candybag_schema())

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.InvalidTypeError)
        self.assertEqual((0, 'name'), err.key_path)

    def test_multiple_validators(self):
        @configsuite.validator_msg('Name should be "Hulk" or "crazy spicy"')
        def _valid_name(name):
            return name in ['Hulk', 'crazy spicy']

        schema = _build_candybag_schema()
        schema[MK.Content][MK.Item][MK.Content]['name'][MK.ElementValidators] += (_valid_name,)

        raw_config = _build_valid_candibag_config()
        raw_config[0]['name'] = ''
        config_suite = configsuite.ConfigSuite(raw_config, schema)

        self.assertFalse(config_suite.valid)
        self.assertEqual(2, len(config_suite.errors))
        for idx, err in enumerate(config_suite.errors):
            self.assertIsInstance(err, configsuite.InvalidValueError)
            self.assertEqual((0, 'name'), err.key_path)
