Deprecated behaviour
====================

Specifying AllowNone and Default
--------------------------------

In *Config Suite* 0.6 the schema keywords `AllowNone` and `Default` was
introduced. `AllowNone` is used to indicate whether a basic element can take
the value `None` and is defaulted to `False`. And `Default` can be used to
provide default values for elements and it defaults to `None`. It should be
noted that there is a strong correlation between `Default`, `AllowNone` and
`Required`. In particular, the later can be deduced from the first two. In
short, if an element is required it should neither allow `None` values nor have
a default. Because if so, it would not be required.

Here is a complete table of valid combinations of the three options:

.. csv-table:: Valid combinations
   :header: "AllowNone", "Default", "Required"
   :widths: 20, 20, 20

   "True", "True", "False"
   "True", "False", "False"
   "False", "True", "False"
   "False", "False", "True"

Required is deprecated
----------------------
In the transition to *Config Suite* 0.6 specifying elements in the schema as
`Required` is deprecated. In particular, it is superseded as described above by
specifying `AllowNone` and `Default`. The plan is that 0.6 will still
function with `Required` in the schemas to ease the process of introducing
`AllowNone` and `Default`. However, upon initialization `ConfigSuite` now
accepts an optional, boolean argument named `deduce_required`. If
`deduce_required` is set to `False` (which is the default value) a deprecation
warning will be raised. After the transition to using `AllowNone` and `Default`
has been made (which the reader is heavily encouraged to finish before
considering the deprecation of `Required`) the consumer is expected to toggle
`deduce_required` to  `True`. At this point a new deprecation warning will be
raised upon creation of a `ConfigSuite` instance if the schema contains a
`Required` specification. However, they are now all safe to remove and you are
indeed encouraged to do so.

Then in the 0.7 release `deduce_required` will default to `None`. If `True`
is passed instead we will raise a deprecation warning and for any other value
we will raise an exception. The idea is that in 0.7 you can safely stop
setting `deduce_required` and then be ready for 0.8, where `deduce_required`
will not be recognized as an optional argument anymore.
