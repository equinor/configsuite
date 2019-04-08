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


class TestReadable(unittest.TestCase):
    def test_not_readable(self):
        schema = data.hero.build_schema()

        heroes = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ],
            "villains": {"Phantom Blot": -10},
        }

        villains = {"villains": ["Eobard Thawne", "Lux"]}

        layered_config = configsuite.ConfigSuite(heroes, schema, layers=(villains,))
        self.assertFalse(layered_config.readable)
        self.assertFalse(layered_config.valid)

    def test_readable_not_valid(self):
        schema = data.hero.build_schema()

        heroes = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently"},
            ],
            "villains": {"Phantom Blot": -10},
        }

        villains = {"villains": {"Eobard Thawne": 11, "Lux": 3}}

        layered_config = configsuite.ConfigSuite(heroes, schema, layers=(villains,))
        self.assertTrue(layered_config.readable)
        self.assertFalse(layered_config.valid)

    def test_readable_valid(self):
        schema = data.hero.build_schema()

        heroes = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ],
            "villains": {"Phantom Blot": -10},
        }

        villains = {"villains": {"Eobard Thawne": 11, "Lux": 3}}

        layered_config = configsuite.ConfigSuite(heroes, schema, layers=(villains,))
        self.assertTrue(layered_config.readable)
        self.assertTrue(layered_config.valid)

    def test_readable_missing_container(self):
        schema = data.hero.build_schema()

        heroes = {
            "heroes": [
                {"name": "Batman", "strength": 10},
                {"name": "Flash", "strength": 12},
                {"name": "Dirk Gently", "strength": 7},
            ]
        }
        config = configsuite.ConfigSuite(heroes, schema)
        self.assertTrue(config.readable)
        self.assertFalse(config.valid)
