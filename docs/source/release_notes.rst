Release Notes
=============

.. Release note sections:
   New features
   Improvements
   Bugfixes
   Deprecations
   Dependencies
   Miscellaneous


dev
---

0.6.6 (2021-01-05)
------------------

**Miscellaneous**
 - Stop running CI on Travis and move PyPI deploy to GitHub Actions

0.6.5 (2020-11-27)
------------------

**New features**
 - Add possibility in schema to specify whether a variable length container (list or dict) is allowed to be empty

**Miscellaneous**
 - Replace usage of deprecated inspect methods

0.6.4 (2020-09-25)
------------------

**Improvements**
 - Validate that content is specified in schema if and only if element is a container.

**Deprecations**
 - Drop Python 2.7 support

**Dependencies**
 - Remove dependency on six

0.6.3 (2020-07-01)
------------------

**Improvements**
 - Have the Sphinx plugin only render examples if they are provided

**Bugfix**
 - Make the Sphinx plugin's CSS changes local to the plugin

0.6.2 (2020-06-10)
------------------

**Improvements**
 - Better validation message for incompatible required value

**Bugfix**
 - Pass on `deduce_required` when pushing

0.6.1 (2020-06-03)
------------------

**Improvements**
 - Add empty line between keys and values in auto generated rst documentation
   to avoid warning on empty descriptions

**Bugfix**
 - Default all containers to the empty container

0.6.0 (2020-05-28)
------------------

**New features**
 - Specify elements to be allowed to take None as value
 - Specify default values for elements in the schema
 - Generate documentation from schema a Sphinx plugin

**Improvements**
 - Python 3.8 support

**Deprecations**
 - Specifying elements as Required in the schema
 - Python 3.4 support

**Miscellaneous**
 - Use `flake8` as part of the CI pipeline
 - Have the CI pipeline ensure that the docs builds without warnings
 - Add GitHub actions as another CI provider
 - Validate internal meta schema in the tests

**Dependencies**
 - The following install dependencies have been added: `docutils`, `PyYAML` and
   `sphinx`

0.5.3 (2019-11-14)
------------------

**Improvements**
 - Make sure all examples in the documentation is valid and run them in the
   test suite

0.5.2 (2019-08-30)
------------------

**Improvements**
 - Various improvements to the documentation

0.5.1 (2019-06-14)
------------------

**Improvements**
 - Fix typos in the documentation

0.5.0 (2019-06-13)
------------------

**New features**
 - Support context validation for containers

**Improvements**
 - Allow for chaining `BooleanResults`, and hence transformations and validators

0.4.2 (2019-05-19)
------------------

**Miscellaneous**
 - Improve information in setup.py

0.4.1 (2019-05-19)
------------------

**Bugfixes**
 - Extractors are now passed to new suite when pushing layers

**New features**
 - Initial documentation written and hosted at read the docs

**Miscellaneous**
 - Minor code improvements

0.4.0 (2019-05-07)
------------------

**New features**
 - Support for context validation
 - Support for layer transformations, transformations and context transformations

**Improvements**
 - Remove layer validation
 - Accept unicode strings as strings
 - No sorting of dict keys

0.3.1 (2019-04-29)
------------------

**Bugfixes**
 - Fix various errors regarding imports

0.3.0 (2019-04-26)
------------------

**Bugfixes**
 - Fix docs import in configsuite's init-file

**New features**
 - New basic types `Date` and `DateType`

**Dependencies**
 - Add six to Python 2 dependencies

0.2.1 (2019-04-12)
------------------

**Bugfixes**
 - Add description to meta schema

**Miscellaneous**
 - Various code improvements due to PyLint

0.2.0 (2019-04-03)
------------------

**New features**
 - Documentation generating capabilities from the specification
 - Support for layered configurations

0.1.0 (2018-11-08)
------------------

**New features**
 - Initial validation and snapshot implementation
 - Validation of schema
 - Support for basic types: int, string, number and bool
 - Support for containers: list, named_dict and dict
 - Support for non-required dict keys
