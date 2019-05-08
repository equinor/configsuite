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
import jinja2

import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


_VARIABLES = {"color": "blue", "secret_number": 42, "animal": "cow"}
_VAR_START = "<"
_VAR_END = ">"


def _render_variables(variables, jinja_env):
    variables = copy.deepcopy(variables)
    for _ in enumerate(variables):
        rendered_values = []
        for key, value in variables.items():
            try:
                variables[key] = jinja_env.from_string(value).render(variables)
                rendered_values.append(variables[key])
            except TypeError:
                continue

    if any([_VAR_START in val for val in rendered_values]):
        raise ValueError("Circular dependencies")

    return variables


def _render(template, definitions=None):
    if definitions is None:
        definitions = {}

    variables = copy.deepcopy(_VARIABLES)
    variables.update(definitions)
    jinja_env = jinja2.Environment(
        variable_start_string=_VAR_START, variable_end_string=_VAR_END, autoescape=True
    )

    try:
        variables = _render_variables(variables, jinja_env)
        jinja_template = jinja_env.from_string(template)
        return jinja_template.render(variables)
    except TypeError:
        return template


@configsuite.transformation_msg("Renders Jinja template using definitions")
def _context_render(elem, context):
    return _render(elem, definitions=context.definitions)


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


def extract_templating_context(configuration):
    Context = collections.namedtuple("TemplatingContext", ["definitions"])
    definitions = {key: value for (key, value) in configuration.definitions}
    return Context(definitions=definitions)


def build_schema_with_definitions():
    return {
        MK.Type: types.NamedDict,
        MK.Content: {
            "definitions": {
                MK.Type: types.Dict,
                MK.Required: False,
                MK.Content: {
                    MK.Key: {MK.Type: types.String},
                    MK.Value: {MK.Type: types.String},
                },
            },
            "templates": {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.String,
                        MK.ContextTransformation: _context_render,
                    }
                },
            },
        },
    }


def build_config_with_definitions():
    return {
        "definitions": {"animal": "pig", "habitants": "<animal>, cow and monkey"},
        "templates": [
            "This is a story about a <animal>.",
            "It had a <color> house.",
            "And the password to enter was <secret_number>.",
            "If you entered the house you would meet: <habitants>",
            "The end.",
        ],
    }


def template_results_with_definitions():
    return (
        "This is a story about a pig.",
        "It had a blue house.",
        "And the password to enter was 42.",
        "If you entered the house you would meet: pig, cow and monkey",
        "The end.",
    )
