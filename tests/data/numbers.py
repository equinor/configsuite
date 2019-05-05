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


import six

import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


@configsuite.transformation_msg("Convert ranges and singeltons into list")
def _realize_list(l):
    """If l is not a string, l will be returend. If l is a string it is assumed
    to contain comma separated elements. Each element is assumed to be either
    a singelton or a range. A singleton is a single number, i.e.  7 or 14. A
    range is a lower and upper element of the range separated by a single '-'.
    When provided with a string we will either return a list containing the
    union of all the singeltons and the ranges, or raise a TypeError or
    ValueError if it fails in the process.

    _realize_list('1,2,4-7,14-15') -> [1, 2, 4, 5, 6, 7, 14, 15]
    """
    if not isinstance(l, six.string_types):
        return l

    real_list = []
    for elem in l.split(","):
        bounds = elem.split("-")
        if len(bounds) == 1:
            if "-" in elem:
                raise ValueError("Did not expect '-' in singleton")
            real_list.append(int(elem))
        elif len(bounds) == 2:
            if elem.count("-") != 1:
                raise ValueError("Did expect single '-' in range")
            lower_bound = int(bounds[0])
            upper_bound = int(bounds[1]) + 1

            if lower_bound > upper_bound:
                err_msg = "Lower bound of range expected to be smaller then upper bound"
                raise ValueError(err_msg)

            real_list += range(lower_bound, upper_bound)
        else:
            raise ValueError("Expected at most one '-' in an element")

    return real_list


@configsuite.transformation_msg("Sort and remove duplicates in list")
def _unique_and_sorted(l):
    return tuple(sorted(set(l)))


def build_schema():
    return {
        MK.Type: types.List,
        MK.LayerTransformation: _realize_list,
        MK.Transformation: _unique_and_sorted,
        MK.Content: {MK.Item: {MK.Type: types.Integer}},
    }
