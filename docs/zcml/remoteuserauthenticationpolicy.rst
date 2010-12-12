.. _remoteuserauthenticationpolicy_directive:

``remoteuserauthenticationpolicy``
----------------------------------

When this directive is used, authentication information is obtained
from a ``REMOTE_USER`` key in the WSGI environment, assumed to
be set by a WSGI server or an upstream middleware component.

Attributes
~~~~~~~~~~

``environ_key``
    The ``environ_key`` is the name that will be used to obtain the
    remote user value from the WSGI environment.  It defaults to
    ``REMOTE_USER``.

``callback``
    The ``callback`` is a Python dotted name to a function passed the
    string representing the remote user and the request as positional
    arguments.  The callback is expected to return None if the user
    represented by the string doesn't exist or a sequence of group
    identifiers (possibly empty) if the user does exist.  If
    ``callback`` is None, the userid will be assumed to exist with no
    groups.  It defaults to ``None``.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <remoteuserauthenticationpolicy
    environ_key="REMOTE_USER"
    callback=".somemodule.somefunc"
    />

Alternatives
~~~~~~~~~~~~

You may create an instance of the
:class:`pyramid.authentication.RemoteUserAuthenticationPolicy` and
pass it to the :class:`pyramid.config.Configurator`
constructor as the ``authentication_policy`` argument during initial
application configuration.

See Also
~~~~~~~~

See also :ref:`authentication_policies_directives_section` and
:class:`pyramid.authentication.RemoteUserAuthenticationPolicy`.
