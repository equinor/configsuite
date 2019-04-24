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
import numbers
import datetime


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

    def __and__(self, other):
        return bool(self) and bool(other)

    @property
    def msg(self):
        msg_fmt = "{} is {} on input {}"
        return msg_fmt.format(self._msg, "true" if self else "false", self._input)

    def __repr__(self):
        fmt = "BooleanResult({}, {}, {})"
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
        class Wrapper(object):
            def __init__(self, function, msg):
                self._function = function
                self._msg = msg

            @property
            def msg(self):
                return self._msg

            def __call__(self, *args, **kwargs):
                res = self._function(*args, **kwargs)
                return BooleanResult(res, self._msg, str(*args) + str(**kwargs))

        return Wrapper(function, msg)

    return real_decorator


BasicType = collections.namedtuple("Type", ["name", "validate"])
Collection = collections.namedtuple("Type", ["name", "validate"])

_type_eq = lambda self, other: self.name == other.name
_type_neq = lambda self, other: not _type_eq(self, other)
Collection.__eq__ = _type_eq
Collection.__neq__ = lambda self, other: not _type_neq(self, other)


@validator_msg("Is x a dictionary")
def _is_pydict(x):
    return isinstance(x, dict)


@validator_msg("Is x a list")
def _is_list(x):
    return isinstance(x, (list, tuple))


@validator_msg("Is x a string")
def _is_string(x):
    return isinstance(x, str)


@validator_msg("Is x an integer")
def _is_integer(x):
    return isinstance(x, int)


@validator_msg("Is x a number")
def _is_number(x):
    return isinstance(x, numbers.Number)


@validator_msg("Is x a bool")
def _is_bool(x):
    return isinstance(x, bool)


@validator_msg("Is x a date")
def _is_date(x):
    return isinstance(x, datetime.date)


@validator_msg("Is x a datetime")
def _is_datetime(x):
    return isinstance(x, datetime.datetime)


NamedDict = Collection("named_dict", _is_pydict)
Dict = Collection("dict", _is_pydict)
List = Collection("list", _is_list)
String = BasicType("string", _is_string)
Integer = BasicType("integer", _is_integer)
Number = BasicType("number", _is_number)
Bool = BasicType("bool", _is_bool)
Date = BasicType("date", _is_date)
DateTime = BasicType("datetime", _is_datetime)

# Meta types


@validator_msg("Is x a type")
def _is_type(x):
    return isinstance(x, (BasicType, Collection))


Type = BasicType("type", _is_type)
Callable = BasicType("callable", validator_msg("Is x callable")(callable))
