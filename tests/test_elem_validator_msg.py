"""Copyright 2019 Equinor ASA and The Netherlands Organisation for
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


import unittest
import configsuite


class TestElemValidatorMsg(unittest.TestCase):
    def test_true(self):
        @configsuite.validator_msg("This should always be true")
        def tautology():
            return True

        self.assertTrue(tautology())

    def test_false(self):
        @configsuite.validator_msg("This should always be false")
        def self_contradiction():
            return False

        self.assertFalse(self_contradiction())

    def test_func_msg(self):
        msg = "This function is self-imploding"

        @configsuite.validator_msg(msg)
        def implode(_):
            raise Exception("Thou shalt not call me")

        self.assertEqual(msg, implode.msg)

    def test_result_msg(self):
        msg = "The indentify function"

        @configsuite.validator_msg(msg)
        def identity(arg):
            return arg

        res_msg_fmt = "{} is {} on input {}"
        for x in (True, False):
            expected_msg = res_msg_fmt.format(msg, str(x).lower(), x)
            # pylint: disable=no-member
            self.assertEqual(expected_msg, identity(x).msg)
