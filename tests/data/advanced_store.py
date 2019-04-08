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


from configsuite import MetaKeys as MK
from configsuite import types


def build_schema():
    return {
        MK.Type: types.NamedDict,
        MK.Content: {
            "employees": {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: {MK.Type: types.String},
                    MK.Value: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            "salary": {MK.Type: types.Number},
                            "shift_leader": {MK.Type: types.String},
                        },
                    },
                },
            },
            "prices": {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: {MK.Type: types.String},
                    MK.Value: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            "kilo": {MK.Type: types.Number},
                            "gram": {MK.Type: types.Number},
                            "unit": {MK.Type: types.Number, MK.Required: False},
                        },
                    },
                },
            },
        },
    }


def build_config():
    return {
        "employees": {
            "Are": {"salary": 4, "shift_leader": "Jonny"},
            "Knut": {"salary": 1, "shift_leader": "Are"},
        },
        "prices": {
            "flour": {"kilo": 4.5, "gram": 30},
            "pig": {"unit": 100, "kilo": 20, "gram": 3},
        },
    }
