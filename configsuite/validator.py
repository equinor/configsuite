import collections
import configsuite
from configsuite import MetaKeys as MK


ValidationResult = collections.namedtuple(
    'ValidationResult',
    ('valid', 'errors')
)


class Validator(object):

    def __init__(self, schema):
        self._schema = schema

    def validate(self, config):
        self._errors = []
        self._key_stack = _KeyStack()
        valid = self._validate(config, self._schema)
        return ValidationResult(valid=valid, errors=tuple(self._errors))

    def _validate(self, config, schema):
        data_type = schema[MK.Type]

        valid = data_type.validate(config)
        if not valid:
            self._add_invalid_type_error(valid.msg)
            return bool(valid)

        if isinstance(data_type, configsuite.BasicType):
           return bool(valid)
        elif data_type == configsuite.types.Dict:
            return self._validate_dict(config, schema[MK.Content])
        else:
            msg = 'Unknown type {} while validating'
            raise TypeError(msg.format(data_type))

    def _validate_dict(self, config, content_schema):
        unknown_keys = set(content_schema.keys()) - set(config.keys())
        if len(unknown_keys) > 0:
            return False

        missing_keys = set(config.keys()) - set(content_schema.keys())
        if len(missing_keys) > 0:
            return False

        valid = True
        for key in set(config.keys()).union(set(content_schema.keys())):
            self._key_stack.append(key)
            valid &= self._validate(config[key], content_schema[key])
            self._key_stack.pop()

        return valid

    def _add_invalid_type_error(self, msg):
        err = configsuite.InvalidTypeError(msg, self._key_stack.keys())
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
