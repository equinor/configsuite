"""Copyright 2019 Equinor ASA and The Netherlands Organisation for
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

import unittest
import datetime

import configsuite
from configsuite import MetaKeys as MK
from configsuite import types
from .data import car


class TestDefaultValues(unittest.TestCase):
    def test_untouched_basic_types(self):
        raw_config = car.build_all_default_config()
        car_schema = car.build_schema()
        car_schema[MK.Content]["tire"][MK.Content]["rim"].pop(MK.Default)

        config_suite = configsuite.ConfigSuite(raw_config, car_schema)
        self.assertTrue(config_suite.valid)

        self.assertEqual(17, config_suite.snapshot.tire.dimension)
        self.assertEqual(None, config_suite.snapshot.tire.rim)

    def test_empty_named_dict_default_values(self):
        raw_config = car.build_all_default_config()
        car_schema = car.build_schema()
        config_suite = configsuite.ConfigSuite(raw_config, car_schema)

        self.assertTrue(config_suite.valid)

        self.assertEqual(17, config_suite.snapshot.tire.dimension)
        self.assertEqual("green", config_suite.snapshot.tire.rim)

    def test_default_values(self):
        raw_config = car.build_config()
        car_schema = car.build_schema()
        config_suite = configsuite.ConfigSuite(raw_config, car_schema)
        self.assertTrue(config_suite.valid)

        # Top level basic type within named dict
        self.assertEqual("Norway", config_suite.snapshot.country)

        # Named dict within named dict
        self.assertEqual(15, config_suite.snapshot.tire.dimension)
        self.assertEqual("green", config_suite.snapshot.tire.rim)

        # Named dict within dict
        owner_data = (("Johan", "Svalbard"), ("Svein", "Earth"))
        self.assertEqual(len(owner_data), len(config_suite.snapshot.owner))
        for (expected_name, expected_location), config_owner in zip(
            owner_data, sorted(config_suite.snapshot.owner)
        ):
            self.assertEqual(expected_name, config_owner.value.name)
            self.assertEqual(expected_location, config_owner.value.location)

        # Named dict within list
        incidents_data = (("whereabouts", 0), ("somewhere else", 1))
        self.assertEqual(len(incidents_data), len(config_suite.snapshot.incidents))
        for (expected_location, expected_casualties), config_owner in zip(
            incidents_data, sorted(config_suite.snapshot.incidents)
        ):
            self.assertEqual(expected_location, config_owner.location)
            self.assertEqual(expected_casualties, config_owner.casualties)

    def test_element_transformations_applied(self):
        raw_config = car.build_all_default_config()
        car_schema = car.build_schema()
        tire_schema = car_schema[MK.Content]["tire"]
        tire_schema[MK.Content]["dimension"][MK.Transformation] = car.inch_to_cm
        config_suite = configsuite.ConfigSuite(raw_config, car_schema)

        self.assertTrue(config_suite.valid)
        self.assertAlmostEqual(17 * 2.54, config_suite.snapshot.tire.dimension)

    def test_context_transformation_applied(self):
        raw_config = car.build_all_default_config()
        car_schema = car.build_schema()
        tire_schema = car_schema[MK.Content]["tire"]
        tire_schema[MK.Content]["dimension"][
            MK.ContextTransformation
        ] = car.inch_to_cm_context_based

        config_suite = configsuite.ConfigSuite(
            raw_config, car_schema, extract_validation_context=lambda snapshot: None
        )

        self.assertTrue(config_suite.valid)
        self.assertAlmostEqual(17 * 2.54, config_suite.snapshot.tire.dimension)

    def test_element_validators_applied(self):
        raw_config = car.build_all_default_config()
        car_schema = car.build_schema()
        tire_content = car_schema[MK.Content]["tire"][MK.Content]
        tire_content["dimension"][MK.ElementValidators] = [car.is_valid_dimension]

        config_suite = configsuite.ConfigSuite(raw_config, car_schema)

        self.assertFalse(config_suite.valid)
        for err in config_suite.errors:
            self.assertTrue(
                isinstance(err, configsuite.validation_errors.InvalidValueError)
            )
            self.assertTrue(err.msg.startswith("Is x a valid dimension"))

    def test_context_validators_applied(self):
        raw_config = car.build_config()
        car_schema = car.build_schema()

        date_content = {
            MK.Type: types.DateTime,
            MK.Default: datetime.datetime(1999, 1, 1),
            MK.ContextValidators: [car.is_valid_date],
            MK.Required: False,
            MK.AllowNone: True,
        }

        owner_schema = car_schema[MK.Content]["owner"]
        owner_schema[MK.Content][MK.Value][MK.Content]["date"] = date_content

        config_suite = configsuite.ConfigSuite(
            raw_config,
            car_schema,
            extract_validation_context=car.extract_production_date,
        )

        self.assertFalse(config_suite.valid)
        for err in config_suite.errors:
            self.assertTrue(
                isinstance(err, configsuite.validation_errors.InvalidValueError)
            )
            self.assertTrue(err.msg.startswith("Is x a valid date"))

    def test_not_allow_default_for_list(self):
        raw_config = car.build_all_default_config()

        car_schema = car.build_schema()
        schema_value_content = {
            MK.Default: ["default value"],
            MK.Type: types.List,
            MK.Content: {MK.Item: {MK.Type: types.String}},
        }
        car_schema[MK.Content]["incidents"] = schema_value_content

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite(raw_config, car_schema)
        self.assertTrue(
            str(error_context.exception).startswith("Default can only be used")
        )

    def test_not_allow_defaults_for_list_items(self):
        raw_config = car.build_all_default_config()

        car_schema = car.build_schema()
        schema_value_content = {
            MK.Type: types.List,
            MK.Content: {MK.Item: {MK.Type: types.String, MK.Default: "default value"}},
        }
        car_schema[MK.Content]["incidents"] = schema_value_content

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite(raw_config, car_schema)
        self.assertTrue(str(error_context.exception).startswith("Default value is"))

    def test_not_allow_default_for_dict(self):
        raw_config = car.build_all_default_config()

        car_schema = car.build_schema()
        schema_value_content = {
            MK.Default: {"key": 10},
            MK.Type: types.Dict,
            MK.Content: {
                MK.Key: {MK.Type: types.String},
                MK.Value: {MK.Type: types.Number, MK.Default: 10},
            },
        }
        car_schema[MK.Content]["owner"] = schema_value_content

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite(raw_config, car_schema)
        self.assertTrue(
            str(error_context.exception).startswith("Default can only be used")
        )

    def test_not_allow_defaults_for_dict_keys(self):
        raw_config = car.build_all_default_config()

        car_schema = car.build_schema()
        schema_value_content = {
            MK.Type: types.Dict,
            MK.Content: {
                MK.Key: {
                    MK.Type: types.String,
                    MK.Default: "default value",
                    MK.Required: False,
                    MK.AllowNone: True,
                },
                MK.Value: {MK.Type: types.Number},
            },
        }
        car_schema[MK.Content]["owner"] = schema_value_content

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite(raw_config, car_schema)
        self.assertTrue(str(error_context.exception).startswith("Default value is"))

    def test_not_allow_defaults_for_dict_values(self):
        raw_config = car.build_all_default_config()

        car_schema = car.build_schema()
        schema_value_content = {
            MK.Type: types.Dict,
            MK.Content: {
                MK.Key: {MK.Type: types.String},
                MK.Value: {
                    MK.Type: types.Number,
                    MK.Default: 10,
                    MK.Required: False,
                    MK.AllowNone: True,
                },
            },
        }
        car_schema[MK.Content]["owner"] = schema_value_content

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite(raw_config, car_schema)
        self.assertTrue(str(error_context.exception).startswith("Default value is"))

    def test_not_allow_default_for_named_dict(self):
        raw_config = car.build_all_default_config()

        schema_value_content = {
            MK.Type: types.NamedDict,
            MK.Default: {"profile": 200, "width": 20},
            MK.Content: {
                "profile": {MK.Type: types.Number},
                "width": {MK.Type: types.Number},
            },
        }
        car_schema = car.build_schema()
        car_schema[MK.Content]["tire"][MK.Content]["rim"] = schema_value_content

        with self.assertRaises(ValueError) as error_context:
            configsuite.ConfigSuite(raw_config, car_schema)
        self.assertTrue(
            str(error_context.exception).startswith("Default can only be used")
        )
