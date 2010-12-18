.. _aclauthorizationpolicy_directive:

``aclauthorizationpolicy``
--------------------------

When this directive is used, authorization information is obtained
from :term:`ACL` objects attached to :term:`resource` objects.

Attributes
~~~~~~~~~~

None.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <aclauthorizationpolicy/>

Alternatives
~~~~~~~~~~~~

You may create an instance of the
:class:`pyramid.authorization.ACLAuthorizationPolicy` and pass it
to the :class:`pyramid.config.Configurator` constructor as
the ``authorization_policy`` argument during initial application
configuration.

See Also
~~~~~~~~

See also :ref:`authorization_policies_directives_section` and
:ref:`security_chapter`.
