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

import copy
import re
import six

import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


_META_SCHEMA = {
    MK.Type: types.NamedDict,
    MK.Content: {
        MK.Type: {MK.Type: types.Type},
        MK.Required: {MK.Type: types.Bool, MK.Required: False},
        MK.Description: {MK.Type: types.String, MK.Required: False},
        MK.ElementValidators: {
            MK.Type: types.List,
            MK.Required: False,
            MK.Content: {MK.Item: {MK.Type: types.Callable}},
        },
    },
}


def assert_valid_schema(schema):
    _assert_valid_schema_level(schema)

    level_type = schema[MK.Type]
    if isinstance(level_type, types.BasicType):
        return
    elif level_type == types.NamedDict:
        _assert_valid_named_dict_schema(schema)
    elif level_type == types.List:
        _assert_valid_list_schema(schema)
    elif level_type == types.Dict:
        _assert_valid_dict_schema(schema)
    else:
        raise AssertionError("Unknown base container: {}".format(schema))


def _assert_valid_schema_level(schema):
    level_schema = copy.deepcopy(schema)
    if MK.Content in level_schema:
        level_schema.pop(MK.Content)

    level_validator = configsuite.Validator(_META_SCHEMA)
    result = level_validator.validate(level_schema)

    if not result.valid:
        for error in result.errors:
            gen_err_msg = lambda error: "{} at {}".format(error.msg, error.key_path)

            if isinstance(error, configsuite.MissingKeyError):
                raise KeyError(gen_err_msg(error))
            elif isinstance(error, configsuite.UnknownKeyError):
                raise KeyError(gen_err_msg(error))
            elif isinstance(error, configsuite.InvalidTypeError):
                raise TypeError(gen_err_msg(error))
            elif isinstance(error, configsuite.InvalidValueError):
                raise ValueError(gen_err_msg(error))
            else:
                raise Exception("Unknown validation error: {}".format(error))


def _assert_dict_key(key):
    if not isinstance(key, six.string_types):
        raise KeyError(
            "Expected all {} keys to be strings, found: {}"
            "".format(types.NamedDict.name, type(key))
        )

    key_regex = "^[a-zA-Z_][a-zA-Z0-9_]*$"
    if not re.match(key_regex, key):
        raise KeyError(
            'Expected all {} keys to match: "{}", found: {}'
            "".format(types.NamedDict.name, key_regex, key)
        )


def _assert_valid_named_dict_schema(schema):
    if MK.Content not in schema:
        err_msg = "{} schema has no {}: {}".format(
            types.NamedDict.name, MK.Content, schema
        )
        raise KeyError(err_msg)

    content = schema[MK.Content]
    if not isinstance(content, dict):
        err_msg = "Expected {} to be a dict, was {}".format(MK.Content, type(content))
        raise ValueError(err_msg)

    for key in content.keys():
        _assert_dict_key(key)

    for value in content.values():
        assert_valid_schema(value)


def _assert_valid_list_schema(schema):
    if MK.Content not in schema:
        err_msg = "{} schema has no {}: {}".format(types.List.name, MK.Content, schema)
        raise KeyError(err_msg)

    content = schema[MK.Content]
    if not isinstance(content, dict):
        err_msg = "Expected {} to be a dict, was {}".format(MK.Content, type(content))
        raise ValueError(err_msg)

    if tuple(content.keys()) != (MK.Item,):
        err_msg = (
            "Expected {} of a {} to contain exactly one key. "
            ", namely {}, was {}."
            "".format(MK.Content, types.List.name, MK.Item, content.keys())
        )
        raise KeyError(err_msg)

    assert_valid_schema(content[MK.Item])


def _assert_valid_dict_schema(schema):
    if MK.Content not in schema:
        err_msg = "{} schema has no {}: {}".format(types.Dict.name, MK.Content, schema)
        raise KeyError(err_msg)

    content = schema[MK.Content]
    if not isinstance(content, dict):
        err_msg = "Expected {} to be a dict, was {}".format(MK.Content, type(content))
        raise ValueError(err_msg)

    expected_keys = (MK.Key, MK.Value)
    if len(content.keys()) != len(expected_keys) or set(content.keys()) != set(
        expected_keys
    ):
        err_msg = "Expected {} of a {} to contain the keys {}, was {}." "".format(
            MK.Content, types.Dict.name, (MK.Key, MK.Value), content.keys()
        )
        raise KeyError(err_msg)

    assert_valid_schema(content[MK.Key])
    assert_valid_schema(content[MK.Value])
