Getting started
===============

A first glance
--------------

For now we will just assume that we have a schema that describes the expected
input. Informally say that we have a very simple configuration where one can
specify ones name and hobby, i.e:

.. code-block:: yaml

    name: espen askeladd
    hobby: collecting stuff

You can then instantiate a suite as follows:

.. code-block:: python

    import configsuite

    with open('config.yml') as f:
        input_config = yaml.load(f)

    suite = configsuite.ConfigSuite(input_config, schema)

You can now check whether data provided in ``input_config`` is valid by accessing
``suite.valid``.

.. code-block:: python

    if suite.valid:
        print("Congratulations! The config is valid.")
    else:
        print("Sorry, the configuration is invalid.")

Now, given that the configuration is indeed valid you would probably like to
access the data. This can be done via the ``ConfigSuite`` member named
``snapshot``. Hence, we could change our example above to:

.. code-block:: python

    if suite.valid:
        msg = "Congratulations {name}! The config is valid. Go {hobby}."
        msg = msg.format(
            name=suite.snapshot.name,
            hobby=suite.snapshot.hobby,
        )
        print(msg)
    else:
        print("Sorry, the configuration is invalid.")

And if feed the example configuration above the output would be::

    Congratulations Espen Askelad! The config is valid. Go collect stuff.

However, if we changed the value of ``name`` to ``13`` (or even worse ``["My", "name", "is kind", "of odd"]``) we would expect the configuration to be invalid and hence that the output would be ``Sorry, the configuration is invalid``. And as useful as this is it would be even better to gain more detailed information about the errors.

.. code-block:: python

    print(suite.errors)
    (
        InvalidTypeError(
            msg=Is x a string is false on input 13,
            key_path=('hobby',),
            layer=None,
        ),
    )

.. code-block:: python

    if suite.valid:
        msg = "Congratulations {name}! The config is valid. Go {hobby}."
        msg = msg.format(
            name=suite.snapshot.name,
            hobby=suite.snapshot.hobby,
        )
        print(msg)

    else:
        print("Sorry, the configuration is invalid.")
        print(suite.errors)

A first schema
~~~~~~~~~~~~~~

The below schema is indeed the one used in our example above. It consists of a
single collection containing the two keys ``name`` and ``hobby``, both of which
value should be a string.

from configsuite import types
from configsuite import MetaKeys as MK

.. code-block:: python

    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "name": {MK.Type: types.String},
            "hobby": {MK.Type: types.String},
        }
    }

Notice the usage of the meta key ``Type`` to specify the type of a specific
element and the usage of ``Content`` to specify the content of a container.

Types
-----

In *Config Suite* we differentiate between *basic types* and *collections*.
Basic types are single valued entities, while collections are data structures
that can hold multiple basic types. In our first example the entire
configuration was considered a collection (of type ``Named dict``), while ``name``
and ``hobby`` are basic types. And while you can define arbitrary *basic types*,
one cannot create new *collections* while using *Config Suite*.

Basic types
~~~~~~~~~~~

We will now give a brief introductory to the *basic types*. All of them can be
utilized in a schema by utilizing the ``MK.Type`` keyword as displayed above.
For an introduction to how one can implement user defined *basic types* we
refer the reader to the advanced section.

String
~~~~~~
We have already seen the usage of the ``String`` type above. It basically accepts
everything considered a string in Python (defined by ``six.string_types``).

Integer
~~~~~~~
An ``Integer`` is as the name suggests an integer.

Number
~~~~~~
When a ``Number`` is specified any integer or floating point value is accepted.

Bool
~~~~
Both boolean values ``True`` and ``False`` are accepted.

Date
~~~~
A date in specified in ISO-format, ``[YYYY]-[MM]-[DD]`` that is.

DateTime
~~~~~~~~
A date and time is expected in ISO-format (``[YYYY]-[MM]-[DD]T[hh]:[mm]:[ss]``).

Collections
~~~~~~~~~~~
We will now explore the supported *collections*. These will form the backbone
of your configuration. In short, if you have a dictionary where you know the keys
up front, you are looking for a *Named dict*, if you have dictionary with
arbitrary keys, you are looking for a *Dict*. If you have a sequence of elements,
you should check out *List*.

Named dict
~~~~~~~~~~
We have already seen the usage of a *Named dict*. In particular, it allows for
mapping values (of potentially different types) to names that we know up front.
This allows us to represent them as attributes of the snapshot (or an sub
element of the snapshot). In general, if you know the values of all of the keys
up front, then a named dict is the right container for you.

