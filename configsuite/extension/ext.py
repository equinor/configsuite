"""Copyright 2018 Equinor ASA and The Netherlands Organisation for
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

import os
import importlib
import inspect

from docutils.parsers.rst import Directive
from docutils.parsers.rst.directives import unchanged_required
from docutils import nodes

import configsuite
from configsuite import MetaKeys as MK
from configsuite import types
from configsuite.extension.ext_nodes import (
    visit_children,
    visit_container,
    visit_content,
    visit_header,
    depart_children,
    depart_container,
    depart_content,
    depart_header,
    cs_children,
    cs_container,
    cs_content,
    cs_header,
)

BASIC_EXAMPLE = {
    "string": "default",
    "integer": "0",
    "number": "0.0",
    "bool": "True",
    "date": "01.01.1999",
    "datetime": "01.01.1999",
}


def scb_static_path(app):
    static_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "_static"))
    app.config.html_static_path.append(static_path)


def generate_section_content(schema, title):
    section_content = cs_content(
        classes=["cs_content"], ids=["cs_{}_content".format(title)]
    )

    section_content += nodes.paragraph(text=schema.get(MK.Description, ""))

    for config_key in [MK.ElementValidators, MK.ContextValidators]:
        element_nodes = [
            nodes.paragraph(text=validator.msg)
            for validator in schema.get(config_key, [])
        ]
        section_content.extend(element_nodes)

    for config_key in [
        MK.LayerTransformation,
        MK.ContextTransformation,
        MK.Transformation,
    ]:
        if config_key in schema:
            section_content += nodes.paragraph(text=schema.get(config_key).msg)

    return section_content


def generate_section_children(schema, title):
    section_children = cs_children(
        classes=["cs_children"], ids=["cs_{}_children".format(title)]
    )

    if schema[MK.Type] == types.NamedDict:
        example = dict()
        for key, value in schema[MK.Content].items():
            generate(value, section_children, key)

        for child in section_children.children:
            example[child["parent"]] = child["example"]

    elif schema[MK.Type] == types.List:
        generate(
            schema[MK.Content][MK.Item], section_children, parent_title="List Item"
        )
        example = [section_children.children[0]["example"]]

    elif schema[MK.Type] == types.Dict:
        example = dict()
        generate(schema[MK.Content][MK.Key], section_children, parent_title="Key")
        generate(schema[MK.Content][MK.Value], section_children, parent_title="Value")
        example[section_children.children[0]["example"]] = section_children.children[1][
            "example"
        ]

    elif isinstance(schema[MK.Type], types.BasicType):
        example = "{}".format(BASIC_EXAMPLE.get(schema[MK.Type].name, "undefined"))
        section_children += nodes.paragraph(
            text=":type: {_type}".format(_type=schema[MK.Type].name)
        )

    else:
        err_msg = "Unexpected type ({}) in schema while generating documentation."
        raise TypeError(err_msg.format(schema[MK.Type]))

    return section_children


def generate(schema, parent_section, parent_title=""):
    title = schema.get(MK.Description, "default_title")[:15]
    title = title.lower()
    title = title.replace(" ", "_")
    example = None

    section = cs_container(
        classes=["cs_container"], ids=["cs_{}_container".format(title)]
    )

    section += cs_header(classes=["cs_header"], text=parent_title)

    section_content = generate_section_content(schema, title)
    section_children = generate_section_children(schema, title)

    section_content += section_children

    section += section_content
    section["example"] = example
    section["parent"] = parent_title

    parent_section += section


class ConfigsuiteDocDirective(Directive):
    has_content = True
    option_spec = {"module": unchanged_required}

    def run(self):
        if "module" not in self.options:
            raise self.error("Required :module: argument missing")

        schema_function_string = self.options.get("module")

        if "." not in schema_function_string:
            raise self.error(
                "Configsuite :module: has invalid format. "
                + "Expected 'module.function', got {}".format(schema_function_string)
            )

        module_str, func_str = schema_function_string.rsplit(".", 1)

        try:
            module = importlib.import_module(module_str)
        except (ImportError) as e:
            raise self.error(str(e))

        try:
            schema_func = getattr(module, func_str)
        except (AttributeError) as e:
            raise self.error(str(e))

        if not callable(schema_func):
            err_msg = (
                "The module.function given at Configsuite :module: "
                + "must provide a callable function, the '{func_name}' was not"
            )
            raise self.error(err_msg.format(func_name=func_str))

        insp = inspect.getfullargspec(schema_func)
        if len(insp.args) != 0:
            err_msg = (
                "The module.function given at Configsuite :module: "
                + "can not require any arguments, the '{func_name}' "
                + "takes {num_args} argument(s)"
            )
            raise self.error(
                err_msg.format(func_name=func_str, num_args=len(insp.args))
            )

        schema = schema_func()
        if not isinstance(schema, dict):
            err_msg = (
                "The module.function given at Configsuite :module: "
                + "is expected to return a dictionary object\n"
                + "The function '{func_name}' returned a {return_type}"
            )
            raise self.error(
                err_msg.format(func_name=func_str, return_type=type(schema))
            )

        section = cs_container(classes=["cs_top_container"])
        generate(schema, section)
        return [section]


def setup(app):
    # Add our static path
    app.connect("builder-inited", scb_static_path)

    # Add relevant code to headers
    app.add_css_file("configsuite_ext.css")
    app.add_js_file("configsuite_ext.js")

    app.add_node(
        cs_container, html=(visit_container, depart_container),
    )

    app.add_node(
        cs_header, html=(visit_header, depart_header),
    )

    app.add_node(
        cs_content, html=(visit_content, depart_content),
    )

    app.add_node(
        cs_children, html=(visit_children, depart_children),
    )

    app.add_directive("configsuite", ConfigsuiteDocDirective)

    return {"version": configsuite.__version__}
