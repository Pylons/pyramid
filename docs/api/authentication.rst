.. _authentication_module:

:mod:`pyramid.authentication`
--------------------------------

Helper Classes
~~~~~~~~~~~~~~

.. automodule:: pyramid.authentication

  .. autoclass:: SessionAuthenticationHelper
     :members:

  .. autoclass:: AuthTktCookieHelper
     :members:

Helper Functions
~~~~~~~~~~~~~~~~

  .. autofunction:: extract_http_basic_credentials

  .. autoclass:: HTTPBasicCredentials
     :members:

Authentication Policies
~~~~~~~~~~~~~~~~~~~~~~~

Authentication policies have been deprecated by the new security system.  See
:ref:`upgrading_auth` for more information.

  .. autoclass:: AuthTktAuthenticationPolicy
     :members:
     :inherited-members:

  .. autoclass:: RemoteUserAuthenticationPolicy
     :members:
     :inherited-members:

  .. autoclass:: SessionAuthenticationPolicy
     :members:
     :inherited-members:

  .. autoclass:: BasicAuthAuthenticationPolicy
     :members:
     :inherited-members:

  .. autoclass:: RepozeWho1AuthenticationPolicy
     :members:
     :inherited-members:
