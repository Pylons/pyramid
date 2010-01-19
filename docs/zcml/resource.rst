.. _resource_directive:

``resource``
------------

The ``resource`` directive adds a resource override for a single
resource.

Attributes
~~~~~~~~~~

``to_override``
   A :term:`resource specification` specifying the resource to be
   overridden.

``override_with``
   A :term:`resource specification` specifying the resource which
   is used as the override.

Examples
~~~~~~~~

.. topic:: Overriding a Single Resource File

  .. code-block:: xml
     :linenos:

     <resource
       to_override="some.package:templates/mytemplate.pt"
       override_with="another.package:othertemplates/anothertemplate.pt"
     />

.. topic:: Overriding all Resources in a Package

  .. code-block:: xml
     :linenos:

     <resource
       to_override="some.package"
       override_with="another.package"
      />

.. topic:: Overriding all Resources in a Subdirectory of a Package

  .. code-block:: xml
     :linenos:

     <resource
       to_override="some.package:templates/"
       override_with="another.package:othertemplates/"
      />

Alternatives
~~~~~~~~~~~~

The :meth:`repoze.bfg.configuration.Configurator.override_resource`
method can be used instead of the ``resource`` ZCML directive.

See Also
~~~~~~~~

See also :ref:`resource_zcml_directive`.
