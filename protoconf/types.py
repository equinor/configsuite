import enum
import collections
import numbers


class BooleanResult(object):
    """BooleanResult is a wrapper around a bool that also has a .msg attribute.

    The message is an explanation of the boolean value.
    """

    def __init__(self, value, msg, indata):
        self._value = value
        self._msg = str(msg)
        self._input = str(indata)

    def __nonzero__(self):
        return self._value is True

    def __bool__(self):
        return self._value is True

    @property
    def msg(self):
        msg_fmt = '{} is {} on input {}'
        return msg_fmt.format(
                self._msg,
                'true' if self else 'false',
                self._input,
                )

    @property
    def raw_msg(self):
        return self._msg

    def __repr__(self):
        fmt = 'BooleanResult({}, {}, {})'
        return fmt.format(bool(self), self._msg, self._input)


def validator_msg(msg):
    """Validator decorator wraps return value in a message container.

    Usage:

        @validator_msg('assert len(x) <= 2')
        def validate_size(x):
            return len(x) <= 2

    Now, if `validate_size` returns a falsy value `ret`, for instance if
    provided with range(4), we will have
        `ret.msg = 'assert len(x) <= 2 is false on input [0, 1, 2, 3]`.

    On the other hand, if `validate_size` returns a true value `ret`, for
    instance if provided with [0, 1], we will have
        `ret.msg = 'assert len(x) <= 2 is true on input [0, 1]`.
    """
    def real_decorator(function):
        def wrapper(*args, **kwargs):
            res = function(*args, **kwargs)
            return BooleanResult(res, msg, str(*args))
        return wrapper
    return real_decorator


BasicType = collections.namedtuple('Type', ['name', 'validate'])
Collection = collections.namedtuple('Type', ['name', 'validate'])


@validator_msg('Is x a dictionary')
def _is_dict(x):
    return isinstance(x, dict)


@validator_msg('Is x a string')
def _is_string(x):
    return isinstance(x, str)


@validator_msg('Is x an integer')
def _is_integer(x):
    return isinstance(x, int)


@validator_msg('Is x a number')
def _is_number(x):
    return isinstance(x, numbers.Number)


@validator_msg('Is x a bool')
def _is_bool(x):
    return isinstance(x, bool)


Dict = Collection('dict', _is_dict)
String = BasicType('string', _is_string)
Integer = BasicType('integer', _is_integer)
Number = BasicType('number', _is_number)
Bool = BasicType('bool', _is_bool)
