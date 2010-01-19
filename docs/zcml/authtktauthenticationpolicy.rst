.. _authtktauthenticationpolicy_directive:

``authtktauthenticationpolicy``
-------------------------------

When this directive is used, authentication information is obtained
from an :mod:`paste.auth.auth_tkt` cookie value, assumed to be set by
a custom login form.

Attributes
~~~~~~~~~~

``secret``
    The ``secret`` is a string that will be used to encrypt the data
    stored by the cookie.  It is required and has no default.

``callback``
    The ``callback`` is a Python dotted name to a function passed the
    string representing the userid stored in the cookie and the
    request as positional arguments.  The callback is expected to
    return None if the user represented by the string doesn't exist or
    a sequence of group identifiers (possibly empty) if the user does
    exist.  If ``callback`` is None, the userid will be assumed to
    exist with no groups.  It defaults to ``None``.

``cookie_name``
    The ``cookie_name`` is the name used for the cookie that contains
    the user information.  It defaults to ``repoze.bfg.auth_tkt``.

``secure``
    ``secure`` is a boolean value.  If it's set to "true", the cookie
    will only be sent back by the browser over a secure (HTTPS)
    connection.  It defaults to "false".

``include_ip``
    ``include_ip`` is a boolean value.  If it's set to true, the
    requesting IP address is made part of the authentication data in
    the cookie; if the IP encoded in the cookie differs from the IP of
    the requesting user agent, the cookie is considered invalid.  It
    defaults to "false".

``timeout``
    ``timeout`` is an integer value.  It represents the maximum age in
    seconds which the auth_tkt ticket will be considered valid.  If
    ``timeout`` is specified, and ``reissue_time`` is also specified,
    ``reissue_time`` must be a smaller value than ``timeout``.  It
    defaults to ``None``, meaning that the ticket will be considered
    valid forever.

``reissue_time``
    ``reissue_time`` is an integer value.  If ``reissue_time`` is
    specified, when we encounter a cookie that is older than the
    reissue time (in seconds), but younger that the ``timeout``, a new
    cookie will be issued.  It defaults to ``None``, meaning that
    authentication cookies are never reissued.  A value of ``0`` means
    reissue a cookie in the response to every request that requires
    authentication.

``max_age``
    ``max_age`` is the maximum age of the auth_tkt *cookie*, in
    seconds.  This differs from ``timeout`` inasmuch as ``timeout``
    represents the lifetime of the ticket contained in the cookie,
    while this value represents the lifetime of the cookie itself.
    When this value is set, the cookie's ``Max-Age`` and ``Expires``
    settings will be set, allowing the auth_tkt cookie to last between
    browser sessions.  It is typically nonsensical to set this to a
    value that is lower than ``timeout`` or ``reissue_time``, although
    it is not explicitly prevented.  It defaults to ``None``, meaning
    (on all major browser platforms) that auth_tkt cookies will last
    for the lifetime of the user's browser session.

Example
~~~~~~~

.. code-block:: xml
   :linenos:

   <authtktauthenticationpolicy
    secret="goshiamsosecret"
    callback=".somemodule.somefunc"
    cookie_name="mycookiename"
    secure="false"
    include_ip="false"
    timeout="86400"
    reissue_time="600"
    max_age="31536000"
    />

Alternatives
~~~~~~~~~~~~

You may create an instance of the
:class:`repoze.bfg.authentication.AuthTktAuthenticationPolicy` and
pass it to the :class:`repoze.bfg.configuration.Configurator`
constructor as the ``authentication_policy`` argument during initial
application configuration.

See Also
~~~~~~~~

See also :ref:`authentication_policies_directives_section` and
:class:`repoze.bfg.authentication.AuthTktAuthenticationPolicy`.
