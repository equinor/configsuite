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
    def __init__(self, raw_config, schema, layers=()):
        assert_valid_schema(schema)
        self._layers = tuple(
            [copy.deepcopy(layer) for layer in tuple(layers) + (raw_config,)]
        )
        self._cached_raw_config = None
        self._schema = copy.deepcopy(schema)
        self._snapshot = None
        self._valid = None
        self._errors = None
        self._readable = None
        self._validate()
        self._assert_state()

    @property
    def valid(self):
        return self._valid

    @property
    def errors(self):
        if len(self._layers) == 1 and self.readable:
            return tuple([err for err in self._errors if err.layer is None])

        return self._errors

    @property
    def readable(self):
        return self._readable

    @property
    def snapshot(self):
        if not self.readable:
            err_msg = "Cannot build snapshot of unreadable configuration."
            raise AssertionError(err_msg)

        if self._snapshot is None:
            self._snapshot = self._build_snapshot(self._raw_config, self._schema)

        return self._snapshot

    def push(self, raw_config):
        return ConfigSuite(raw_config, self._schema, self._layers)

    @property
    def _raw_config(self):
        """The raw config cannot be built and will also not be utilized if the
        config is not readable. Due to this it is built lazily.
        """
        if not self.readable:
            err_msg = (
                "Internal error: Cannot build raw_config of unreadable configuration."
            )
            raise AssertionError(err_msg)

        if self._cached_raw_config is None:
            self._cached_raw_config = self._build_raw_config(self._layers, self._schema)

        return self._cached_raw_config

    def _build_raw_config(self, layers, schema):
        data_type = schema[MK.Type]
        if isinstance(data_type, configsuite.types.BasicType):
            return layers[-1]
        elif data_type == configsuite.types.List:
            item_schema = schema[MK.Content][MK.Item]
            config = []
            for layer in layers:
                config += [
                    self._build_raw_config((item,), item_schema) for item in layer
                ]
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
                    config[key] = self._build_raw_config(
                        child_layers, content_schema[key]
                    )
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
                config[key] = self._build_raw_config(
                    child_layers, content_schema[MK.Value]
                )
            return config
        else:
            msg = "Encountered unknown type {} while building raw config"
            raise TypeError(msg.format(str(data_type)))

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
            sorted(
                [
                    Pair(
                        self._build_snapshot(key, key_schema),
                        self._build_snapshot(value, value_schema),
                    )
                    for key, value in config.items()
                ]
            )
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

    def _validate_layers(self):
        validator = configsuite.Validator(self._schema)

        errors = []
        for idx, layer in enumerate(self._layers):
            val_res = validator.validate(layer)
            errors += [error.create_layer_error(idx) for error in val_res.errors]

        def _not_dict(schema):
            dict_types = (configsuite.types.Dict, configsuite.types.NamedDict)
            return schema[MK.Type] not in dict_types

        dict_validator = configsuite.Validator(self._schema, stop_condition=_not_dict)
        dict_missing_errors = []
        for idx, layer in enumerate(self._layers):
            val_res = dict_validator.validate(layer)
            dict_missing_errors += [
                error.create_layer_error(idx)
                for error in val_res.errors
                if isinstance(error, configsuite.MissingKeyError)
            ]

        errors = tuple(set(errors) - set(dict_missing_errors))
        self._valid &= len(errors) == 0
        self._errors += tuple(errors)

    def _validate_readability(self):
        readable_errors = (configsuite.UnknownKeyError, configsuite.MissingKeyError)

        def _not_container(schema):
            return not isinstance(schema[MK.Type], configsuite.types.Collection)

        container_validator = configsuite.Validator(
            self._schema, stop_condition=_not_container
        )
        container_errors = []
        for idx, layer in enumerate(self._layers):
            val_res = container_validator.validate(layer)
            container_errors += [
                error.create_layer_error(idx)
                for error in val_res.errors
                if not isinstance(error, readable_errors)
            ]

        self._readable &= len(container_errors) == 0
        self._valid &= self._readable
        self._errors += tuple(container_errors)

    def _validate(self):
        self._valid = True
        self._readable = True
        self._errors = ()

        self._validate_readability()
        if not self.readable:
            return

        self._validate_layers()

        validator = configsuite.Validator(self._schema)
        val_res = validator.validate(self._raw_config)
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
