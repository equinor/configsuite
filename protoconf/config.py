import copy
import protoconf
import collections


class ConfigSuite(object):

    def __init__(self, raw_config, schema):
        self._raw_config = copy.deepcopy(raw_config)
        self._schema = copy.deepcopy(schema)
        self._valid = None
        self._snapshot = None

    @property
    def valid(self):
        if self._valid is None:
            validator = protoconf.Validator(self._schema)
            val_res = validator.validate(self._raw_config)
            self._valid = val_res.valid

        return self._valid

    @property
    def snapshot(self):
        if self._snapshot is None:
            self._snapshot = self._build_snapshot(
                    self._raw_config,
                    self._schema,
                    )

        return self._snapshot

    def _build_snapshot(self, config, schema):
        data_type = schema[protoconf.MetaKeys.Type]
        if data_type.basic:
            return config
        elif data_type == protoconf.types.Dict:
            dict_name = data_type.name
            dict_keys = config.keys()
            dict_collection = collections.namedtuple(dict_name, dict_keys)

            child_schema = schema[protoconf.MetaKeys.Content]
            return dict_collection(**{
                key: self._build_snapshot(config.get(key), child_schema[key])
                for key in child_schema
            })
        else:
            msg = 'Encountered unknown type {} while building snapshot'
            raise TypeError(msg.format(str(data_type)))
