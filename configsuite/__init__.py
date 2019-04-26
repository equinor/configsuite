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


try:
    from ._version import version as __version__
except ImportError:
    from .__about__ import __version__


from .meta_keys import MetaKeys
from .types import (
    BasicType,
    Collection,
    String,
    Integer,
    List,
    Number,
    Date,
    DateTime,
    Dict,
    NamedDict,
    validator_msg,
)
from .validation_errors import (
    ValidationError,
    InvalidTypeError,
    MissingKeyError,
    UnknownKeyError,
    InvalidValueError,
)
from .validator import Validator
from .config import ConfigSuite
from . import docs
