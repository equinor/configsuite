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


import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


@configsuite.validator_msg("Name should not be empty")
def _non_empty_name(elem):
    return len(elem) > 0


def build_schema():
    return {
        MK.Type: types.List,
        MK.Content: {
            MK.Item: {
                MK.Type: types.NamedDict,
                MK.Content: {
                    "color": {MK.Type: types.String},
                    "name": {
                        MK.Type: types.String,
                        MK.ElementValidators: (_non_empty_name,),
                    },
                    "price": {MK.Type: types.Number},
                    "story": {MK.Type: types.String, MK.Required: False},
                },
            }
        },
    }


def build_config():
    return [
        {"color": "green", "name": "Hulk", "price": 0.1},
        {"color": "red", "name": "crazy spicy", "price": 1},
    ]


def build_story_config():
    return [
        {
            "color": "green",
            "name": "Hulk",
            "price": 0.1,
            "story": "Created from the remains of the Hulk",
        },
        {"color": "red", "name": "crazy spicy", "price": 1},
    ]
