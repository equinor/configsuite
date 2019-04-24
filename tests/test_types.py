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

import datetime
import numbers
import unittest

import configsuite

from . import data


class TestTypes(unittest.TestCase):
    def test_name_pet_accepted(self):
        raw_config = data.pets.build_config()
        config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

        self.assertTrue(config_suite.valid)

        config = config_suite.snapshot
        self.assertEqual(raw_config["name"], config.name)
        self.assertEqual(raw_config["pet"]["name"], config.pet.name)
        self.assertEqual(raw_config["pet"]["favourite_food"], config.pet.favourite_food)

    def test_invalid_string(self):
        for name in [14, None, [], (), {}]:
            raw_config = data.pets.build_config()
            raw_config["name"] = name
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

            self.assertFalse(config_suite.valid)

            self.assertEqual(1, len(config_suite.errors))
            err = config_suite.errors[0]
            self.assertIsInstance(err, configsuite.InvalidTypeError)
            self.assertEqual(("name",), err.key_path)

            config = config_suite.snapshot
            self.assertEqual(raw_config["name"], config.name)
            self.assertEqual(raw_config["pet"]["name"], config.pet.name)
            self.assertEqual(
                raw_config["pet"]["favourite_food"], config.pet.favourite_food
            )

    def test_invalid_base_dict(self):
        for raw_config in [14, None, [{"name": "Markus"}], ()]:
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())
            self.assertFalse(config_suite.valid)

            self.assertEqual(1, len(config_suite.errors))
            err = config_suite.errors[0]
            self.assertIsInstance(err, configsuite.InvalidTypeError)
            self.assertEqual((), err.key_path)

    def test_invalid_dict(self):
        for pet in [14, None, [{"name": "Markus"}], ()]:
            raw_config = data.pets.build_config()
            raw_config["pet"] = pet
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())
            self.assertFalse(config_suite.valid)

            self.assertEqual(1, len(config_suite.errors))
            err = config_suite.errors[0]
            self.assertIsInstance(err, configsuite.InvalidTypeError)
            self.assertEqual(("pet",), err.key_path)

    def test_string(self):
        for strval in ["fdnsjk", "", "str4thewin", True, [], 1, 1.2, {}, None]:
            raw_config = data.pets.build_config()
            raw_config["name"] = strval
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

            if isinstance(strval, str):
                self.assertTrue(config_suite.valid)
                self.assertEqual(strval, config_suite.snapshot.name)
                self.assertEqual(0, len(config_suite.errors))
            else:
                self.assertFalse(config_suite.valid)
                self.assertEqual(1, len(config_suite.errors))
                err = config_suite.errors[0]
                self.assertIsInstance(err, configsuite.InvalidTypeError)
                self.assertEqual(("name",), err.key_path)

    def test_int(self):
        for intval in ["fdnsjk", "", False, 0, -10, [], 1, 1.2, {}, None]:
            raw_config = data.pets.build_config()
            raw_config["pet"]["nkids"] = intval
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

            if isinstance(intval, int):
                self.assertTrue(config_suite.valid)
                self.assertEqual(intval, config_suite.snapshot.pet.nkids)
                self.assertEqual(0, len(config_suite.errors))
            else:
                self.assertFalse(config_suite.valid)
                self.assertEqual(1, len(config_suite.errors))
                err = config_suite.errors[0]
                self.assertIsInstance(err, configsuite.InvalidTypeError)
                self.assertEqual(("pet", "nkids"), err.key_path)

    def test_number(self):
        for numval in [False, True, "fdnsjk", "", 0, -10, [], 1, 1.2, {}, None]:
            raw_config = data.pets.build_config()
            raw_config["pet"]["weight"] = numval
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

            if isinstance(numval, numbers.Number):
                self.assertTrue(config_suite.valid)
                self.assertEqual(numval, config_suite.snapshot.pet.weight)
                self.assertEqual(0, len(config_suite.errors))
            else:
                self.assertFalse(config_suite.valid)
                self.assertEqual(1, len(config_suite.errors))
                err = config_suite.errors[0]
                self.assertIsInstance(err, configsuite.InvalidTypeError)
                self.assertEqual(("pet", "weight"), err.key_path)

    def test_bool(self):
        for boolval in [False, True, "fdnsjk", "", 0, -10, [], 1, 1.2, {}, None]:
            raw_config = data.pets.build_config()
            raw_config["pet"]["likeable"] = boolval
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

            if isinstance(boolval, bool):
                self.assertTrue(config_suite.valid)
                self.assertEqual(boolval, config_suite.snapshot.pet.likeable)
                self.assertEqual(0, len(config_suite.errors))
            else:
                self.assertFalse(config_suite.valid)
                self.assertEqual(1, len(config_suite.errors))
                err = config_suite.errors[0]
                self.assertIsInstance(err, configsuite.InvalidTypeError)
                self.assertEqual(("pet", "likeable"), err.key_path)

    def test_list(self):
        playgrounds = [{"name": "superfun", "score": 1}, {"name": "Hell", "score": 99}]

        for end_idx, _ in enumerate(playgrounds):
            raw_config = data.pets.build_config()
            raw_config["playgrounds"] = playgrounds[:end_idx]
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

            self.assertTrue(config_suite.valid, "Errors: %r" % (config_suite.errors,))
            config = config_suite.snapshot
            self.assertEqual(end_idx, len(config.playgrounds))

            for idx, plgr in enumerate(playgrounds[:end_idx]):
                self.assertEqual(plgr["name"], config.playgrounds[idx].name)
                self.assertEqual(plgr["score"], config.playgrounds[idx].score)

    def test_list_errors(self):
        raw_config = data.pets.build_config()
        raw_config["playgrounds"] = [{"name": "faulty grounds"}]
        config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

        self.assertFalse(config_suite.valid)
        self.assertEqual(1, len(config_suite.errors))
        err = config_suite.errors[0]
        self.assertIsInstance(err, configsuite.MissingKeyError)
        self.assertEqual(("playgrounds", 0), err.key_path)

    def test_date(self):
        timestamp = datetime.datetime(2015, 1, 2, 3, 4, 5)
        date = datetime.date(2010, 1, 1)
        types = [timestamp, date, "fdnsjk", "", 0, -10, [], 1, 1.2, {}, None]

        for date in types:
            raw_config = data.pets.build_config()
            raw_config["pet"]["birthday"] = date
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

            if isinstance(date, datetime.date):
                self.assertTrue(config_suite.valid)
                self.assertEqual(date, config_suite.snapshot.pet.birthday)
                self.assertEqual(0, len(config_suite.errors))
            else:
                self.assertFalse(config_suite.valid)
                self.assertEqual(1, len(config_suite.errors))
                err = config_suite.errors[0]
                self.assertIsInstance(err, configsuite.InvalidTypeError)
                self.assertEqual(("pet", "birthday"), err.key_path)

    def test_datetime(self):
        timestamp = datetime.datetime(2015, 1, 2, 3, 4, 5)
        date = datetime.date(2010, 1, 1)
        types = [timestamp, date, "fdnsjk", "", 0, -10, [], 1, 1.2, {}, None]

        for date in types:
            raw_config = data.pets.build_config()
            raw_config["pet"]["timestamp"] = date
            config_suite = configsuite.ConfigSuite(raw_config, data.pets.build_schema())

            if isinstance(date, datetime.datetime):
                self.assertTrue(config_suite.valid)
                self.assertEqual(date, config_suite.snapshot.pet.timestamp)
                self.assertEqual(0, len(config_suite.errors))
            else:
                self.assertFalse(config_suite.valid)
                self.assertEqual(1, len(config_suite.errors))
                err = config_suite.errors[0]
                self.assertIsInstance(err, configsuite.InvalidTypeError)
                self.assertEqual(("pet", "timestamp"), err.key_path)
