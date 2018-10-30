import collections


class ValidationErrorNames(object):
    UNKNOWN_KEY = 'unknown_key'
    MISSING_KEY = 'missing_key'
    INVALID_TYPE = 'invalid_type'
    INVALID_VALUE = 'invalid_value'


UnknownKeyError = collections.namedtuple(
    ValidationErrorNames.UNKNOWN_KEY,
    ('msg', 'key_path')
    )


MissingKeyError = collections.namedtuple(
    ValidationErrorNames.MISSING_KEY,
    ('msg', 'key_path')
    )


InvalidTypeError = collections.namedtuple(
    ValidationErrorNames.INVALID_TYPE,
    ('msg', 'key_path')
    )

InvalidValueError = collections.namedtuple(
    ValidationErrorNames.INVALID_VALUE,
    ('msg', 'key_path')
    )
