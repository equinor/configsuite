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


import copy
import configsuite
import collections


from .schema import assert_valid_schema
from .meta_keys import MetaKeys as MK


class ConfigSuite(object):
    """A `Suite` exposing the functionality of Config Suite in a unified manner.

    The intended usage of Config Suite is via this immutable suite. It is constructed
    with a `schema` describing the structure of a configuration, together with
    a `raw_config` and possibly additional `layers`.

    Parameters:
    -----------
    raw_config
        The configuration taking precedence.
    schema
        A description of the structure of a valid configuration, together with
        actions that are to be carried out.
    layers: iterable of layers, optional
        Additional layers of configuration. A layer takes precedence over all
        other layers following it in the given sequence. Note that `raw_config`
        takes precedence over all elements of `layers`.
    extract_validation_context: callable, optional
        Callable that extracts the context used for validation. The callable is
        given a snapshot of the configuration as argument. Defaults to the
        constant function always returning `None`.
    extract_transformation_context: callable, optional
        Callable that extracts the context used for transformations. The
        callable is given a snapshot of the configuration as argument. Defaults
        to the constant function always returning `None`.

    Raises:
    -------
    TypeError, KeyError, ValueError
        Approperiate errors are raised if provided with an invalid schema. Note
        that errors are independent of `raw_config` and `layers` and hence not
        user input responsive.
    """

    def __init__(
        self,
        raw_config,
        schema,
        layers=(),
        extract_validation_context=lambda snapshot: None,
        extract_transformation_context=lambda snapshot: None,
    ):
        assert_valid_schema(schema)
        self._layers = tuple(
            [copy.deepcopy(layer) for layer in tuple(layers) + (raw_config,)]
        )
        self._schema = copy.deepcopy(schema)
        self._extract_validation_context = extract_validation_context
        self._extract_transformation_context = extract_transformation_context

        self._readable = True
        self._valid = True
        self._errors = ()
        self._snapshot = None

        self._cached_merged_config = self._build_merged_config()
        if self._readable:
            self._validate_final()
        self._assert_state()

    @property
    def valid(self):
        """A boolean indicating whether the resulting configuration was deemed
        valid according to the schema."""
        return self._valid

    @property
    def errors(self):
        """An iterable of `configsuite.errors` that occurred during validation. Is always
        empty if `valid` is `True` and non-empty otherwise."""
        return self._errors

    @property
    def readable(self):
        """A boolean indicating whether the resulting configuration was deemed
        readable. Is always `True` if `valid` is `True`. For the consequences
        of being readable, see the documentation of `snapshot`."""
        return self._readable

    @property
    def snapshot(self):
        """A complete, immutable representation of the resulting configuration.

        Raises:
        -------
        AssertionError
            Raised on access if `suite` is not `readable`.
        """
        if not self.readable:
            err_msg = "Cannot build snapshot of unreadable configuration."
            raise AssertionError(err_msg)

        if self._snapshot is None:
            self._snapshot = self._build_snapshot(self._merged_config, self._schema)

        return self._snapshot

    @property
    def _validation_context(self):
        return self._extract_validation_context(self.snapshot)

    def push(self, raw_config):
        """Builds a new suite with `raw_config` on top of the current suite.

        Builds a new suite with the same schema, but with `raw_config` on top
        of the layers in the current suite.

        Parameters:
        -----------
        raw_config:
            A configuration that is to take precedence over all layers in the
            current suite.

        Returns:
        --------
        A new `ConfigSuite` with `raw_config` as the first layer.
        """
        return ConfigSuite(
            raw_config,
            self._schema,
            layers=self._layers,
            extract_validation_context=self._extract_validation_context,
            extract_transformation_context=self._extract_transformation_context,
        )

    @property
    def _merged_config(self):
        """The merged config cannot be built and will also not be utilized if the
        config is not readable. Due to this it is built lazily.
        """
        if not self.readable:
            err_msg = "Internal error: Cannot build merged_config of unreadable configuration."
            raise AssertionError(err_msg)

        if self._cached_merged_config is None:
            err_msg = "Internal error: Merged config cannot be accessed before cache is built."
            raise AssertionError(err_msg)

        return self._cached_merged_config

    def _build_merged_config(self):
        layers = self._build_transformed_layers()

        self._validate_readability(layers)
        if not self.readable:
            return None

        merged_config = self._build_initial_merged_config(layers, self._schema)
        merged_config = self._apply_transformations(merged_config)

        self._validate_readability((merged_config,))
        if not self.readable:
            return None

        merged_config = self._apply_context_transformations(merged_config)

        self._validate_readability((merged_config,))
        if not self.readable:
            return None

        return merged_config

    def _build_transformed_layers(self):
        layer_transformer = configsuite.Transformer(
            self._schema, MK.LayerTransformation, (), bottom_up=False
        )
        layers = []
        for layer in self._layers:
            trans_layer = layer_transformer.transform(layer)
            self._errors += trans_layer.errors
            layers.append(trans_layer.result)

        self._valid &= len(self._errors) == 0
        return layers

    def _build_initial_merged_config(self, layers, schema):
        rec = self._build_initial_merged_config
        data_type = schema[MK.Type]

        if isinstance(data_type, configsuite.types.BasicType):
            return layers[-1]
        elif data_type == configsuite.types.List:
            item_schema = schema[MK.Content][MK.Item]
            config = []
            for layer in layers:
                config += [rec((item,), item_schema) for item in layer]
            return tuple(config)
        elif data_type == configsuite.types.NamedDict:
            content_schema = schema[MK.Content]
            config = {}
            all_keys = (key for layer in layers for key in layer.keys())
            for key in all_keys:
                child_layers = tuple([layer[key] for layer in layers if key in layer])
                if len(child_layers) == 0:
                    continue

                if key in content_schema:
                    config[key] = rec(child_layers, content_schema[key])
                else:
                    config[key] = child_layers[-1]
            return config
        elif data_type == configsuite.types.Dict:
            content_schema = schema[MK.Content]
            config = {}
            all_keys = (key for layer in layers for key in layer.keys())
            for key in all_keys:
                child_layers = tuple([layer[key] for layer in layers if key in layer])
                if len(child_layers) == 0:
                    continue
                config[key] = rec(child_layers, content_schema[MK.Value])
            return config
        else:
            msg = "Encountered unknown type {} while building raw config"
            raise TypeError(msg.format(str(data_type)))

    def _apply_transformations(self, config):
        transformer = configsuite.Transformer(self._schema, MK.Transformation, ())
        trans_res = transformer.transform(config)
        self._errors += trans_res.errors
        self._valid &= len(trans_res.errors) == 0
        return trans_res.result

    def _apply_context_transformations(self, config):
        prelim_snapshot = self._build_snapshot(config, self._schema)
        try:
            context = self._extract_transformation_context(prelim_snapshot)
        # pylint: disable=broad-except
        except Exception as e:
            self._valid = False
            self._errors += (configsuite.ContextExtractionError(str(e), ()),)
            return config

        context_transformer = configsuite.Transformer(
            self._schema, MK.ContextTransformation, (context,)
        )
        trans_res = context_transformer.transform(config)
        self._errors += trans_res.errors
        self._valid &= len(trans_res.errors) == 0
        return trans_res.result

    def _build_named_dict_snapshot(self, config, schema):
        data_type = schema[MK.Type]
        content_schema = schema[MK.Content]
        dict_name = data_type.name
        dict_keys = sorted(content_schema.keys())
        dict_collection = collections.namedtuple(dict_name, dict_keys)

        return dict_collection(
            **{
                key: self._build_snapshot(config.get(key), content_schema[key])
                for key in content_schema
            }
        )

    def _build_list_snapshot(self, config, schema):
        item_schema = schema[MK.Content][MK.Item]
        return tuple([self._build_snapshot(elem, item_schema) for elem in config])

    def _build_dict_snapshot(self, config, schema):
        key_schema = schema[MK.Content][MK.Key]
        value_schema = schema[MK.Content][MK.Value]

        Pair = collections.namedtuple("KeyValuePair", ["key", "value"])
        return tuple(
            [
                Pair(
                    self._build_snapshot(key, key_schema),
                    self._build_snapshot(value, value_schema),
                )
                for key, value in config.items()
            ]
        )

    def _build_snapshot(self, config, schema):
        if config is None:
            return None

        data_type = schema[MK.Type]
        if isinstance(data_type, configsuite.BasicType):
            return config
        elif data_type == configsuite.types.NamedDict:
            return self._build_named_dict_snapshot(config, schema)
        elif data_type == configsuite.types.List:
            return self._build_list_snapshot(config, schema)
        elif data_type == configsuite.types.Dict:
            return self._build_dict_snapshot(config, schema)
        else:
            msg = "Encountered unknown type {} while building snapshot"
            raise TypeError(msg.format(str(data_type)))

    def _validate_readability(self, layers):
        readable_errors = (configsuite.UnknownKeyError, configsuite.MissingKeyError)

        def _not_container(schema):
            return not isinstance(schema[MK.Type], configsuite.types.Collection)

        container_validator = configsuite.Validator(
            self._schema, stop_condition=_not_container, apply_validators=False
        )
        container_errors = []
        for idx, layer in enumerate(layers):
            val_res = container_validator.validate(layer)
            container_errors += [
                error.create_layer_error(idx)
                for error in val_res.errors
                if not isinstance(error, readable_errors)
            ]

        self._readable &= len(container_errors) == 0
        self._valid &= self._readable
        self._errors += tuple(container_errors)

    def _validate_final(self):
        if not self.readable:
            err_msg = "Internal error: Not readable when doing final validation"
            raise AssertionError(err_msg)
        self._assert_state()

        validator = configsuite.Validator(self._schema)
        val_res = validator.validate(self._merged_config, self._validation_context)
        self._valid &= val_res.valid
        self._errors += val_res.errors

    def _assert_state(self):
        """Asserts that the internal state is consistent. In particular we will
        verify that:
         - not readable => not valid
         - valid <=> no errors
        """
        if not self.readable and self.valid:
            err_msg = "Internal error: Config is valid, but not readable"
            raise AssertionError(err_msg)
        if self.valid and len(self.errors) > 0:
            err_msg = "Internal error: Config is valid, but has errors"
            raise AssertionError(err_msg)
        if not self.valid and len(self.errors) == 0:
            err_msg = "Internal error: Config is not valid, but has no errors"
            raise AssertionError(err_msg)
