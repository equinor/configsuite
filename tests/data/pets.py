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


import datetime
import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


def build_schema():
    @configsuite.validator_msg("Score should be non-negative")
    def _non_negative_score(elem):
        return elem > 0

    return {
        MK.Type: types.NamedDict,
        MK.Description: (
            "The PetMeet configuration is to give an overview of you and your "
            "pet to better be able to find a matching pet owner."
        ),
        MK.Content: {
            "name": {MK.Type: types.String, MK.Description: "Your full name."},
            "pet": {
                MK.Type: types.NamedDict,
                MK.Description: "Information about your pet.",
                MK.Content: {
                    "name": {MK.Type: types.String, MK.Description: "Name of the pet."},
                    "timestamp": {
                        MK.Type: types.DateTime,
                        MK.Description: "Record entry date.",
                    },
                    "favourite_food": {
                        MK.Type: types.String,
                        MK.Description: "Favourite food of the pet.",
                    },
                    "weight": {
                        MK.Type: types.Number,
                        MK.Description: "Weight of pet in tons.",
                    },
                    "nkids": {
                        MK.Type: types.Integer,
                        MK.Description: "Number of kids.",
                    },
                    "likeable": {
                        MK.Type: types.Bool,
                        MK.Description: "Is the pet likeable?",
                    },
                    "birthday": {
                        MK.Type: types.Date,
                        MK.Description: "Birthday of the pet.",
                    },
                },
            },
            "playgrounds": {
                MK.Type: types.List,
                MK.Description: "List of all playgrounds you take your pet to.",
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.NamedDict,
                        MK.Description: "Information about a playground.",
                        MK.Content: {
                            "name": {
                                MK.Type: types.String,
                                MK.Description: "Name of the playground.",
                            },
                            "score": {
                                MK.Type: types.Integer,
                                MK.Description: "Your score for the playground.",
                            },
                        },
                    }
                },
            },
            "veterinary_scores": {
                MK.Type: types.Dict,
                MK.Description: (
                    "List of all veterinaries you have taken your pet to."
                ),
                MK.Content: {
                    MK.Key: {
                        MK.Type: types.String,
                        MK.Description: "Name of the veterinary.",
                    },
                    MK.Value: {
                        MK.ElementValidators: (_non_negative_score,),
                        MK.Type: types.Number,
                        MK.Description: "Your score of the vet.",
                    },
                },
            },
        },
    }


def build_config():
    return {
        "name": "Markus",
        "pet": {
            "name": "Donkey Kong",
            "timestamp": datetime.datetime(2018, 5, 6, 12, 58, 22),
            "favourite_food": "bananas",
            "weight": 1.9,
            "nkids": 8,
            "likeable": True,
            "birthday": datetime.date(2018, 1, 1),
        },
        "playgrounds": [],
        "veterinary_scores": {"Dr. Dolittle": 10},
    }


def build_docs():
    return """The PetMeet configuration is to give an overview of you and your pet to better be able to find a matching pet owner.

**name*:**
    Your full name.

    :type: string

**pet*:**
    Information about your pet.

    **name*:**
        Name of the pet.

        :type: string

    **timestamp*:**
        Record entry date.

        :type: datetime

    **favourite_food*:**
        Favourite food of the pet.

        :type: string

    **weight*:**
        Weight of pet in tons.

        :type: number

    **nkids*:**
        Number of kids.

        :type: integer

    **likeable*:**
        Is the pet likeable?

        :type: bool

    **birthday*:**
        Birthday of the pet.

        :type: date

**playgrounds*:**
    List of all playgrounds you take your pet to.

    **<list_item>:**
            Information about a playground.

            **name*:**
                Name of the playground.

                :type: string

            **score*:**
                Your score for the playground.

                :type: integer

**veterinary_scores*:**
    List of all veterinaries you have taken your pet to.

    **<key>:**
            Name of the veterinary.

            :type: string
    **<value>:**
            Your score of the vet.

            :requirement: Score should be non-negative

            :type: number"""
