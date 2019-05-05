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

import configsuite
from configsuite import MetaKeys as MK


TransformationResult = collections.namedtuple(
    "TransformationResult", ("success", "errors", "result")
)


class Transformer(object):
    def __init__(
        self, schema, transformation_type, transformation_context, bottom_up=True
    ):
        self._schema = schema
        self._transformation_type = transformation_type
        self._transformation_context = transformation_context
        self._bottom_up = bottom_up
        self._errors = None

        self._debug = transformation_type == MK.ContextTransformation
        self._debug &= transformation_context is not None

    def transform(self, config):
        self._errors = []
        transformed_config = self._transform(config, self._schema, ())

        return TransformationResult(
            success=len(self._errors) == 0,
            errors=tuple(self._errors),
            result=transformed_config,
        )

    def _transform(self, config, schema, key_path):
        if not self._bottom_up:
            config = self._apply_single_transformation(config, schema, key_path)

        data_type = schema[MK.Type]
        if isinstance(data_type, configsuite.types.BasicType):
            pass
        elif data_type == configsuite.types.List:
            config = self._transform_list(config, schema, key_path)
        elif data_type == configsuite.types.NamedDict:
            config = self._transform_named_dict(config, schema, key_path)
        elif data_type == configsuite.types.Dict:
            config = self._transform_dict(config, schema, key_path)
        else:
            msg = "Encountered unknown type {} while building raw config"
            raise TypeError(msg.format(str(data_type)))

        if self._bottom_up:
            config = self._apply_single_transformation(config, schema, key_path)

        return config

    def _transform_list(self, config, schema, key_path):
        if not configsuite.types.List.validate(config):
            return config

        item_schema = schema[MK.Content][MK.Item]
        return tuple(
            [
                self._transform(item, item_schema, key_path + (idx,))
                for idx, item in enumerate(config)
            ]
        )

    def _transform_named_dict(self, config, schema, key_path):
        if not configsuite.types.NamedDict.validate(config):
            return config

        content_schema = schema[MK.Content]
        transformed_config = {}
        for key, value in config.items():
            if key not in content_schema:
                transformed_config[key] = value
                continue

            transformed_config[key] = self._transform(
                value, content_schema[key], key_path + (key,)
            )

        return transformed_config

    def _transform_dict(self, config, schema, key_path):
        if not configsuite.types.Dict.validate(config):
            return config

        key_schema = schema[MK.Content][MK.Key]
        value_schema = schema[MK.Content][MK.Value]

        transformed_config = {}
        for key, value in config.items():
            tkey = self._transform(key, key_schema, key_path + (key,))
            tval = self._transform(value, value_schema, key_path + (key,))
            transformed_config[tkey] = tval

        return transformed_config

    def _apply_single_transformation(self, config, schema, key_path):
        if self._transformation_type not in schema:
            return config

        transformation = schema[self._transformation_type]
        try:
            return transformation(config, *(self._transformation_context))
        # pylint: disable=broad-except
        except Exception as e:
            error_fmt = "'{}' failed on input '{}' with error '{}'"
            error_msg = error_fmt.format(transformation.msg, config, str(e))
            self._errors.append(configsuite.TransformationError(error_msg, key_path))

        return config
