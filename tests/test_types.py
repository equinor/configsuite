import unittest
import type_name


def _build_name_pet_schema():
    return {
        type_name.MetaKeys.Type: type_name.types.Dict,
        type_name.MetaKeys.Content: {
            'name': {
                type_name.MetaKeys.Type: type_name.types.String,
            },
            'pet': {
                type_name.MetaKeys.Type: type_name.types.String,
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

            config = config_suite.snapshot
            self.assertEqual(raw_config['name'], config.name)
            self.assertEqual(raw_config['pet'], config.pet)
