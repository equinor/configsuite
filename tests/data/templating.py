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


import copy
import jinja2

import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


_VARIABLES = {"color": "blue", "secret_number": 42, "animal": "cow"}


def _render(template, definitions=None):
    if definitions is None:
        definitions = {}

    variables = copy.deepcopy(_VARIABLES)
    variables.update(definitions)
    jinja_env = jinja2.Environment(variable_start_string="<", variable_end_string=">")
    try:
        jinja_template = jinja_env.from_string(template)
    except TypeError:
        return template

    return jinja_template.render(variables)


@configsuite.transformation_msg("Renders Jinja template")
def _render_no_vars(elem):
    return _render(elem)


def build_schema_no_definitions():
    return {
        MK.Type: types.List,
        MK.Content: {
            MK.Item: {MK.Type: types.String, MK.Transformation: _render_no_vars}
        },
    }


def build_config_no_definitions():
    return [
        "This is a story about a <animal>.",
        "It had a <color> house.",
        "And the password to enter was <secret_number>.",
        "The end.",
    ]


def template_results_no_definitions():
    return (
        "This is a story about a cow.",
        "It had a blue house.",
        "And the password to enter was 42.",
        "The end.",
    )
