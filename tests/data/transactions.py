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
from configsuite import types


@configsuite.validator_msg("Currency rate should not be negative")
def _positive_rate(rate):
    return rate > 0


@configsuite.validator_msg("Amount should not be negative")
def _positive_amount(amount):
    return amount > 0


@configsuite.validator_msg("Should be defined currency")
def _is_currency(elem, context):
    return elem in context.currencies


def build_schema():
    return {
        MK.Type: types.NamedDict,
        MK.Content: {
            "exchange_rates": {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: {MK.Type: types.String},
                    MK.Value: {
                        MK.Type: types.Number,
                        MK.ElementValidators: (_positive_rate,),
                    },
                },
            },
            "transactions": {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            "source": {
                                MK.Type: types.String,
                                MK.ContextValidators: (_is_currency,),
                            },
                            "target": {
                                MK.Type: types.String,
                                MK.ContextValidators: (_is_currency,),
                            },
                            "amount": {
                                MK.Type: types.Number,
                                MK.ElementValidators: (_positive_amount,),
                            },
                        },
                    }
                },
            },
        },
    }


def build_config():
    return {
        "exchange_rates": {
            "NOK": 1,
            "EUR": 9.67,
            "USD": 8.68,
            "FLC": 0.0024,
            "Bitcoin": 0.000022,
        },
        "transactions": [
            {"source": "NOK", "target": "USD", "amount": 1000},
            {"source": "Bitcoin", "target": "EUR", "amount": 1},
            {"source": "FLC", "target": "FLC", "amount": 0.001},
        ],
    }


def extract_validation_context(configuration):
    currencies = ()
    if configuration.exchange_rates is not None:
        currencies = tuple([cur_name for cur_name, _ in configuration.exchange_rates])

    Context = collections.namedtuple("Context", ("currencies"))
    return Context(currencies)
