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


import collections
import configsuite
from configsuite import MetaKeys as MK


ValidationResult = collections.namedtuple("ValidationResult", ("valid", "errors"))


class Validator(object):
    def __init__(self, schema, stop_condition=(lambda schema: False)):
        self._schema = schema
        self._errors = None
        self._key_stack = None
        self._stop_condition = stop_condition

    def validate(self, config):
        self._errors = []
        self._key_stack = _KeyStack()
        valid = self._validate(config, self._schema)
        return ValidationResult(valid=valid, errors=tuple(self._errors))

    def _validate(self, config, schema):
        if self._stop_condition(schema):
            return True

        data_type = schema[MK.Type]

        valid = data_type.validate(config)
        if not valid:
            self._add_invalid_type_error(valid.msg)
        elif isinstance(data_type, configsuite.BasicType):
            pass
        elif data_type == configsuite.types.NamedDict:
            valid &= self._validate_named_dict(config, schema[MK.Content])
        elif data_type == configsuite.types.List:
            valid &= self._validate_list(config, schema[MK.Content])
        elif data_type == configsuite.types.Dict:
            valid &= self._validate_dict(config, schema[MK.Content])
        else:
            msg = "Unknown type {} while validating"
            raise TypeError(msg.format(data_type))

        if valid:
            valid &= self._element_validation(config, schema)

        return bool(valid)

    def _element_validation(self, config, schema):
        elem_vals = schema.get(MK.ElementValidators, ())

        valid = True
        for val in elem_vals:
            res = val(config)
            if not res:
                valid = False
                self._add_invalid_value_error(res.msg)

        return valid

    def _identify_unknown_dict_keys(self, config, content_schema):
        unknown_keys = set(config.keys()) - set(content_schema.keys())
        for key in unknown_keys:
            msg_fmt = "Unknown key: {}"
            self._add_unknown_key_error(msg_fmt.format(key))
        return len(unknown_keys) == 0

    def _identify_missing_dict_keys(self, config, content_schema):
        optional_keys = [
            key
            for key in content_schema
            if not content_schema[key].get(MK.Required, True)
        ]
        missing_keys = (
            set(content_schema.keys()) - set(config.keys()) - set(optional_keys)
        )

        for key in missing_keys:
            msg_fmt = "Missing key: {}"
            self._add_missing_key_error(msg_fmt.format(key))
        return len(missing_keys) == 0

    def _validate_named_dict(self, config, content_schema):
        valid = True
        valid &= self._identify_unknown_dict_keys(config, content_schema)
        valid &= self._identify_missing_dict_keys(config, content_schema)

        valid_keys = set(config.keys()).intersection(set(content_schema.keys()))
        for key in valid_keys:
            self._key_stack.append(key)
            valid &= self._validate(config[key], content_schema[key])
            self._key_stack.pop()

        return valid

    def _validate_list(self, config, schema):
        item_schema = schema[MK.Item]

        valid = True
        for idx, config_item in enumerate(config):
            self._key_stack.append(idx)
            valid &= self._validate(config_item, item_schema)
            self._key_stack.pop()

        return valid

    def _validate_dict(self, config, content_schema):
        key_schema = content_schema[MK.Key]
        value_schema = content_schema[MK.Value]

        valid = True
        for key, value in config.items():
            self._key_stack.append(key)
            valid &= self._validate(key, key_schema)
            valid &= self._validate(value, value_schema)
            self._key_stack.pop()

        return valid

    def _add_invalid_type_error(self, msg):
        self._add_error(msg, configsuite.InvalidTypeError)

    def _add_unknown_key_error(self, msg):
        self._add_error(msg, configsuite.UnknownKeyError)

    def _add_missing_key_error(self, msg):
        self._add_error(msg, configsuite.MissingKeyError)

    def _add_invalid_value_error(self, msg):
        self._add_error(msg, configsuite.InvalidValueError)

    def _add_error(self, msg, ErrorType):
        err = ErrorType(msg, self._key_stack.keys())
        self._errors.append(err)


class _KeyStack(object):
    def __init__(self):
        self._stack = []

    def append(self, key):
        self._stack.append(key)

    def pop(self):
        self._stack.pop()

    def keys(self):
        return tuple(self._stack)
