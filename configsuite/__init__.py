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

from __future__ import absolute_import

try:
    from ._version import version as __version__
except ImportError:
    from .__about__ import __version__

from configsuite.meta_keys import MetaKeys
from configsuite.types import (
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
    transformation_msg,
)
from configsuite.validation_errors import (
    ValidationError,
    InvalidTypeError,
    MissingKeyError,
    UnknownKeyError,
    InvalidValueError,
    TransformationError,
    ContextExtractionError,
)
from configsuite.validator import Validator
from configsuite.transformer import Transformer
from configsuite.config import ConfigSuite
from configsuite import docs
