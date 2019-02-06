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


import unittest
import sys


import configsuite
from configsuite import MetaKeys as MK
from configsuite import types


def _build_pet_docs_schema():
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


def _build_expected_docs():
    return """The PetMeet configuration is to give an overview of you and your pet to better be able to find a matching pet owner.

**name*:**
    Your full name.

    :type: string

**pet*:**
    Information about your pet.

    **name*:**
        Name of the pet.

        :type: string

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


class TestDocGen(unittest.TestCase):
    @unittest.skipIf(sys.version_info < (3, 6), reason="requires python3.6 or higher")
    def test_doc_generate(self):
        """This test is skipped for Python versions prior to 3.6 due to those
        not preserving the order of a dictionary (it is technically not a part
        of the API of 3.6 either, but it is how it is implemented) and hence
        not the output of the doc.generate either.
        """
        schema = _build_pet_docs_schema()
        docs = configsuite.docs.generate(schema)

        exp_docs = _build_expected_docs()
        self.assertEqual(exp_docs, docs)

    def test_doc_generate_weak(self):
        """This is a much weaker version of the test_doc_generate. It still
        checks that the generator gives output that could possibly be the same
        as the proper test.
        """
        schema = _build_pet_docs_schema()
        docs = configsuite.docs.generate(schema)

        exp_docs = _build_expected_docs()
        self.assertEqual(sorted(exp_docs), sorted(docs))
