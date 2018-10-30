import collections


class ValidationErrorNames(object):
    INVALID_TYPE = 'invalid_type'


InvalidTypeError = collections.namedtuple(
    ValidationErrorNames.INVALID_TYPE,
    ('msg', 'key_path')
    )
