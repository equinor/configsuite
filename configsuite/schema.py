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
import warnings

import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


@types.validator_msg("Is x any type")
def _is_anytype(_):
    return True


_Anytype = types.BasicType("_anytype", _is_anytype)


@configsuite.validator_msg("AllowNone can only be used for BasicType")
def _check_allownone_type(schema_level):
    if MK.AllowNone in schema_level:
        return isinstance(schema_level[MK.Type], types.BasicType)
    return True


@configsuite.validator_msg("Required can only be used for BasicType")
def _check_required_type(schema_level):
    if MK.Required in schema_level:
        return isinstance(schema_level[MK.Type], types.BasicType)
    return True


@configsuite.validator_msg(
    "A schema element can be required if and only if the schema element does "
    "not allow None as a value and defaults to None"
)
def _check_allownone_required(schema_level):
    if not isinstance(schema_level[MK.Type], types.BasicType):
        return True

    is_required = schema_level.get(MK.Required, True)
    allow_none = schema_level.get(MK.AllowNone, False)
    has_non_none_default = schema_level.get(MK.Default) is not None

    return is_required != allow_none or has_non_none_default


@configsuite.validator_msg("Default can only be used for BasicType")
def _check_default_type(schema_level):
    if MK.Default in schema_level:
        return isinstance(schema_level[MK.Type], types.BasicType)
    return True


@configsuite.validator_msg("Required can not have Default")
def _check_required_not_default(schema_level):
    if schema_level.get(MK.Required, True):
        return MK.Default not in schema_level
    return True


@configsuite.validator_msg("Only variable length containers can specify AllowEmpty")
def _check_allowempty_only_variable_containers(schema_level):
    level_type = schema_level.get(MK.Type)
    const_len = isinstance(level_type, types.BasicType) or level_type == types.NamedDict
    return not (const_len and MK.AllowEmpty in schema_level)


_SCHEMA_LEVEL_DEFAULTS = {
    MK.Required: True,
    MK.AllowNone: False,
    MK.AllowEmpty: True,
    MK.Description: "",
    MK.ElementValidators: (),
    MK.ContextValidators: (),
}


META_SCHEMA = {
    MK.Type: types.NamedDict,
    MK.ElementValidators: (
        _check_allownone_type,
        _check_required_type,
        _check_default_type,
        _check_allownone_required,
        _check_required_not_default,
        _check_allowempty_only_variable_containers,
    ),
    MK.Content: {
        MK.Type: {MK.Type: types.Type},
        MK.Required: {
            MK.Type: types.Bool,
            MK.Required: False,
            MK.Default: _SCHEMA_LEVEL_DEFAULTS[MK.Required],
        },
        MK.AllowNone: {
            MK.Type: types.Bool,
            MK.Required: False,
            MK.Default: _SCHEMA_LEVEL_DEFAULTS[MK.AllowNone],
        },
        MK.Description: {
            MK.Type: types.String,
            MK.Required: False,
            MK.Default: _SCHEMA_LEVEL_DEFAULTS[MK.Description],
        },
        MK.Default: {MK.Type: _Anytype, MK.Required: False, MK.AllowNone: True},
        MK.ElementValidators: {
            MK.Type: types.List,
            MK.Content: {MK.Item: {MK.Type: types.Callable}},
        },
        MK.ContextValidators: {
            MK.Type: types.List,
            MK.Content: {MK.Item: {MK.Type: types.Callable}},
        },
        MK.Transformation: {
            MK.Type: types.Callable,
            MK.Required: False,
            MK.AllowNone: True,
        },
        MK.ContextTransformation: {
            MK.Type: types.Callable,
            MK.Required: False,
            MK.AllowNone: True,
        },
        MK.LayerTransformation: {
            MK.Type: types.Callable,
            MK.Required: False,
            MK.AllowNone: True,
        },
        MK.Content: {MK.Type: _Anytype},
        MK.AllowEmpty: {
            MK.Type: types.Bool,
            MK.Required: False,
            MK.Default: _SCHEMA_LEVEL_DEFAULTS[MK.AllowEmpty],
        },
    },
}


def _build_meta_schema(deduce_required, schema_type):
    meta_schema = copy.deepcopy(META_SCHEMA)

    if isinstance(schema_type, types.BasicType):
        meta_schema[MK.Content].pop(MK.Content)

    if deduce_required:
        meta_schema[MK.ElementValidators] = (
            _check_allownone_type,
            _check_required_type,
            _check_default_type,
            _check_allowempty_only_variable_containers,
        )

    return meta_schema


_REQUIRED_DEPRECATION_MSG = (
    "Specifying whether elements are required directly is deprecated. "
    "Please remove them from your schema to adopt to future behaviour. "
    "See the documentation for more details."
)


