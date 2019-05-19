Advanced Usage
==============

Creating your own types
-----------------------

Config Suite supports you creating your own basic types. This is done by
creating a new instance of ``configsuite.BasicType``. The constructor takes a
type name, as well as a validator of the type. For instance, the ``Date``
type in Config Suite could be implemented as follows:

.. code-block:: python

    @configsuite.validator_msg("Is x a date")
    def _is_date(x):
        return isinstance(x, datetime.date)

    Date = configsuite.BasicType("date", _is_date)

After this, you can use ``Date`` as a ``MetaKeys.Type`` value in your schema as
displayed in the ``cars``-schema.

Context validators
------------------

Context validators enables validation of an entry based on the value of entries
located elsewhere in the configuration. This is a two-step procedure; where the
first step is a consumer-defined function for extracting context of a snapshot.
The given snapshot is guaranteed to be readable and is extracted after all
transformations have been applied. Then, after an element have been validated
recursively and the element validator has been applied, if the element is still
deemed valid, the context validator is applied.

The typical application of a context validator is when you have multiple,
central concepts in your configuration. An example would be a configuration of
students and classes. You want to enable specification of both students and
classes, yet you also want to list the students attending each class. 

.. code-block:: python

    import collection

    import configsuite
    from configsuite import MetaKeys as MK
    from configsuite import types


    _student_schema = {
        MK.Type: types.List,
        MK.Content: {
            MK.Item: {
                MK.Type: types.NamedDict,
                MK.Content: {
                    "name": {MK.Type: types.String},
                    "age": {MK.Type: types.Integer},
                    "favourite_lunch": {MK.Type: types.String}
                },
            },
        },
    }


    @configsuite.validatior_msg("Is x a student name")
    def _is_student(name, context):
        return name in context.student_names


    _course_schema = {
        MK.Type: types.List,
        MK.Content: {
            MK.Item: {
                MK.Type: types.NamedDict,
                MK.Content: {
                    "name": {MK.Type: types.String},
                    "max_size": {MK.Type: types.Integer},
                    "students": {
                        MK.Type: types.List,
                        MK.Content: {
                            MK.Item: {
                                MK.Type: types.String,
                                MK.ContextValidator: _is_student, 
                            },
                        },
                    },
                },
            },
        },
    }


    schema = {
        "students": _student_schema,
        "courses": _course_schema,
    }


    def _extract_student_names(snapshot):
        Context = collection.namedtuple("Context", ("student_names",))
        student_names = tuple(
            student.name for student in snapshot.students
        )
        return Context(student_names=student_names)

Note that we have split the schema in two in this example to keep it a bit more
manageable. Also, observe how ``_is_student`` takes both a ``name`` (which we know
is a ``string``) as well as a ``context``. Besides that, we had to implement a
function that extracts the ``context`` from a snapshot. Notice that we are in
complete control of the ``context``, which means that we could have returned the
entire snapshot, or a tuple containing just the ``student`` names. The first is
not recommended as it is good to be conscious regarding what the context
contains. In particular, a user will have to carry the same amount of
information in their head while auditing a configuration file. The later,
because we recommend to make the context extendable without having to change
all the context validators. And by putting all student names under an
attribute, we achieve just that.

Now, to create a suite with the configuration ``config``, we do as follows:

.. code-block:: python

    suite = configsuite.ConfigSuite(
        config,
        schema,
        extract_validation_context=_extract_student_names,
    )

Context transformations
-----------------------
Context transformations allows for transforming elements based on the
values of other elements. This was implemented to support the following
scenario; you want to define variables in one part of the configuration and
then substitute values in another part based on these variables. We will now
display a simple implementation of such a system.

First, we must implement functionality for given a ``template`` and ``definitions``
to render the templates. That can be done as follows:

