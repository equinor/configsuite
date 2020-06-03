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
import datetime

import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


def build_schema():
    return {
        MK.Type: types.NamedDict,
        MK.Content: {
            "production_date": {MK.Type: types.DateTime},
            "country": {
                MK.Type: types.String,
                MK.Default: "Norway",
                MK.Required: False,
                MK.AllowNone: True,
            },
            "tire": {
                MK.Type: types.NamedDict,
                MK.Content: {
                    "dimension": {
                        MK.Type: types.Number,
                        MK.Default: 17,
                        MK.Required: False,
                        MK.AllowNone: True,
                    },
                    "rim": {
                        MK.Type: types.String,
                        MK.Default: "green",
                        MK.Required: False,
                        MK.AllowNone: True,
                    },
                },
            },
            "owner": {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: {MK.Type: types.String},
                    MK.Value: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            "name": {MK.Type: types.String},
                            "location": {
                                MK.Type: types.String,
                                MK.Default: "Earth",
                                MK.Required: False,
                                MK.AllowNone: True,
                            },
                        },
                    },
                },
            },
            "incidents": {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            "location": {MK.Type: types.String},
                            "casualties": {
                                MK.Type: types.Number,
                                MK.Default: 0,
                                MK.Required: False,
                                MK.AllowNone: True,
                            },
                        },
                    }
                },
            },
        },
    }


def build_schema_with_validators_and_transformators():
    schema = build_schema()
    dimension_schema = schema[MK.Content]["tire"][MK.Content]["dimension"]
    dimension_schema[MK.Transformation] = inch_to_cm
    dimension_schema[MK.ContextTransformation] = inch_to_cm_context_based

    dimension_schema[MK.ElementValidators] = [is_valid_dimension]
    date_content = {
        MK.Type: types.DateTime,
        MK.Default: datetime.datetime(1999, 1, 1),
        MK.ContextValidators: [is_valid_date],
        MK.Required: False,
        MK.AllowNone: True,
    }

    owner_schema = schema[MK.Content]["owner"]
    owner_schema[MK.Content][MK.Value][MK.Content]["date"] = date_content
    return schema


@configsuite.validator_msg("Is x a valid dimension")
def is_valid_dimension(dimension):
    return 30 <= dimension <= 50


@configsuite.validator_msg("Is x a valid date")
def is_valid_date(date, context):
    return date >= context.production_date


@configsuite.transformation_msg("Convert to cm")
def inch_to_cm(l):
    return l * 2.54


@configsuite.transformation_msg("Convert to cm - ignoring context")
def inch_to_cm_context_based(l, _):
    return l * 2.54


def extract_production_date(snapshot):
    Context = collections.namedtuple("Context", ("production_date",))
    return Context(production_date=snapshot.production_date)


def build_all_default_config():
    return {"production_date": datetime.datetime(2000, 1, 1)}


def build_config():
    return {
        "production_date": datetime.datetime(2000, 1, 1),
        "tire": {"dimension": 15},
        "owner": {
            "first entry": {"name": "Johan", "location": "Svalbard"},
            "second entry": {"name": "Svein"},
        },
        "incidents": [
            {"location": "whereabouts"},
            {"location": "somewhere else", "casualties": 1},
        ],
    }
