import collections
import protoconf
from protoconf import MetaKeys as MK


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

        if isinstance(data_type, protoconf.BasicType):
           return bool(valid)
        elif data_type == protoconf.types.Dict:
            return self._validate_dict(config, schema[MK.Content])
        elif data_type == protoconf.types.List:
            return self._validate_list(config, schema[MK.Content])
        else:
            msg = 'Unknown type {} while validating'
            raise TypeError(msg.format(data_type))

    def _identify_unknown_dict_keys(self, config, content_schema):
        unknown_keys = set(config.keys()) - set(content_schema.keys())
        for key in unknown_keys:
            msg_fmt = 'Unknown key: {}'
            self._add_unknown_key_error(msg_fmt.format(key))
        return len(unknown_keys) == 0

    def _identify_missing_dict_keys(self, config, content_schema):
        optional_keys = [
            key
            for key in content_schema
            if not content_schema[key].get(MK.Required, True)
        ]
        missing_keys = (
            set(content_schema.keys())
            - set(config.keys())
            - set(optional_keys)
        )

        for key in missing_keys:
            msg_fmt = 'Missing key: {}'
            self._add_missing_key_error(msg_fmt.format(key))
        return len(missing_keys) == 0

    def _validate_dict(self, config, content_schema):
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
        assert 1 == len(schema)
        item_schema = schema[MK.Item]

        valid = True
        for idx, config_item in enumerate(config):
            self._key_stack.append(idx)
            valid &= self._validate(config_item, item_schema)
            self._key_stack.pop()

        return valid

    def _add_invalid_type_error(self, msg):
        self._add_error(msg, protoconf.InvalidTypeError)

    def _add_unknown_key_error(self, msg):
        self._add_error(msg, protoconf.UnknownKeyError)

    def _add_missing_key_error(self, msg):
        self._add_error(msg, protoconf.MissingKeyError)

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
