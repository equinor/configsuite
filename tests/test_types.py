import unittest
import protoconf
from protoconf import MetaKeys as MK
from protoconf import types


def _build_name_pet_schema():
    return {
        MK.Type: types.Dict,
        MK.Content: {
            'name': {
                MK.Type: types.String,
            },
            'pet': {
                MK.Type: types.Dict,
                MK.Content: {
                    'name': {
                        MK.Type: types.String,
                    },
                    'favourite_food': {
                        MK.Type: types.String,
                    },
                },
            },
        },
    }


def _build_name_pet_config_suite(raw_config):
    return protoconf.ConfigSuite(raw_config, _build_name_pet_schema())


class TestTypes(unittest.TestCase):

    def test_name_pet_accepted(self):
        raw_config = {
            'name': 'Markus',
            'pet': {
                'name': 'Donkey Kong',
                'favourite_food': 'bananas',
            },
        }
        config_suite = _build_name_pet_config_suite(raw_config)

        self.assertTrue(config_suite.valid)

        config = config_suite.snapshot
        self.assertEqual(raw_config['name'], config.name)
        self.assertEqual(raw_config['pet']['name'], config.pet.name)
        self.assertEqual(
                raw_config['pet']['favourite_food'],
                config.pet.favourite_food,
                )

    def test_name_pet_invalid_name(self):
        for name in [14, None, [], (), {}]:
            raw_config = {
                'name': name,
                'pet': {
                    'name': 'Donkey Kong',
                    'favourite_food': 'bananas',
                },
            }
            config_suite = _build_name_pet_config_suite(raw_config)

            self.assertFalse(config_suite.valid)

            config = config_suite.snapshot
            self.assertEqual(raw_config['name'], config.name)
            self.assertEqual(raw_config['pet']['name'], config.pet.name)
            self.assertEqual(
                    raw_config['pet']['favourite_food'],
                    config.pet.favourite_food,
                    )

    def test_name_pet_invalid_base_container(self):
        for raw_config in [14, None, [{'name': 'Markus'}], ()]:
            config_suite = _build_name_pet_config_suite(raw_config)
            self.assertFalse(config_suite.valid)

    def test_name_pet_invalid_pet(self):
        for pet in [14, None, [{'name': 'Markus'}], ()]:
            raw_config = { 'name': 'Markus', 'pet': pet }
            config_suite = _build_name_pet_config_suite(raw_config)
            self.assertFalse(config_suite.valid)
