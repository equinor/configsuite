import unittest


import protoconf
from protoconf import MetaKeys as MK
from protoconf import types


def _build_candidate_schema():
    return {
        MK.Type: types.Dict,
        MK.Content: {
            'name': {
                MK.Type: types.String,
            },
            'weight': {
                MK.Type: types.Number,
                MK.Required: False,
            },
            'current_job': {
                MK.Type: types.Dict,
                MK.Required: False,
                MK.Content: {
                    'company_name': {
                        MK.Type: types.String,
                    },
                    'position': {
                        MK.Type: types.String,
                        MK.Required: False,
                    },
                },
            },
        }
    }


def _build_valid_candidate_config():
    return {
        'name': 'Atle Jonny',
        'weight': 100,
        'current_job': {
            'company_name': 'Super Traktor',
            'position': 'Assisting director of the printer room',
        },
    }


class TestKeys(unittest.TestCase):

    def test_plain_candidate_config(self):
        raw_config = _build_valid_candidate_config()
        config_suite = protoconf.ConfigSuite(raw_config, _build_candidate_schema())
        self.assertTrue(config_suite.valid)

    def test_unknown_key(self):
        raw_config = _build_valid_candidate_config()
        raw_config['favourite_food'] = 'bibimpap'
        config_suite = protoconf.ConfigSuite(raw_config, _build_candidate_schema())

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, protoconf.UnknownKeyError)
        self.assertEqual((), err.key_path)

    def test_missing_key(self):
        raw_config = _build_valid_candidate_config()
        raw_config.pop('name')
        config_suite = protoconf.ConfigSuite(raw_config, _build_candidate_schema())

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, protoconf.MissingKeyError)
        self.assertEqual((), err.key_path)

    def test_not_required(self):
        raw_config = _build_valid_candidate_config()
        raw_config.pop('weight')
        config_suite = protoconf.ConfigSuite(raw_config, _build_candidate_schema())

        self.assertTrue(config_suite.valid)
        self.assertEqual(None, config_suite.snapshot.weight)

    def test_required_if_parent(self):
        raw_config = _build_valid_candidate_config()
        raw_config['current_job'].pop('company_name')
        config_suite = protoconf.ConfigSuite(raw_config, _build_candidate_schema())

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, protoconf.MissingKeyError)
        self.assertEqual(('current_job',), err.key_path)

    def test_optional_child_of_optional(self):
        raw_config = _build_valid_candidate_config()
        raw_config['current_job'].pop('position')
        config_suite = protoconf.ConfigSuite(raw_config, _build_candidate_schema())

        self.assertTrue(config_suite.valid)