_EXPLICIT_REQUIRED_DEPRECATION_MSG = (
    "Specifying whether elements are required directly is deprecated. Use "
    "`ConfigSuite(..., deduce_required=True)` to adopt to future behaviour. "
    "See the documentation for more details."
)


def assert_valid_schema(
    schema, allow_default=False, validate_named_keys=True, deduce_required=False
):
    with warnings.catch_warnings(record=True) as warnings_manager:
        _assert_valid_schema(
            schema,
            allow_default=allow_default,
            validate_named_keys=validate_named_keys,
            deduce_required=deduce_required,
        )

    if not deduce_required:
        warnings.warn(
            _EXPLICIT_REQUIRED_DEPRECATION_MSG, DeprecationWarning, stacklevel=3,
        )
    elif any(_REQUIRED_DEPRECATION_MSG == str(w.message) for w in warnings_manager):
        warnings.warn(
            _REQUIRED_DEPRECATION_MSG, DeprecationWarning, stacklevel=3,
        )


def _assert_valid_schema(schema, allow_default, validate_named_keys, deduce_required):
    _assert_valid_schema_level(schema, allow_default, deduce_required)

    level_type = schema[MK.Type]
    if isinstance(level_type, types.BasicType):
        return
    elif level_type == types.NamedDict:
        _assert_valid_named_dict_schema(schema, validate_named_keys, deduce_required)
    elif level_type == types.List:
        _assert_valid_list_schema(schema, validate_named_keys, deduce_required)
    elif level_type == types.Dict:
        _assert_valid_dict_schema(schema, validate_named_keys, deduce_required)
    else:
        raise TypeError("Unknown base container: {}".format(schema))


def _build_level_schema(schema):
    schema = copy.deepcopy(schema)
    level_schema = copy.deepcopy(_SCHEMA_LEVEL_DEFAULTS)
    is_basic_type = isinstance(schema[MK.Type], types.BasicType)

    # Discard ignore from default if not in level schema
    if MK.Required not in schema:
        level_schema.pop(MK.Required)

    # Discard basic type defaults for non-basic types
    if not is_basic_type:
        for basic_key in (MK.Required, MK.Default, MK.AllowNone):
            if basic_key in level_schema:
                level_schema.pop(basic_key)

    # Discard allow_empty default for basic types and named dicts
    if is_basic_type or schema[MK.Type] == types.NamedDict:
        level_schema.pop(MK.AllowEmpty)

    level_schema.update(schema)
    return level_schema


def _assert_valid_schema_level(schema, allow_default, deduce_required):
    schema = _build_level_schema(schema)

    if MK.Required in schema:
        warnings.warn(_REQUIRED_DEPRECATION_MSG, DeprecationWarning)

    if MK.Default in schema and not allow_default:
        fmt = "Default value is only allowed for contents in NamedDict"
        raise ValueError(fmt)

    meta_schema = _build_meta_schema(deduce_required, schema.get(MK.Type))
    level_validator = configsuite.Validator(meta_schema)
    result = level_validator.validate(schema)

    if not result.valid:
        for error in result.errors:

            def gen_err_msg(error):
                return "{} at {}".format(error.msg, error.key_path)

            if isinstance(error, configsuite.MissingKeyError):
                raise KeyError(gen_err_msg(error))
            elif isinstance(error, configsuite.UnknownKeyError):
                raise KeyError(gen_err_msg(error))
            elif isinstance(error, configsuite.InvalidTypeError):
                raise TypeError(gen_err_msg(error))
            elif isinstance(error, configsuite.InvalidValueError):
                raise ValueError(gen_err_msg(error))
            else:
                raise AssertionError(
                    "Internal error: Unknown validation error: {}".format(error)
                )


def _assert_dict_key(key):
    if not isinstance(key, str):
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


def _assert_valid_named_dict_schema(schema, validate_keys, deduce_required):
    if MK.Content not in schema:
        err_msg = "{} schema has no {}: {}".format(
            types.NamedDict.name, MK.Content, schema
        )
        raise KeyError(err_msg)

    content = schema[MK.Content]
    if not isinstance(content, dict):
        err_msg = "Expected {} to be a dict, was {}".format(MK.Content, type(content))
        raise ValueError(err_msg)

    if validate_keys:
        for key in content.keys():
            _assert_dict_key(key)

    for value in content.values():
        _assert_valid_schema(value, True, validate_keys, deduce_required)


def _assert_valid_list_schema(schema, validate_named_keys, deduce_required):
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

    _assert_valid_schema(content[MK.Item], False, validate_named_keys, deduce_required)


def _assert_valid_dict_schema(schema, validate_named_keys, deduce_required):
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

    _assert_valid_schema(content[MK.Key], False, validate_named_keys, deduce_required)
    _assert_valid_schema(content[MK.Value], False, validate_named_keys, deduce_required)
