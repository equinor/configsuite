import copy
import type_name
import collections


class ConfigSuite(object):

    def __init__(self, raw_config, schema):
        self._raw_config = copy.deepcopy(raw_config)
        self._schema = copy.deepcopy(schema)
        self._snapshot = None

    @property
    def snapshot(self):
        if self._snapshot is None:
            self._snapshot = self._build_snapshot(
                    self._raw_config,
                    self._schema,
                    )

        return self._snapshot

    def _build_snapshot(self, config, schema):
        data_type = schema[type_name.MetaKeys.Type]
        if data_type.basic:
            return config
        elif data_type == type_name.types.Dict:
            dict_name = data_type.name
            dict_keys = config.keys()
            dict_collection = collections.namedtuple(dict_name, dict_keys)

            child_schema = schema[type_name.MetaKeys.Content]
            return dict_collection(**{
                key: self._build_snapshot(config.get(key), child_schema[key])
                for key in child_schema
            })
        else:
            msg = 'Encountered unknown type {} while building snapshot'
            raise TypeError(msg.format(str(data_type)))
