import enum
import collections

Type = collections.namedtuple('Type', ['name', 'validate', 'basic'])

Dict = Type('dict', lambda x: isinstance(x, dict), False)
String = Type('string', lambda x: isinstance(x, str), True)
