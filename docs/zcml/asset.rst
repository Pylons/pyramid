.. _asset_directive:

``asset``
---------

The ``asset`` directive adds an asset override for a single
static file/directory asset.

Attributes
~~~~~~~~~~

``to_override``
   A :term:`asset specification` specifying the asset to be
   overridden.

``override_with``
   A :term:`asset specification` specifying the asset which
   is used as the override.

Examples
~~~~~~~~

.. topic:: Overriding a Single Asset File

  .. code-block:: xml
     :linenos:

     <asset
       to_override="some.package:templates/mytemplate.pt"
       override_with="another.package:othertemplates/anothertemplate.pt"
     />

.. topic:: Overriding all Assets in a Package

  .. code-block:: xml
     :linenos:

     <asset
       to_override="some.package"
       override_with="another.package"
      />

.. topic:: Overriding all Assets in a Subdirectory of a Package

  .. code-block:: xml
     :linenos:

     <asset
       to_override="some.package:templates/"
       override_with="another.package:othertemplates/"
      />

Alternatives
~~~~~~~~~~~~

The :meth:`pyramid.config.Configurator.override_asset`
method can be used instead of the ``resource`` ZCML directive.

This directive can also be invoked as the ``resource`` ZCML directive for
backwards compatibility purposes.

See Also
~~~~~~~~

See also :ref:`asset_zcml_directive`.
