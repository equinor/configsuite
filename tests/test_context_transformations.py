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


import collections
import copy
import unittest
import sys

import configsuite
from configsuite import MetaKeys as MK
from .data import templating


class TestContextTransformations(unittest.TestCase):
    def test_context_transformation_valid(self):
        raw_config = templating.build_config_with_definitions()
        suite = configsuite.ConfigSuite(
            raw_config,
            templating.build_schema_with_definitions(),
            extract_transformation_context=templating.extract_templating_context,
        )
        self.assertTrue(suite.valid, suite.errors)
        self.assertEqual(
            templating.template_results_with_definitions(), suite.snapshot.templates
        )

    def test_context_transformation_layers(self):
        raw_config = templating.build_config_with_definitions()
        top_layer = {"definitions": {"animal": "horse"}}
        suite = configsuite.ConfigSuite(
            top_layer,
            templating.build_schema_with_definitions(),
            layers=(raw_config,),
            extract_transformation_context=templating.extract_templating_context,
        )
        self.assertTrue(suite.valid, suite.errors)
        self.assertEqual(
            tuple(
                [
                    line.replace("pig", "horse")
                    for line in templating.template_results_with_definitions()
                ]
            ),
            suite.snapshot.templates,
        )

    def test_context_transformation_push(self):
        raw_config = templating.build_config_with_definitions()
        top_layer = {"definitions": {"animal": "horse"}}
        suite = configsuite.ConfigSuite(
            raw_config,
            templating.build_schema_with_definitions(),
            extract_transformation_context=templating.extract_templating_context,
        )

        layered_suite = suite.push(top_layer)
        self.assertTrue(layered_suite.valid, layered_suite.errors)
        self.assertEqual(
            tuple(
                [
                    line.replace("pig", "horse")
                    for line in templating.template_results_with_definitions()
                ]
            ),
            layered_suite.snapshot.templates,
        )

    def test_context_transformation_exception(self):
        raw_config = templating.build_config_with_definitions()

        schema = templating.build_schema_with_definitions()
        temp_schema = schema[MK.Content]["templates"][MK.Content][MK.Item]
        _render = temp_schema[MK.ContextTransformation]
        transformation_msg = "Renders Jinja template until the end"
        error_msg = "Did not expect to reach the end!"

        @configsuite.transformation_msg(transformation_msg)
        def _no_end_render(elem, context):
            if elem == "The end.":
                raise ValueError(error_msg)
            return _render(elem, context)

        temp_schema[MK.ContextTransformation] = _no_end_render

        suite = configsuite.ConfigSuite(
            raw_config,
            schema,
            extract_transformation_context=templating.extract_templating_context,
        )
        self.assertFalse(suite.valid)

        self.assertEqual(1, len(suite.errors))
        err = suite.errors[0]
        self.assertIsInstance(err, configsuite.TransformationError)
        error_fmt = "'{}' failed on input '{}' with error '{}'"
        expected_error = error_fmt.format(transformation_msg, "The end.", error_msg)
        self.assertEqual(expected_error, err.msg)
        self.assertEqual(("templates", 4), err.key_path)

    def test_context_transformation_context_extraction_exception(self):
        def _extract_context_with_errors(configuration):
            if ("raise", "exception") in configuration.definitions:
                raise Exception("I'm containing errors")
            return templating.extract_templating_context(configuration)

        raw_config = templating.build_config_with_definitions()
        raw_config["definitions"]["raise"] = "exception"

        suite = configsuite.ConfigSuite(
            raw_config,
            templating.build_schema_with_definitions(),
            extract_transformation_context=_extract_context_with_errors,
        )

        self.assertFalse(suite.valid)
        self.assertEqual(1, len(suite.errors))
        err = suite.errors[0]
        self.assertIsInstance(err, configsuite.ContextExtractionError)

    def test_context_transformation_list(self):
        def extract_prefix_and_definitions(configuration):
            def_context = templating.extract_templating_context(configuration)

            prefix = "(default_prefix)"
            for key, val in configuration.definitions:
                if key == "prefix":
                    prefix = val

            Context = collections.namedtuple("Context", ["definitions", "prefix"])
            return Context(definitions=def_context.definitions, prefix=prefix)

        raw_config = templating.build_config_with_definitions()
        prefix = "[(unreal prefix)] "
        raw_config["definitions"]["prefix"] = prefix

        @configsuite.transformation_msg("Adds prefix to all strings in list")
        def _context_prefixer(templates, context):
            return tuple([context.prefix + template for template in templates])

        schema = templating.build_schema_with_definitions()
        schema[MK.Content]["templates"][MK.ContextTransformation] = _context_prefixer

        suite = configsuite.ConfigSuite(
            raw_config,
            schema,
            extract_transformation_context=extract_prefix_and_definitions,
        )

        self.assertTrue(suite.valid)
        self.assertEqual(
            tuple(
                [
                    prefix + template
                    for template in templating.template_results_with_definitions()
                ]
            ),
            suite.snapshot.templates,
        )

    def test_context_transformation_nameddict(self):
        raw_config = templating.build_config_with_definitions()

        def extract_illegal_and_definitions(configuration):
            def_context = templating.extract_templating_context(configuration)

            Context = collections.namedtuple("Context", ["definitions", "inject"])
            return Context(definitions=def_context.definitions, inject=True)

        @configsuite.transformation_msg("Injects key `illegal` mapping to `True`")
        def _inject_illegal(elem, context):
            elem = copy.deepcopy(elem)
            if context.inject:
                elem["inject"] = True
            return elem

        schema = templating.build_schema_with_definitions()
        schema[MK.ContextTransformation] = _inject_illegal

        suite = configsuite.ConfigSuite(
            raw_config,
            schema,
            extract_transformation_context=extract_illegal_and_definitions,
        )

        self.assertFalse(suite.valid)
        self.assertEqual(1, len(suite.errors))
        self.assertIsInstance(suite.errors[0], configsuite.UnknownKeyError)

    def test_context_transformation_dict(self):
        raw_config = templating.build_config_with_definitions()

        def extract_templates_and_definitions(configuration):
            def_context = templating.extract_templating_context(configuration)

            Context = collections.namedtuple("Context", ["definitions", "templates"])
            return Context(
                definitions=def_context.definitions, templates=configuration.templates
            )

        @configsuite.transformation_msg("Injects all templates as definitions")
        def template_injector(definitions, context):
            definitions = copy.deepcopy(definitions)
            for idx, template in enumerate(context.templates):
                definitions["template[{}]".format(idx)] = template
            return definitions

        schema = templating.build_schema_with_definitions()
        schema[MK.Content]["definitions"][MK.ContextTransformation] = template_injector

        suite = configsuite.ConfigSuite(
            raw_config,
            schema,
            extract_transformation_context=extract_templates_and_definitions,
        )

        self.assertTrue(suite.valid)
        self.assertEqual(
            sum(map(len, raw_config.values())), len(suite.snapshot.definitions)
        )

    def test_context_transformation_non_readable_results(self):
        raw_config = templating.build_config_with_definitions()

        @configsuite.transformation_msg("Deforming elements")
        def _deformer(elem, _):
            return [elem]

        schema = templating.build_schema_with_definitions()
        schema[MK.ContextTransformation] = _deformer

        suite = configsuite.ConfigSuite(
            raw_config,
            schema,
            extract_transformation_context=templating.extract_templating_context,
        )
        self.assertFalse(suite.readable, suite.errors)
        self.assertEqual(1, len(suite.errors))

    def test_context_transformation_non_readable_transformation_result(self):
        raw_config = templating.build_config_with_definitions()

        @configsuite.transformation_msg("Deforming elements")
        def _deformer(elem):
            return [elem]

        schema = templating.build_schema_with_definitions()
        schema[MK.Transformation] = _deformer
        schema[MK.ContextTransformation] = lambda *_: sys.exit(1)

        suite = configsuite.ConfigSuite(
            raw_config,
            schema,
            extract_transformation_context=templating.extract_templating_context,
        )
        self.assertFalse(suite.readable, suite.errors)
        self.assertEqual(1, len(suite.errors))
        self.assertIsInstance(suite.errors[0], configsuite.InvalidTypeError)

    def test_context_transformation_after_transformation(self):
        raw_config = templating.build_config_with_definitions()
        prefix = "[(unreal prefix)] "

        @configsuite.transformation_msg("Adds prefix to a string")
        def _add_prefix(template):
            return prefix + template

        schema = templating.build_schema_with_definitions()
        template_schema = schema[MK.Content]["templates"][MK.Content][MK.Item]
        template_schema[MK.Transformation] = _add_prefix

        suite = configsuite.ConfigSuite(
            raw_config,
            schema,
            extract_transformation_context=templating.extract_templating_context,
        )

        self.assertTrue(suite.valid)
        self.assertEqual(
            tuple(
                [
                    prefix + template
                    for template in templating.template_results_with_definitions()
                ]
            ),
            suite.snapshot.templates,
        )

    def test_context_transformation_prior_to_validation(self):
        raw_config = templating.build_config_with_definitions()
        raw_config["templates"].append(">")

        @configsuite.validator_msg("Are all template traces gone")
        def _no_template_trace(template):
            return "<" not in template and ">" not in template

        schema = templating.build_schema_with_definitions()
        template_schema = schema[MK.Content]["templates"][MK.Content][MK.Item]
        template_schema[MK.ElementValidators] = (_no_template_trace,)

        suite = configsuite.ConfigSuite(
            raw_config,
            schema,
            extract_transformation_context=templating.extract_templating_context,
        )

        self.assertFalse(suite.valid)
        self.assertEqual(1, len(suite.errors))
        self.assertIsInstance(suite.errors[0], configsuite.InvalidValueError)
