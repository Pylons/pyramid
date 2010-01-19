.. _adapter_directive:

``adapter``
-----------

Register a :term:`Zope Component Architecture` "adapter".

Attributes
~~~~~~~~~~

``factory``
  The adapter factory (often a class).

``provides``
  The :term:`interface` that an adapter instance resulting from a
  lookup will provide.

``for``
  Interfaces or classes to be adapted, separated by spaces,
  e.g. ``interfaces.IFoo interfaces.IBar``.

``name``
  The adapter name.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <adapter
     for=".foo.IFoo .bar.IBar"
     provides=".interfaces.IMyAdapter"
     factory=".adapters.MyAdapter"
     />

Alternatives
~~~~~~~~~~~~

Use the ``registerAdapter`` method of the ``registry`` attribute of a
:term:`Configurator` instance during initial application setup.

See Also
~~~~~~~~

None.

