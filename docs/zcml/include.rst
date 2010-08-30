.. _include_directive:

``include``
-----------

The ``include`` directive includes configuration from an external ZCML
file.  Use of the ``include`` tag allows a user to split configuration
across multiple ZCML files, and allows package distributors to provide
default ZCML configuration for specific purposes which can be
included by the integrator of the package as necessary.

Attributes
~~~~~~~~~~

``package``
   A :term:`dotted Python name` which references a Python :term:`package`.

``file``
   An absolute or relative filename which references a ZCML file.

The ``package`` and ``file`` attributes can be used together or
separately as necessary.

Examples
~~~~~~~~

.. topic:: Loading the File Named ``configure.zcml`` from a Package Implicitly

   .. code-block:: xml
      :linenos:

      <include package="some.package" />

.. topic:: Loading the File Named ``other.zcml`` From the Current Package

   .. code-block:: xml
      :linenos:

      <include file="other.zcml" />

.. topic:: Loading a File From a Subdirectory of the Current Package

   .. code-block:: xml
      :linenos:

      <include file="subdir/other.zcml" />

.. topic:: Loading the File Named ``/absolute/path/other.zcml``

   .. code-block:: xml
      :linenos:

      <include file="/absolute/path/other.zcml" />

.. topic:: Loading the File Named ``other.zcml`` From a Package Explicitly

   .. code-block:: xml
      :linenos:

      <include package="some.package" file="other.zcml" />

Alternatives
~~~~~~~~~~~~

None.

See Also
~~~~~~~~

See also :ref:`helloworld_declarative`.

