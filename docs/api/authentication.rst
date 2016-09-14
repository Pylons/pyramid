.. _authentication_module:

:mod:`pyramid.authentication`
--------------------------------

Authentication Policies
~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: pyramid.authentication

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

Helper Classes
~~~~~~~~~~~~~~

  .. autoclass:: AuthTktCookieHelper
     :members:

  .. autoclass:: HTTPBasicCredentials
     :members:

Helper Functions
~~~~~~~~~~~~~~~~

  .. autofunction:: extract_http_basic_credentials
