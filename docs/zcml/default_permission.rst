.. _default_permission_directive:

``default_permission``
-------------------------------

Set the default permission to be used by all :term:`view
configuration` registrations.

This directive accepts a single attribute ,``name``, which should be
used as the default permission string.  An example of a permission
string: ``view``.  Adding a default permission makes it unnecessary to
protect each view configuration with an explicit permission, unless
your application policy requires some exception for a particular view.

If a default permission is *not* set, views represented by view
configuration registrations which do not explicitly declare a
permission will be executable by entirely anonymous users (any
authorization policy is ignored).

There can be only one default permission active at a time within an
application, thus the ``default_permission`` directive can only be
used once in any particular set of ZCML.

Attributes
~~~~~~~~~~

``name``
    Must be a string representing a :term:`permission`,
    e.g. ``view``.


Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <default_permission
    name="view"
    />

Alternatives
~~~~~~~~~~~~

Using the ``default_permission`` argument to the
:class:`pyramid.config.Configurator` constructor can be used
to achieve the same purpose.

Using the 
:meth:`pyramid.config.Configurator.set_default_permission`
method can be used to achieve the same purpose when using imperative
configuration.

See Also
~~~~~~~~

See also :ref:`setting_a_default_permission`.
