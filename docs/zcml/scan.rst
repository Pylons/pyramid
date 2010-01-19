.. _scan_directive:

``scan``
--------

To make use of :term:`configuration decoration` decorators, you must
perform a :term:`scan`.  A scan finds these decorators in code.  The
``scan`` ZCML directive tells :mod:`repoze.bfg` to begin such a scan.

Attributes
~~~~~~~~~~

``package``
    The package to scan or the single dot (``.``), meaning the
    "current" package (the package in which the ZCML file lives).

Example
~~~~~~~

.. code-block:: xml
   :linenos:
    
   <scan package="."/>

Alternatives
~~~~~~~~~~~~

The :meth:`repoze.bfg.configuration.Configurator.scan` method performs
the same job as the ``scan`` ZCML directive.

See Also
~~~~~~~~

See also :ref:`mapping_views_using_a_decorator_section`.
