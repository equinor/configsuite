"""Copyright 2020 Equinor ASA and The Netherlands Organisation for
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


import configsuite
import unittest


class TestValidateMetaSchema(unittest.TestCase):
    # pylint: disable=no-self-use
    def test_validate_meta_schema(self):
        configsuite.schema.assert_valid_schema(
            configsuite.schema.META_SCHEMA,
            allow_default=False,
            validate_named_keys=False,
        )
