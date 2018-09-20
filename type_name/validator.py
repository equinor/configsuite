import collections
import type_name
from type_name import MetaKeys as MK


ValidationResult = collections.namedtuple(
    'ValidationResult',
    ('valid', 'errors')
)


class Validator(object):

    def __init__(self, schema):
        self._schema = schema

    def validate(self, config):
        valid = self._validate(config, self._schema)
        return ValidationResult(valid=valid, errors=())


    def _validate(self, config, schema):
        data_type = schema[MK.Type]

        valid = data_type.validate(config)
        if not valid:
            return valid

        if data_type.basic:
           return valid 
        elif data_type == type_name.types.Dict:
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

        for key in config:
            if not self._validate(config[key], content_schema[key]):
                return False

        return True
