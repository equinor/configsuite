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


import collections
import copy
import unittest

import configsuite
from configsuite import MetaKeys as MK
from configsuite import transformation_msg as trans_msg

from .data import templating
from .data import favourite_numbers
from .data import hero


@configsuite.transformation_msg("Put numbers under types in sorted order")
def _sort_favourites(nums_dict):
    nums_dict = copy.deepcopy(nums_dict)
    num_names = ("favourite_uint4", "favourite_uint8", "favourite_int")

    nums = [nums_dict.get(name) for name in num_names]
    neg, non_neg = [x for x in nums if x < 0], [x for x in nums if x >= 0]
    nums = sorted(neg, key=abs) + sorted(non_neg, key=abs)
    nums = collections.deque(nums)

    for name in num_names:
        if name in nums_dict:
            nums_dict[name] = nums.popleft()

    return nums_dict


class TestTransformations(unittest.TestCase):
    def test_transformation_valid(self):
        raw_config = templating.build_config_no_definitions()
        suite = configsuite.ConfigSuite(
            raw_config, templating.build_schema_no_definitions()
        )
        self.assertTrue(suite.valid)
        self.assertEqual(templating.template_results_no_definitions(), suite.snapshot)

    def test_transformation_invalid_value(self):
        raw_config = templating.build_config_no_definitions()
        raw_config.append(14)
        suite = configsuite.ConfigSuite(
            raw_config, templating.build_schema_no_definitions()
        )
        self.assertFalse(suite.valid)

        self.assertEqual(1, len(suite.errors))
        err = suite.errors[0]
        self.assertIsInstance(err, configsuite.InvalidTypeError)

    def test_transformation_exception(self):
        raw_config = templating.build_config_no_definitions()

        schema = templating.build_schema_no_definitions()
        temp_schema = schema[MK.Content][MK.Item]
        _render = temp_schema[MK.Transformation]
        transformation_msg = "Renders Jinja template until the end"
        error_msg = "Did not expect to reach the end!"

        @configsuite.transformation_msg(transformation_msg)
        def _no_end_render(elem):
            if elem == "The end.":
                raise ValueError(error_msg)
            return _render(elem)

        temp_schema[MK.Transformation] = _no_end_render

        suite = configsuite.ConfigSuite(raw_config, schema)
        self.assertFalse(suite.valid)

        self.assertEqual(1, len(suite.errors))
        err = suite.errors[0]
        self.assertIsInstance(err, configsuite.TransformationError)
        error_fmt = "'{}' failed on input '{}' with error '{}'"
        expected_error = error_fmt.format(transformation_msg, "The end.", error_msg)
        self.assertEqual(expected_error, err.msg)
        self.assertEqual((3,), err.key_path)

    def test_transformation_multi_layer(self):
        raw_config = templating.build_config_no_definitions()

        schema = templating.build_schema_no_definitions()
        schema[MK.Transformation] = trans_msg("Max length 3")(lambda l: l[-3:])

        top_layer = ("To be continued.", "... another day.")

        suite = configsuite.ConfigSuite(top_layer, schema)
        self.assertTrue(suite.valid)
        self.assertEqual(top_layer, suite.snapshot)

        layer_suite = configsuite.ConfigSuite(top_layer, schema, layers=(raw_config,))
        self.assertTrue(layer_suite.valid)
        self.assertEqual(
            templating.template_results_no_definitions()[-1:] + top_layer,
            layer_suite.snapshot,
        )

    def test_transformation_list(self):
        raw_config = templating.build_config_no_definitions()

        schema = templating.build_schema_no_definitions()
        schema[MK.Transformation] = trans_msg("Max length 3")(lambda l: l[-3:])

        suite = configsuite.ConfigSuite(raw_config, schema)
        self.assertTrue(suite.valid)
        self.assertEqual(
            templating.template_results_no_definitions()[-3:], suite.snapshot
        )

    def test_transformation_non_readable_results(self):
        raw_config = templating.build_config_no_definitions()

        @configsuite.transformation_msg("Deforming elements")
        def _deformer(elem):
            return {"unexpected_nesting": elem}

        schema = templating.build_schema_no_definitions()
        schema[MK.Transformation] = _deformer

        suite = configsuite.ConfigSuite(raw_config, schema)
        self.assertFalse(suite.readable, suite.errors)

    def test_transformation_nameddict(self):
        schema = favourite_numbers.build_schema()
        schema[MK.Transformation] = _sort_favourites

        raw_config = {
            "favourite_uint4": 1024,
            "favourite_uint8": 7,
            "favourite_int": 42,
        }
        suite = configsuite.ConfigSuite(raw_config, schema)
        self.assertTrue(suite.valid, suite.errors)
        self.assertEqual(7, suite.snapshot.favourite_uint4)
        self.assertEqual(42, suite.snapshot.favourite_uint8)
        self.assertEqual(1024, suite.snapshot.favourite_int)

    def test_transformation_prior_to_validation(self):
        schema = favourite_numbers.build_schema()
        schema[MK.Transformation] = _sort_favourites

        raw_config = {
            "favourite_uint4": 1024,
            "favourite_uint8": 2 ** 4,
            "favourite_int": 42,
        }
        suite = configsuite.ConfigSuite(raw_config, schema)
        self.assertFalse(suite.valid)

    def test_transformation_dict(self):
        @configsuite.transformation_msg("Remove he who must not be named")
        def _remove_unspeakable_names(villains):
            villains = copy.deepcopy(villains)
            if "Voldemort" in villains:
                villains.pop("Voldemort")
            return villains

        schema = hero.build_schema()
        schema[MK.Content]["villains"][MK.Transformation] = _remove_unspeakable_names

        villains = {
            "heroes": [{"name": "Lucky Luke", "strength": 8}],
            "villains": {"The Joker": 7, "Voldemort": 10},
        }
        suite = configsuite.ConfigSuite(villains, schema)
        self.assertTrue(suite.valid, suite.errors)
        self.assertEqual((("The Joker", 7),), suite.snapshot.villains)
