.. _repozewho1authenticationpolicy_directive:

``repozewho1authenticationpolicy``
----------------------------------

When this directive is used, authentication information is obtained
from a ``repoze.who.identity`` key in the WSGI environment, assumed to
be set by :term:`repoze.who` middleware.

Attributes
~~~~~~~~~~

``identifier_name``
    The ``identifier_name`` controls the name used to look up the
    :term:`repoze.who` "identifier" plugin within
    ``request.environ['repoze.who.plugins']`` which is used by this
    policy to "remember" and "forget" credentials.  It defaults to
    ``auth_tkt``.

``callback``
    The ``callback`` is a Python dotted name to a function passed the
    repoze.who identity and the request as positional arguments.  The
    callback is expected to return None if the user represented by the
    identity doesn't exist or a sequence of group identifiers
    (possibly empty) if the user does exist.  If ``callback`` is None,
    the userid will be assumed to exist with no groups.  It defaults
    to ``None``.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <repozewho1authenticationpolicy
    identifier_name="auth_tkt"
    callback=".somemodule.somefunc"
    />

Alternatives
~~~~~~~~~~~~

You may create an instance of the
:class:`pyramid.authentication.RepozeWho1AuthenticationPolicy` and
pass it to the :class:`pyramid.config.Configurator`
constructor as the ``authentication_policy`` argument during initial
application configuration.

See Also
~~~~~~~~

See also :ref:`authentication_policies_directives_section` and
:class:`pyramid.authentication.RepozeWho1AuthenticationPolicy`.
