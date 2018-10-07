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
        }
    }


def _build_valid_candidate_config():
    return {
        'name': 'Atle Jonny',
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
