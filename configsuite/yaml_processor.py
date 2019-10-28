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

from yaml import SafeLoader, ScalarNode, SequenceNode, MappingNode


class DuplicateKeyError(Exception):
    def __init__(self, key_path, mark, first_mark):
        self._key_path = key_path
        self._mark = mark
        self._first_mark = first_mark

    def __str__(self):
        return "Duplicate key '{}' found:\n {}\nFirst occurrence:\n {}".format(
            self.key_path[-1], str(self.mark), self.first_mark
        )

    @property
    def key_path(self):
        return self._key_path

    @property
    def mark(self):
        return self._mark

    @property
    def first_mark(self):
        return self._first_mark

    def __eq__(self, other):
        return self._mark == other._mark

    def __neq__(self, other):
        return not (self == other)

    def __hash__(self):
        return hash(self._mark)


class YamlProcessor(object):
    def __init__(self, layer):
        self._documents = []
        self._key_path = []
        self._keys = {}

        self._load_layer(layer)

    def get_documents(self):
        return self._documents

    def get_mark(self, key_path):
        if key_path in self._keys:
            return self._keys[key_path]

    def _load_layer(self, layer):
        self._loader = SafeLoader(layer)
        while self._loader.check_node():
            node = self._loader.get_node()
            self._process_node(node)
            self._documents.append(self._loader.construct_document(node))

    def _process_node(self, node):
        if isinstance(node, ScalarNode):
            pass

        elif isinstance(node, SequenceNode):
            for idx, val in enumerate(node.value):
                self._key_path.append(idx)
                self._keys[tuple(self._key_path)] = val.start_mark

                self._process_node(val)
                self._key_path.pop()

        elif isinstance(node, MappingNode):
            keys = {}
            for key, val in node.value:
                assert isinstance(key, ScalarNode)
                obj = self._loader.construct_object(key)

                self._key_path.append(obj)

                if obj in keys:
                    raise DuplicateKeyError(self._key_path, key.start_mark, keys[obj])
                else:
                    keys[obj] = key.start_mark

                self._keys[tuple(self._key_path)] = val.start_mark

                self._process_node(val)
                self._key_path.pop()
