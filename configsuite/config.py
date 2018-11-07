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

    def __init__(self, raw_config, schema):
        assert_valid_schema(schema)
        self._raw_config = copy.deepcopy(raw_config)
        self._schema = copy.deepcopy(schema)
        self._valid = None
        self._errors = None
        self._snapshot = None

    @property
    def valid(self):
        self._ensure_validation()
        return self._valid

    @property
    def errors(self):
        self._ensure_validation()
        return self._errors

    @property
    def snapshot(self):
        if self._snapshot is None:
            self._snapshot = self._build_snapshot(
                    self._raw_config,
                    self._schema,
                    )

        return self._snapshot

    def _build_snapshot(self, config, schema):
        if config is None:
            return None

        data_type = schema[MK.Type]
        if isinstance(data_type, configsuite.BasicType):
            return config
        elif data_type == configsuite.types.NamedDict:
            content_schema = schema[MK.Content]
            dict_name = data_type.name
            dict_keys = content_schema.keys()
            dict_collection = collections.namedtuple(dict_name, dict_keys)

            return dict_collection(**{
                key: self._build_snapshot(config.get(key), content_schema[key])
                for key in content_schema
            })
        elif data_type == configsuite.types.List:
            item_schema = schema[MK.Content][MK.Item]
            return tuple(map(
                lambda elem: self._build_snapshot(elem, item_schema),
                config
            ))
        elif data_type == configsuite.types.Dict:
            key_schema = schema[MK.Content][MK.Key]
            value_schema = schema[MK.Content][MK.Value]

            Pair = collections.namedtuple('KeyValuePair', ['key', 'value'])
            return tuple([
                Pair(
                    self._build_snapshot(key, key_schema),
                    self._build_snapshot(value, value_schema)
                )
                for key, value in config.items()
            ])
        else:
            msg = 'Encountered unknown type {} while building snapshot'
            raise TypeError(msg.format(str(data_type)))

    def _ensure_validation(self):
        if self._valid is None:
            validator = configsuite.Validator(self._schema)
            val_res = validator.validate(self._raw_config)
            self._valid = val_res.valid
            self._errors = val_res.errors
