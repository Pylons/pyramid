.. _utility_directive:

``utility``
-----------

Register a :term:`Zope Component Architecture` "utility".

Attributes
~~~~~~~~~~

``component``
  The utility component (cannot be specified if ``factory`` is
  specified).

``factory``
  A factory that creates a component (cannot be specified if
  ``component`` is specified).

``provides``
  The :term:`interface` that an utility instance resulting from a
  lookup will provide.

``name``
  The utility name.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <utility
     provides=".interfaces.IMyUtility"
     component=".utilities.MyUtility"
     />

Alternatives
~~~~~~~~~~~~

Use the ``registerUtility`` method of the ``registry`` attribute of a
:term:`Configurator` instance during initial application setup.

See Also
~~~~~~~~

None.