.. code-block:: python

    from configsuite import types
    from configsuite import MetaKeys as MK

    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "owner": {
                MK.type: types.NamedDict,
                MK.Content: {
                    "name": {MK.type: types.String},
                    "credit": {MK.type: types.Number},
                    "insured": {MK.type: types.Bool},
                },
            },
            "car": {
                MK.Type: types.NamedDict,
                MK.Content: {
                    "brand": {MK.type: types.String},
                    "first_registered": {MK.Type: types.Date}
                },
            },
        },
    }

the above example describes a configuration describing both an ``owner`` and a
``car``. for the ``owner`` the ``name``, ``credit`` and whether she is ``insured`` is to
be specified, while for the ``car`` the ``brand`` and date it was
``first_registered`` is specified. a valid configuration could look something
like this:

.. code-block:: yaml

    owner:
      name: Donald Duck
      credit: -1000
      insured: true

    car:
      brand: Belchfire Runabout
      first_registered: 1938-07-01

and now, we could validate and access the data as follows:

.. code-block:: python

    # ... configuration is loaded into 'input_config' ...

    suite = configsuite.ConfigSuite(input_config, schema)

    if suite.valid:
        print("name of owner is {}".format(
            suite.snapshot.owner.name
        ))
        print("car was first registered {}".format(
            suite.snapshot.car.first_registered
        ))

Notice that since keys in a named dict are made attributes in the snapshot,
they all have to be valid Python variable names.

List
~~~~
Another supported container is the ``List``. The data should be bundled together
either in a Python ``list`` or a ``tuple``. A very concrete difference of a Config
Suite list and a Python list is that in Config Suite all elements are expected
to be of the same type. This makes for an easier format for the user as well as
the programmer when one is dealing with configurations. A very simple example
representing a list of integers would be as follows:

.. code-block:: python

    import configsuite
    from configsuite import types
    from configsuite import MetaKeys as MK

    schema = {
        MK.Types: types.List,
        MK.Content: {
            MK.Item: {
                MK.Type: types.Integer,
            },
        },
    }

    config = [1, 1, 2, 3, 5, 7, 13]

    suite = configsuite.ConfigSuite(config, schema)

    if suite.valid:
        for idx, value in enumerate(suite.snapshot):
            print("config[{}] is {}".format(idx, value))

A more complex example can be made by considering our example from the
``NamedDict`` section and imagining that an ``owner`` could have multiple ``cars``
that was to be contained in a list.

.. code-block:: python

    from configsuite import types
    from configsuite import MetaKeys as MK

    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "owner": {
                MK.type: types.NamedDict,
                MK.Content: {
                    "name": {MK.type: types.String},
                    "credit": {MK.type: types.Float},
                    "insured": {MK.type: types.Bool},
                },
            },
            "cars": {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            "brand": {MK.type: types.String},
                            "first_registered": {MK.Type: types.Date}
                        },
                    },
                },
            },
        },
    }

    config = {
        "owner": {
          "name": Donald Duck,
          "credit": -1000,
          "insured": True,
        },
        "cars": [
            {
              "brand": "Belchfire Runabout",
              "first_registered": datetime.Date(1938, 7, 1),
            },
            {
              "brand": "Duckworth",
              "first_registered": datetime.Date(1987, 9, 18),
            },
        ]
    }

    suite = configsuite.ConfigSuite(config, schema)

    if suite.valid:
        print("name of owner is {}".format(suite.snapshot.owner.name))
        for car in suite.snapshot.cars:
            print("- {}".format(car.brand))

Notice that ``suite.snapshot.cars`` is returned as a ``tuple``-like structure. It
is iterable, indexable (``suite.snapshot.cars[0]``) and immutable.

Dict
~~~~
The last of the data structures is the ``Dict``. Contrary to the ``NamedDict`` one
does not need to know the keys upfront and in addition the keys can be of other
types than just ``strings``. However, the restriction is that all the keys needs
to be of the same type and all the values needs to be of the same type. The
rationale for this is similar to that one of the list. Uniform types for
arbitrary sized configurations are easier and better, both for the user and the
programmer. A simple example mapping animals to frequencies are displayed below.

.. code-block:: python

    import configsuite
    from configsuite import types
    from configsuite import MetaKeys as MK

    schema = {
        MK.Type: types.Dict,
        MK.Content: {
            MK.Key: {MK.Type: types.String},
            MK.Value: {MK.Type: types.Integer},
        },
    }

    config = {
        "monkey": 13,
        "donkey": 16,
        "horse": 28,
    }

    suite = configsuite.ConfigSuite(config, schema)
    assert suite.valid:

    for animal, frequency in suite.snapshot:
        print("{} was observed {} times".format(animal, frequency))

