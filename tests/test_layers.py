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

import configsuite

from . import data


class TestLayers(unittest.TestCase):
    def assertEqualSnapshots(self, first, second):
        self.assertEqual(first.heroes, second.heroes)
        self.assertEqual(sorted(first.villains), sorted(second.villains))

    def test_layers_named_dict_disjoint_push(self):
        schema = data.hero.build_schema()

        heroes = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ]
        }

        villains = {"villains": {"Eobard Thawne": 11, "Lux": 3}}

        hero_config = configsuite.ConfigSuite(heroes, schema)
        self.assertTrue(hero_config.valid)
        hero_villains_config = hero_config.push(villains)
        self.assertTrue(hero_villains_config.valid)

        combined = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ],
            "villains": {"Eobard Thawne": 11, "Lux": 3},
        }
        combined_config = configsuite.ConfigSuite(combined, schema)
        self.assertTrue(combined_config.valid)

        self.assertEqualSnapshots(
            combined_config.snapshot, hero_villains_config.snapshot
        )

    def test_layers_named_dict_intersection_push(self):
        schema = data.hero.build_schema()

        heroes = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ],
            "villains": {"Phantom Blot": -10, "Lux": 2},
        }

        villains = {"villains": {"Eobard Thawne": 11, "Lux": 3}}

        hero_config = configsuite.ConfigSuite(heroes, schema)
        self.assertTrue(hero_config.valid)
        hero_villains_config = hero_config.push(villains)
        self.assertTrue(hero_villains_config.valid)

        combined = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ],
            "villains": {"Phantom Blot": -10, "Eobard Thawne": 11, "Lux": 3},
        }
        combined_config = configsuite.ConfigSuite(combined, schema)
        self.assertTrue(combined_config.valid)

        self.assertEqualSnapshots(
            combined_config.snapshot, hero_villains_config.snapshot
        )

    def test_layers_named_dict_disjoint_init(self):
        schema = data.hero.build_schema()

        heroes = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ]
        }

        villains = {"villains": {"Eobard Thawne": 11, "Lux": 3}}

        layered_config = configsuite.ConfigSuite(heroes, schema, layers=(villains,))
        self.assertTrue(layered_config.valid)

        combined = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ],
            "villains": {"Eobard Thawne": 11, "Lux": 3},
        }
        combined_config = configsuite.ConfigSuite(combined, schema)
        self.assertTrue(combined_config.valid)

        self.assertEqualSnapshots(combined_config.snapshot, layered_config.snapshot)

    def test_layers_named_dict_intersection_init(self):
        schema = data.hero.build_schema()

        heroes = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ],
            "villains": {"Phantom Blot": -10, "Lux": 3},
        }

        layers = ({"villains": {"Eobard Thawne": 11}}, {"villains": {"Lux": 5}})

        layered_config = configsuite.ConfigSuite(heroes, schema, layers=layers)
        self.assertTrue(layered_config.valid)

        combined = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ],
            "villains": {"Eobard Thawne": 11, "Lux": 3, "Phantom Blot": -10},
        }
        combined_config = configsuite.ConfigSuite(combined, schema)
        self.assertTrue(combined_config.valid)

        self.assertEqualSnapshots(combined_config.snapshot, layered_config.snapshot)

    def test_multi_layers_dict_intersection(self):
        schema = data.hero.build_schema()

        bottom_layer = {
            "heroes": [],
            "villains": {"Phantom Blot": 0, "Lux": 0, "Joker": 0},
        }
        middle_layer = {"villains": {"Phantom Blot": 1, "Lux": 1}}
        top_layer = {"villains": {"Phantom Blot": 2}}

        layered_config = configsuite.ConfigSuite(
            top_layer, schema, layers=(bottom_layer, middle_layer)
        )
        self.assertTrue(layered_config.valid)

        villains = dict(layered_config.snapshot.villains)
        self.assertEqual(
            sorted(["Phantom Blot", "Lux", "Joker"]), sorted(villains.keys())
        )
        self.assertEqual(0, villains["Joker"])
        self.assertEqual(1, villains["Lux"])
        self.assertEqual(2, villains["Phantom Blot"])

    def test_layers_list_init(self):
        schema = data.hero.build_schema()

        heroes = {
            "heroes": [{"name": "Batman", "strength": 10}],
            "villains": {"Phantom Blot": -10, "Lux": 3, "Eobard Thawne": 11},
        }

        layers = (
            {"heroes": [{"name": "Flash", "strength": 12}]},
            {"heroes": [{"name": "Dirk Gently", "strength": 7}]},
        )

        layered_config = configsuite.ConfigSuite(heroes, schema, layers=layers)
        self.assertTrue(layered_config.valid)

        combined = {
            "heroes": [
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
                {"name": "Batman", "strength": 10},
            ],
            "villains": {"Eobard Thawne": 11, "Lux": 3, "Phantom Blot": -10},
        }
        combined_config = configsuite.ConfigSuite(combined, schema)
        self.assertTrue(combined_config.valid)

        self.assertEqualSnapshots(combined_config.snapshot, layered_config.snapshot)

    def test_invalid_layer(self):
        schema = data.hero.build_schema()

        dummy_layer = {
            "heroes": [{"name": "Batman", "strength": 10}],
            "villains": {"The joker": "there is not such thing as evil"},
        }

        real_layer = {
            "heroes": [{"name": "Batman", "strength": 10}],
            "villains": {"The Joker": 9},
        }

        layered_config = configsuite.ConfigSuite(
            real_layer, schema, layers=(dummy_layer,)
        )
        self.assertTrue(layered_config.readable)
        self.assertFalse(layered_config.valid)

    def test_invalid_layer_inside_list(self):
        schema = data.hero.build_schema()

        dummy_layer = {"heroes": [{"name": "Batman"}]}

        real_layer = {
            "heroes": [{"name": "Batman", "strength": 10}],
            "villains": {"The Joker": 9},
        }

        layered_config = configsuite.ConfigSuite(
            real_layer, schema, layers=(dummy_layer,)
        )
        self.assertTrue(layered_config.readable)
        self.assertFalse(layered_config.valid)
        self.assertTrue(len(layered_config.errors) > 0)

        combined = {
            "heroes": [{"name": "Batman"}, {"name": "Batman", "strength": 10}],
            "villains": {"The Joker": 9},
        }

        combined_config = configsuite.ConfigSuite(combined, schema)
        self.assertTrue(combined_config.readable)
        self.assertFalse(combined_config.valid)

        self.assertEqualSnapshots(combined_config.snapshot, layered_config.snapshot)
