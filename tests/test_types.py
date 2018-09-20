import unittest
import type_name
from type_name import MetaKeys as MK


def _build_name_pet_schema():
    return {
        MK.Type: type_name.types.Dict,
        MK.Content: {
            'name': {
                MK.Type: type_name.types.String,
            },
            'pet': {
                MK.Type: type_name.types.String,
            }
        }
    }


def _build_name_pet_config_suite(raw_config):
    return type_name.ConfigSuite(raw_config, _build_name_pet_schema())


class TestTypes(unittest.TestCase):

    def test_name_pet_accepted(self):
        raw_config = {
            'name': 'Markus',
            'pet': 'Donkey Kong',
        }
        config_suite = _build_name_pet_config_suite(raw_config)

        self.assertTrue(config_suite.valid)

        config = config_suite.snapshot
        self.assertEqual(raw_config['name'], config.name)
        self.assertEqual(raw_config['pet'], config.pet)

    def test_name_pet_invalid_pet(self):
        for pet in [14, None, [], (), {}]:
            raw_config = {
                'name': 'Markus',
                'pet': pet,
            }
            config_suite = _build_name_pet_config_suite(raw_config)

            self.assertFalse(config_suite.valid)

            config = config_suite.snapshot
            self.assertEqual(raw_config['name'], config.name)
            self.assertEqual(raw_config['pet'], config.pet)

    def test_name_pet_invalid_container(self):
        for raw_config in [14, None, [{'name': 'Markus'}], ()]:
            config_suite = _build_name_pet_config_suite(raw_config)
            self.assertFalse(config_suite.valid)
