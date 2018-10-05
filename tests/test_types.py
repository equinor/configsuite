import numbers
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
                    'weight': {
                        MK.Type: types.Number,
                    },
                    'nkids': {
                        MK.Type: types.Integer,
                    },
                    'likeable': {
                        MK.Type: types.Bool,
                    },
                },
            },
        },
    }


def _build_name_pet_config_suite(raw_config):
    return protoconf.ConfigSuite(raw_config, _build_name_pet_schema())

def _build_valid_pet_config():
    return {
        'name': 'Markus',
        'pet': {
            'name': 'Donkey Kong',
            'favourite_food': 'bananas',
            'weight': 1.9,
            'nkids': 8,
            'likeable': True,
        },
    }


class TestTypes(unittest.TestCase):

    def test_name_pet_accepted(self):
        raw_config = _build_valid_pet_config()
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
            raw_config = _build_valid_pet_config()
            raw_config['name'] = name

            config_suite = _build_name_pet_config_suite(raw_config)

            self.assertFalse(config_suite.valid)

            self.assertEqual(1, len(config_suite.errors))
            err = config_suite.errors[0]
            self.assertIsInstance(err, protoconf.InvalidTypeError)
            self.assertEqual(('name',), err.key_path)

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

            self.assertEqual(1, len(config_suite.errors))
            err = config_suite.errors[0]
            self.assertIsInstance(err, protoconf.InvalidTypeError)
            self.assertEqual((), err.key_path)

    def test_name_pet_invalid_pet(self):
        for pet in [14, None, [{'name': 'Markus'}], ()]:
            raw_config = { 'name': 'Markus', 'pet': pet }
            config_suite = _build_name_pet_config_suite(raw_config)
            self.assertFalse(config_suite.valid)

            self.assertEqual(1, len(config_suite.errors))
            err = config_suite.errors[0]
            self.assertIsInstance(err, protoconf.InvalidTypeError)
            self.assertEqual(('pet',), err.key_path)

    def test_unknown_key(self):
        raw_config = _build_valid_pet_config()
        raw_config['favourite_food'] = 'bibimpap'
        config_suite = _build_name_pet_config_suite(raw_config)

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, protoconf.UnknownKeyError)
        self.assertEqual((), err.key_path)

    def test_missing_pet_name(self):
        raw_config = _build_valid_pet_config()
        raw_config['pet'].pop('name')
        config_suite = _build_name_pet_config_suite(raw_config)

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, protoconf.MissingKeyError)
        self.assertEqual(('pet',), err.key_path)

    def test_string(self):
        for strval in ['fdnsjk', '', 'str4thewin', True, [], 1, 1.2, {}, None]:
            raw_config = _build_valid_pet_config()
            raw_config['name'] = strval
            config_suite = _build_name_pet_config_suite(raw_config)

            if isinstance(strval, str):
                self.assertTrue(config_suite.valid)
                self.assertEqual(strval, config_suite.snapshot.name)
                self.assertEqual(0, len(config_suite.errors))
            else:
                self.assertFalse(config_suite.valid)
                self.assertEqual(1, len(config_suite.errors))
                err = config_suite.errors[0]
                self.assertIsInstance(err, protoconf.InvalidTypeError)
                self.assertEqual(('name',), err.key_path)

    def test_int(self):
        for intval in ['fdnsjk', '', False, 0, -10, [], 1, 1.2, {}, None]:
            raw_config = _build_valid_pet_config()
            raw_config['pet']['nkids'] = intval
            config_suite = _build_name_pet_config_suite(raw_config)

            if isinstance(intval, int):
                self.assertTrue(config_suite.valid)
                self.assertEqual(intval, config_suite.snapshot.pet.nkids)
                self.assertEqual(0, len(config_suite.errors))
            else:
                self.assertFalse(config_suite.valid)
                self.assertEqual(1, len(config_suite.errors))
                err = config_suite.errors[0]
                self.assertIsInstance(err, protoconf.InvalidTypeError)
                self.assertEqual(('pet', 'nkids'), err.key_path)

    def test_number(self):
        for numval in [False, True, 'fdnsjk', '', 0, -10, [], 1, 1.2, {}, None]:
            raw_config = _build_valid_pet_config()
            raw_config['pet']['weight'] = numval
            config_suite = _build_name_pet_config_suite(raw_config)

            if isinstance(numval, numbers.Number):
                self.assertTrue(config_suite.valid)
                self.assertEqual(numval, config_suite.snapshot.pet.weight)
                self.assertEqual(0, len(config_suite.errors))
            else:
                self.assertFalse(config_suite.valid)
                self.assertEqual(1, len(config_suite.errors))
                err = config_suite.errors[0]
                self.assertIsInstance(err, protoconf.InvalidTypeError)
                self.assertEqual(('pet', 'weight'), err.key_path)

    def test_bool(self):
        for boolval in [False, True, 'fdnsjk', '', 0, -10, [], 1, 1.2, {}, None]:
            raw_config = _build_valid_pet_config()
            raw_config['pet']['likeable'] = boolval
            config_suite = _build_name_pet_config_suite(raw_config)

            if isinstance(boolval, bool):
                self.assertTrue(config_suite.valid)
                self.assertEqual(boolval, config_suite.snapshot.pet.likeable)
                self.assertEqual(0, len(config_suite.errors))
            else:
                self.assertFalse(config_suite.valid)
                self.assertEqual(1, len(config_suite.errors))
                err = config_suite.errors[0]
                self.assertIsInstance(err, protoconf.InvalidTypeError)
                self.assertEqual(('pet', 'likeable'), err.key_path)
