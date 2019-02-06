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
import subprocess
import os

from configsuite import MetaKeys as MK
from configsuite import types


def generate(schema, level=0):
    indent = level * 4 * " "
    element_sep = "\n\n"

    docs = [indent + schema.get(MK.Description, "")]

    elem_vals = schema.get(MK.ElementValidators, ())
    if len(elem_vals) > 0:
        try:
            docs += [
                indent
                + ":requirement: {}".format(
                    ", ".join([elem_val.msg for elem_val in elem_vals])
                )
            ]
        except AttributeError:
            raise Exception(elem_vals[0].__name__)

    if schema[MK.Type] == types.NamedDict:
        req_child_marker = lambda key: (
            "*" if schema[MK.Content][key].get(MK.Required, True) else ""
        )

        docs += [
            "\n".join(
                (
                    indent
                    + "**{key}{req}:**".format(key=key, req=req_child_marker(key)),
                    generate(value, level=level + 1),
                )
            )
            for key, value in schema[MK.Content].items()
        ]
    elif schema[MK.Type] == types.List:
        docs += [
            "\n".join(
                [
                    indent + "**<list_item>:**",
                    generate(schema[MK.Content][MK.Item], level=level + 2),
                ]
            )
        ]
    elif schema[MK.Type] == types.Dict:
        docs += [
            "\n".join(
                [
                    indent + "**<key>:**",
                    generate(schema[MK.Content][MK.Key], level=level + 2),
                    indent + "**<value>:**",
                    generate(schema[MK.Content][MK.Value], level=level + 2),
                ]
            )
        ]
    elif isinstance(schema[MK.Type], types.BasicType):
        docs += [indent + ":type: {_type}".format(_type=schema[MK.Type].name)]
    else:
        err_msg = "Unexpected type ({}) in schema while generating documentation."
        raise TypeError(err_msg.format(schema[MK.Type]))

    return element_sep.join(docs)