As you can see, the elements of a ``Dict`` is accessible in ``(key, value)`` pairs
in the same manner ``dict.items`` would provide for a Python dictionary. The
reason for not supporting indexing by key is ``Dict``, contrary to ``NamedDict``,
is for dictionaries with an unknown set of keys. Hence, processing them as
key-value-pairs is the only rational thing to do.

Configuration readiness
-----------------------

A very central concept in *Config Suite* is that of configuration readiness.
Given that our configuration is indeed valid we can trust that
``suite.snapshot`` will describe all values as defined in the schema and that
all the values are valid. Hence, we do not need to check for availability nor
correctness of the configuration.

Readable
~~~~~~~~
The concept of configuration readiness implies one specified a value in the
schema, one is to expect that that piece of data is indeed present in the
snapshot. But what if the configuration feed to the suite is not valid? If the
errors appear in basic types, one can still access all the data as expected
(i.e. ``config.snapshot.owner.name`` from the car example above).  However, if
a container is of the wrong type on cannot guarantee such a thing.  In
particular, if we bring back the single-car example from above and consider the
following configuration:

.. code-block:: yaml


    owner:
      name: Donald Duck
      credit: -1000
      insured: true

    car:
      - my first car
      - my second car

The ``car`` data is completely off and there is no way one could provide a
reasonable value for ``config.snapshor.car.brand``. In such scenarios the
configuration is deemed *unreadable*. There is a special marker for this,
namely ``ConfigSuite.readable``. If ``readable`` is true, then the snapshot can be
built and all the entire configuration can be accessed. However, if the suite
is not ``readable`` and one tries to fetch the snapshot an ``AssertionError`` will
be raised.

Note that all valid suites also are readable. And that all unreadable suites
also are invalid.

Default values
-----------------------------

So far all entries in your configuration file have been mandatory to fill in.
And if some key in a Named dict would be missing a ``MissingKeyError`` would be
registered. However, this is not always the wanted behaviour. By using the
``MetaKeys.Required`` option you can control whether a key is indeed required.
You could change the ``cars`` schema above such that ``credit`` would be optional
as follows:

.. code-block:: python

    from configsuite import types
    from configsuite import MetaKeys as MK

    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "owner": {
                MK.type: types.NamedDict,
                MK.Content: {
                    "name": {MK.Type: types.String},
                    "credit": {
                        MK.Type: types.Float,
                        MK.Required: False,
                    },
                    "insured": {MK.Type: types.Bool},
                },
            },
            "cars": {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            "brand": {MK.Type: types.String},
                            "first_registered": {MK.Type: types.Date}
                        },
                    },
                },
            },
        },
    }

And then if no ``credit`` was specified a ``MissingKeyError`` would not be
registered. However, recall the principle of configuration readiness. Since,
the programmer should not have to special case whether or not the value is
present in the ``snapshot``. The ``snapshot`` is always built based on the schema
and hence ``suite.snapshot.owner.credit`` would indeed be an attribute
independently of whether the user has configured it. In this scenario the value
of ``suite.snapshot.owner.credit`` would be ``None``. To configure the default
value to something else then ``None``, we refer the reader to the next section.

How to specify default values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
We have planned two ways of providing default values in Config Suite. You are
to either specify it in the schema via the keyword ``MetaKeys.Default`` (NOTE:
This is yet to be implemented!). This has the advantage of being able to provide default
values inside list-elements. The disadvantage is that you would need to edit
the code to change the default values and hence site or project specific
defaults are not suited for this purpose. The second, and currently only
implemented, way of specifying default are via ``layers``.

Note that no element should be both required and have a given ``Default`` value.

Layers
------

Layers is a fundamental concept in Config Suite that enables you to retrieve
configurations from multiple sources in a consistent manner. It can be utilized
to give priority to different sources, being application defaults, installation
defaults, project or user settings, as well as case specific configuration. It
can also be utilized to reprent changes in configuration from a UI in a
consistent manner.

In short, a layer is, a possibly incomplete, configuration source. Multiple
layers can be stacked on top of each other to form a single configuration. In
such a stack, top layers take precedence over lower layers. For each of the
types there are specific rules for how that type is merged when multiple layers
are combined into a single value.

Layers can be passed to a suite via the keyword argument ``layers``. In
particular, if constructed as follows

.. code-block:: python

    suite = configsuite.ConfigSuite(
        config,
        schema,
        layers=(middle_layer, bottom_layer),
    )

This will result in the layers ``(config, middle_layer, bottom_layer)``, where
elements in ``config`` takes precedence over the two other layers and the
elements in ``middle_layer`` over elements in ``bottom_layer``.

Basic types
~~~~~~~~~~~
Basic types are simply overwritten and only the value from the top most layer
specifying that value is kept.

