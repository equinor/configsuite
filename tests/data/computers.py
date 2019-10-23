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
            "OS": {MK.Type: types.String},
            "components": {
                MK.Type: types.NamedDict,
                MK.Content: {"cpu": {MK.Type: types.String}},
            },
            "externals": {
                MK.Type: types.List,
                MK.Content: {MK.Item: {MK.Type: types.String}},
            },
            "software": {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: {MK.Type: types.String},
                    MK.Value: {MK.Type: types.String},
                },
            },
        },
    }


def build_config():
    return {
        "OS": "Linux",
        "components": {"cpu": "amd"},
        "externals": ["Floppy", "Punch cards"],
        "software": {"python": "1.3", "ERT": "3.0"},
    }
