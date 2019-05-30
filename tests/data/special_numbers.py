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


@configsuite.validator_msg("Is preference consistence with favourite")
def _preference_favourite_consistency(person, context):
    if person["prefer_normal"]:
        valid_nums = set(context.normal_numbers)
    else:
        valid_nums = set(context.special_numbers)

    favourite_nums = set(person["favourite_numbers"])
    return favourite_nums.issubset(valid_nums)


def extract_context(configuration):
    return configuration


_PERSON_SCHEMA = {
    MK.Type: types.NamedDict,
    MK.ContextValidators: (_preference_favourite_consistency,),
    MK.Content: {
        "prefer_normal": {MK.Type: types.Bool},
        "favourite_numbers": {
            MK.Type: types.List,
            MK.Content: {MK.Item: {MK.Type: types.Integer}},
        },
    },
}


def build_schema():
    return {
        MK.Type: types.NamedDict,
        MK.Content: {
            "special_numbers": {
                MK.Type: types.List,
                MK.Content: {MK.Item: {MK.Type: types.Integer}},
            },
            "normal_numbers": {
                MK.Type: types.List,
                MK.Content: {MK.Item: {MK.Type: types.Integer}},
            },
            "questionnaire": {
                MK.Type: types.List,
                MK.Content: {MK.Item: _PERSON_SCHEMA},
            },
            "mathematicians": {
                MK.Type: types.Dict,
                MK.Content: {MK.Key: {MK.Type: types.String}, MK.Value: _PERSON_SCHEMA},
            },
            "others": {MK.Type: types.NamedDict, MK.Content: {"self": _PERSON_SCHEMA}},
        },
    }


def build_config():
    return {
        "special_numbers": [1, 2, 6, 18],
        "normal_numbers": [3, 4, 5, 7, 15, 31],
        "questionnaire": [
            {"prefer_normal": True, "favourite_numbers": [3, 15]},
            {"prefer_normal": False, "favourite_numbers": [1, 6, 18]},
        ],
        "mathematicians": {
            "Frank P. Ramsey": {
                "prefer_normal": False,
                "favourite_numbers": [1, 2, 6, 18],
            }
        },
        "others": {"self": {"prefer_normal": True, "favourite_numbers": [4, 7, 31]}},
    }