.. code-block:: python

    import collections
    import copy
    import jinja2

    import configsuite
    from configsuite import MetaKeys as MK
    from configsuite import types


    # To avoid collision with dict and set syntax in yaml
    _VAR_START = "<"
    _VAR_END = ">"


    def _render_variables(variables, jinja_env):
        """Repeatedly render the variables to support the scenario when one
        variable refers to another one.
        """
        variables = copy.deepcopy(variables)
        for _ in enumerate(variables):
            rendered_values = []
            for key, value in variables.items():
                try:
                    variables[key] = jinja_env.from_string(value).render(variables)
                    rendered_values.append(variables[key])
                except TypeError:
                    continue

        if any([_VAR_START in val for val in rendered_values]):
            raise ValueError("Circular dependencies")

        return variables


    def _render(template, definitions):
        """Render a template with the given definitions."""
        if definitions is None:
            definitions = {}

        variables = copy.deepcopy(definitions)
        jinja_env = jinja2.Environment(
            variable_start_string=_VAR_START, variable_end_string=_VAR_END, autoescape=True
        )

        try:
            variables = _render_variables(variables, jinja_env)
            jinja_template = jinja_env.from_string(template)
            return jinja_template.render(variables)
        except TypeError:
            return template


    @configsuite.transformation_msg("Renders Jinja template using definitions")
    def _context_render(elem, context):
        return _render(elem, definitions=context.definitions)

Second, we must implement a context extractor.

.. code-block:: python

    def extract_templating_context(configuration):
        Context = collections.namedtuple("TemplatingContext", ["definitions"])
        definitions = {key: value for (key, value) in configuration.definitions}
        return Context(definitions=definitions)

Third, we define the schema.

.. code-block:: python

    schema = {
        MK.Type: types.NamedDict,
        MK.Content: {
            "definitions": {
                MK.Type: types.Dict,
                MK.Content: {
                    MK.Key: {MK.Type: types.String},
                    MK.Value: {MK.Type: types.String},
                },
            },
            "templates": {
                MK.Type: types.List,
                MK.Content: {
                    MK.Item: {
                        MK.Type: types.String,
                        MK.ContextTransformation: _context_render,
                    }
                },
            },
        },
    }

And then, given the following yaml-configuration:

.. code-block:: yaml

    definitions:
      animal: pig
      habitants: <animal>, cow and monkey
      secret_number: 42
    templates:
      - This is a story about a <animal>.
      - It had a <color> house.
      - And the password to enter was <secret_number>.
      - If you entered the house you would meet: <habitants>.
      - The end.


we obtain the following rendered ``templates`` after feeding the ``config``,
``schema`` and the ``extract_templating_context`` through
``configsuite.ConfigSuite``.

.. code-block:: python

    >>> suite.snapshot.templates
    (
        "This is a story about a pig.",
        "It had a blue house.",
        "And the password to enter was 42.",
        "If you entered the house you would meet: pig, cow and monkey",
        "The end.",
    )

Notice that we can now merge multiple layers, with definitions in higher levels
taking precedence.

A note on contexts
~~~~~~~~~~~~~~~~~~

In these section we cover some advance topics that should be used with care.
The contexts due to the fact that parts of the configuration can no longer be
validated independently. Which implies that the user might have to make changes
far apart to keep a configuration file consistent, data that is naturally
displayed together in a UI cannot be validated without taking the rest of the
configuration into account and the difficulty of understanding your
configuration increases.

Layer transformations
---------------------
A layer transformation is applied to an element of a layer **before** the
various layers are merged. The observant reader might notice that hence the
layer transformations provide no real benefit over a standard transformation
for Basic Types. The natural application of a layer transformation is to
transform a collection such that merging can be carried out. Due to this,
*Config Suite* can give no guarantee what so ever on the content of the data
provided to a layer transformation.

A natural application of layer transformations is to support ranges where lists
of integers are expected. In particular, one would like to be able to write
``1-3, 5-7, 9`` and get ``[1, 2, 3, 5, 6, 7, 9]`` as a result. Assume one implements a
function ``_realize_list`` that takes as input a string of ranges and singletons
and returns a list as in the example above. And that one in addition decorates it with a
``transformation_msg``. Then, the following schema

.. code-block:: python

    from configsuite import MetaKeys as MK
    from configsuite import types

    {
        MK.Type: types.List,
        MK.LayerTransformation: _realize_list,
        MK.Content: {MK.Item: {MK.Type: types.Integer}},
    }

gives the specification of a list of integers for which one can instead provide
strings of ranges and singletons in some of the layers. For a full
implementation, where in addition the final list (after the layers have been
merged) is sorted and duplicates are removed we refer the reader to the `test
data <https://github.com/equinor/configsuite/blob/master/tests/data/numbers.py>`_.

Note that for the layer transformations to give the intended functionality they
are applied in a top down manner. This is another distinction from the other
transformations (including the context transformations further down) that are
all applied in a bottom up manner.
