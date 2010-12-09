.. _localenegotiator_directive:

``localenegotiator``
--------------------

Set the :term:`locale negotiator` for the current configurator to
support localization of text.

Attributes
~~~~~~~~~~

``negotiator``

  The :term:`dotted Python name` to a :term:`locale negotiator`
  implementation.  This attribute is required.  If it begins with a
  dot (``.``), the name will be considered relative to the directory
  in which the ZCML file which contains this directive lives.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <localenegotiator
     negotiator="some.package.module.my_locale_negotiator"
     />

Alternatives
~~~~~~~~~~~~

Use :meth:`pyramid.config.Configurator.set_locale_negotiator`
method instance during initial application setup.

See Also
~~~~~~~~

See also :ref:`activating_translation`.