Named dicts and dicts
~~~~~~~~~~~~~~~~~~~~~
Named dicts and dicts are by default joined in an update kind of fashion. All
the values are joined recursively, key by key. This implies that for the
``cars``-example with the following layers:

.. code-block:: yaml

    # Lower level
    owner:
      name: Donald Duck
      credit: 100

.. code-block:: yaml

    # Upper level
    owner:
      name: Scrooge McDuck
      insured: True

would result in the following after being merged:

.. code-block:: yaml

    # Merged configuration
    owner:
      name: Scrooge McDuck
      credit: 100
      insured: True

Lists
~~~~~
Lists are by default appended, with the top layer elements appearing after
lower levels. If we again lock at the ``cars``-example:

.. code-block:: yaml

    # Lower level
    cars:
      -
        brand: Belchfire Runabout
        first_registered: 1938-7-1
      -
        brand: Duckworth
        first_registered: 1987-9-18

.. code-block:: yaml

    # Upper level
    cars:
      -
        brand: Troll
        first_registered: 1956-11-6

would result in the following after being merged:

.. code-block:: yaml

    # Merged configuration
    cars:
      -
        brand: Belchfire Runabout
        first_registered: 1938-7-1
      -
        brand: Duckworth
        first_registered: 1987-9-18
      -
        brand: Troll
        first_registered: 1956-11-6

Documentation generation
------------------------

Currently *Config Suite* have rather limited functionality for generating
documentation. This is to be improved in the future. Currently, you can pass
your schema to ``configsuite.docs.generate`` and it will generate documentation
as `reStructuredText <http://docutils.sourceforge.net/rst.html>`_.

Validators
----------

Validators enables validation beyond the type validation. As a first example,
let us say that you have a value in your configuration that should only contain
characters from the alphabet and spaces. This would be a quite natural
validation of the ``name`` field in our first example.

First, you need to write a function that validates the requirements above and
returns its result as a boolean.

.. code-block:: python

    @configsuite.validator_msg("Is x a valid name")
    def _is_name(name):
        return all(char.isalpha() or char.isspace() for char in name)

Notice the decorator ``validator_msg``. This adds a statement regarding the
purpose of the validator to the validator and a statement regarding the result
of the validation to the returned result. These messages are used both if a validator
fails to register errors as well as to generate documentation. In particular:

.. code-block:: python

    >>> _is_name.msg
    'Is x a valid name'

    >>> _is_name("1234").msg
    "Is x a valid name is false on input '1234'"

    >>> _is_name("My Name").msg
    "Is x a valid name is true on input 'My Name'"

Afterwards, you can add this to your schema as follows:

.. code-block:: python

    from configsuite import types
    from configsuite import MetaKeys as MK

    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "name": {
                MK.Type: types.String,
                MK.ElementValidator: _is_name,
            },
            "hobby": {MK.Type: types.String},
        }
    }

Notice that we do not have to check that the input is a string. This is because
type validation is always carried out first and the validator is only applied
if the type validation succeeded.

Transformations
---------------

Transformations enables changing the data in the merged configuration before it
is validated and the snapshot becomes accessible. A simple example of this is
that you would like to support scientific notation for numbers in your
configuration files. This is a well-known short coming of *PyYAML*. In
particular, you would like the ``cars`` example to support the following:

.. code-block:: yaml

    owner:
      name: Donald Duck
      credit: -1e10
      insured: true

However, loading the above from a ``yml``-file would yield the following data:

.. code-block:: python

    "owner": {
      "name": "Donald Duck",
      "credit": "-1e10",
      "insured": True,
    }

Note that the value of ``credit`` is a string. However, it is easy to write a
transformer for this purpose.

.. code-block:: python

    _num_convert_msg = "Tries to convert input to a float"
    @configsuite.transformation_msg(_num_convert_msg)
    def _to_float(num):
        return float(num)

And now, we can insert this into the schema as follows:

.. code-block:: python

    from configsuite import types
    from configsuite import MetaKeys as MK

    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "owner": {
                MK.type: types.NamedDict,
                MK.Content: {
                    "name": {MK.Type: types.String},
                    "credit": {
                        MK.Type: types.Float,
                        MK.Required: False,
                        MK.Transformator: _to_float,
                    },
                    "insured": {MK.Type: types.Bool},
                },
            },
            "cars": {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.NamedDict,
                        MK.Content: {
                            "brand": {MK.Type: types.String},
                            "first_registered": {MK.Type: types.Date}
                        },
                    },
                },
            },
        },
    }

As a final note about transformations it should be said that currently *Config
Suite* does not validate readability in between transformations. This implies
that if a transformations has the capability of changing the data type of a
collection, then the promise of the transformations being provided with data of
the correct type is only true as long as the transformations preserve this
while being applied.

