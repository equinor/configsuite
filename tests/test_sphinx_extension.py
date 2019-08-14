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

import os
import unittest
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace
from sphinx.errors import SphinxWarning
from functools import wraps

from tests import tmpdir


def func_returns_int():
    return 1


def func_takes_arguments(arg1):  # pylint: disable=unused-argument
    return {}


non_callable_object = 1


class MockApp(Sphinx):
    """
    A subclass of :class:`Sphinx`
    """

    def __init__(self,):

        Sphinx.__init__(
            self,
            srcdir=os.path.abspath(""),
            confdir=os.path.abspath(""),
            outdir="result",
            doctreedir="doctreedir",
            buildername="html",
            warningiserror=True,
        )


class with_sphinx_app(object):
    def __init__(self, *sphinxargs, **sphinxkwargs):
        self.sphinxargs = sphinxargs
        self.sphinxkwargs = sphinxkwargs

    def __call__(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            app = None
            sphinxkwargs = dict(self.sphinxkwargs)
            with docutils_namespace():
                app = MockApp(*self.sphinxargs, **sphinxkwargs)
                return func(*(args + (app,)), **kwargs)

        return decorator


class TestSphinxExtension(unittest.TestCase):
    @tmpdir("tests/data/doc")
    @with_sphinx_app()
    def test_invalid_setup(self, app):
        missing_func = """
        .. configsuite::
            :module: tests
        """

        with open("index.rst", "w") as f:
            f.write(missing_func)

        with self.assertRaises(SphinxWarning) as context:
            app.build()

        self.assertTrue(
            "Expected 'module.function', got tests" in str(context.exception)
        )

    @tmpdir("tests/data/doc")
    @with_sphinx_app()
    def test_invalid_module(self, app):
        invalid_func = """
        .. configsuite::
            :module: tests.non_existing_module.non_existing_function
        """

        with open("index.rst", "w") as f:
            f.write(invalid_func)

        with self.assertRaises(SphinxWarning) as context:
            app.build()

        self.assertTrue("non_existing_module" in str(context.exception))

    @tmpdir("tests/data/doc")
    @with_sphinx_app()
    def test_invalid_func(self, app):
        invalid_func = """
        .. configsuite::
            :module: tests.data.non_existing_function
        """

        with open("index.rst", "w") as f:
            f.write(invalid_func)

        with self.assertRaises(SphinxWarning) as context:
            app.build()

        self.assertTrue(
            "has no attribute 'non_existing_function'" in str(context.exception)
        )

    @tmpdir("tests/data/doc")
    @with_sphinx_app()
    def test_func_must_be_callable(self, app):
        invalid_func = """
        .. configsuite::
            :module: tests.test_sphinx_extension.non_callable_object
        """

        with open("index.rst", "w") as f:
            f.write(invalid_func)

        with self.assertRaises(SphinxWarning) as context:
            app.build()

        self.assertTrue(
            "must provide a callable function, the 'non_callable_object' was not"
            in str(context.exception)
        )

    @tmpdir("tests/data/doc")
    @with_sphinx_app()
    def test_func_takes_no_arguments(self, app):
        invalid_func = """
        .. configsuite::
            :module: tests.test_sphinx_extension.func_takes_arguments
        """

        with open("index.rst", "w") as f:
            f.write(invalid_func)

        with self.assertRaises(SphinxWarning) as context:
            app.build()

        self.assertTrue(
            "not require any arguments, the 'func_takes_arguments' takes 1 argument(s)"
            in str(context.exception)
        )

    @tmpdir("tests/data/doc")
    @with_sphinx_app()
    def test_func_invalid_return_type(self, app):
        invalid_func = """
        .. configsuite::
            :module: tests.test_sphinx_extension.func_returns_int
        """

        with open("index.rst", "w") as f:
            f.write(invalid_func)

        with self.assertRaises(SphinxWarning) as context:
            app.build()

        self.assertTrue(
            "The function 'func_returns_int' returned" in str(context.exception)
        )

    @tmpdir("tests/data/doc")
    @with_sphinx_app()
    def test_sphinx_build(self, app):
        app.build()
        with open(os.path.join(app.outdir, "index.html"), "r") as f:
            html = f.read()

        contents = [
            "Text above",
            "The PetMeet configuration is to give an",
            "name",
            "Your full name.",
            "Text below",
        ]

        for content in contents:
            self.assertTrue(content in html)

    @tmpdir("tests/data/doc")
    @with_sphinx_app()
    def test_sphinx_complete_generation(self, app):
        complete_schema = """
        .. configsuite::
            :module: tests.data.car.build_schema_with_validators_and_transformators
        """
        with open("index.rst", "w") as f:
            f.write(complete_schema)

        app.build()
        with open(os.path.join(app.outdir, "index.html"), "r") as f:
            html = f.read()

        contents = [
            "production_date",
            "country",
            #  "Norway",
            "tire",
            "dimension",
            # "17",
            "owner",
            "location",
            "incidents",
            "Convert to cm",
            "Convert to cm - ignoring context",
            "Is x a valid date",
            "Is x a valid dimension",
        ]
        for content in contents:
            self.assertTrue(content in html)
