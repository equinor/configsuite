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


class ValidationError(object):
    def __init__(self, message, key_path, layer=None):
        self._message = message
        self._key_path = key_path
        self._layer = layer

    def __repr__(self):
        return "{}(msg={}, key_path={}, layer={})".format(
            self.__class__.__name__, self.msg, self.key_path, self.layer
        )

    @property
    def msg(self):
        return self._message

    @property
    def key_path(self):
        return self._key_path

    @property
    def layer(self):
        return self._layer

    def create_layer_error(self, layer):
        return self.__class__(self.msg, self.key_path, layer=layer)

    def __eq__(self, other):
        return (
            self.msg == other.msg
            and self.key_path == other.key_path
            and self.layer == other.layer
        )

    def __neq__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash((self.msg, self.key_path, self.layer))


class UnknownKeyError(ValidationError):
    pass


class MissingKeyError(ValidationError):
    pass


class InvalidValueError(ValidationError):
    pass


class InvalidTypeError(ValidationError):
    pass
