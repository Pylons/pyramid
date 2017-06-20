What's New in Pyramid 1.9
=========================

This article explains the new features in :app:`Pyramid` version 1.9 as compared to its predecessor, :app:`Pyramid` 1.8. It also documents backwards incompatibilities between the two versions and deprecations added to :app:`Pyramid` 1.9, as well as software dependency changes and notable documentation additions.

Major Feature Additions
-----------------------

- The file format used by all ``p*`` command line scripts such as ``pserve`` and ``pshell``, as well as the :func:`pyramid.paster.bootstrap` function is now replaceable thanks to a new dependency on `plaster <http://docs.pylonsproject.org/projects/plaster/en/latest/>`_.

  For now, Pyramid is still shipping with integrated support for the PasteDeploy INI format by depending on the `plaster_pastedeploy <https://github.com/Pylons/plaster_pastedeploy>`_ binding library. This may change in the future so it is recommended for applications to start depending on the appropriate plaster binding for their needs.

  See https://github.com/Pylons/pyramid/pull/2985

- Added an :term:`execution policy` hook to the request pipeline. An execution policy has the ability to control creation and execution of the request objects before they enter the rest of the pipeline. This means for a single request environ the policy may create more than one request object.

  The execution policy can be replaced using the new :meth:`pyramid.config.Configurator.set_execution_policy` config directive.

  The first library to use this feature is `pyramid_retry <http://docs.pylonsproject.org/projects/pyramid-retry/en/latest/>`_.

  See https://github.com/Pylons/pyramid/pull/2964

- CSRF support has been refactored out of sessions and into its own independent API in the :mod:`pyramid.csrf` module. It supports a pluggable :class:`pyramid.interfaces.ICSRFStoragePolicy` which can be used to define your own mechanism for generating and validating CSRF tokens. By default, Pyramid continues to use the :class:`pyramid.csrf.LegacySessionCSRFStoragePolicy` that uses the ``request.session.get_csrf_token`` and ``request.session.new_csrf_token`` APIs under the hood to preserve compatibility with older Pyramid applications. Two new policies are shipped as well, :class:`pyramid.csrf.SessionCSRFStoragePolicy` and :class:`pyramid.csrf.CookieCSRFStoragePolicy` which will store the CSRF tokens in the session and in a standalone cookie, respectively. The storage policy can be changed by using the new :meth:`pyramid.config.Configurator.set_csrf_storage_policy` config directive.

  CSRF tokens should be used via the new :func:`pyramid.csrf.get_csrf_token`, :func:`pyramid.csrf.new_csrf_token` and :func:`pyramid.csrf.check_csrf_token` APIs in order to continue working if the storage policy is changed. Also, the :func:`pyramid.csrf.get_csrf_token` function is now injected into templates to be used conveniently in UI code.

  See https://github.com/Pylons/pyramid/pull/2854 and https://github.com/Pylons/pyramid/pull/3019

Minor Feature Additions
-----------------------

- Support an ``open_url`` config setting in the ``pserve`` section of the config file. This url is used to open a web browser when ``pserve --browser`` is invoked. When this setting is unavailable the ``pserve`` script will attempt to guess the port the server is using from the ``server:<server_name>`` section of the config file but there is no requirement that the server is being run in this format so it may fail. See https://github.com/Pylons/pyramid/pull/2984

- The :class:`pyramid.config.Configurator` can now be used as a context manager which will automatically push/pop threadlocals (similar to :meth:`pyramid.config.Configurator.begin` and :meth:`pyramid.config.Configurator.end`). It will also automatically perform a :meth:`pyramid.config.Configurator.commit` at the end and thus it is only recommended to be used at the top-level of your app. See https://github.com/Pylons/pyramid/pull/2874

- The threadlocals are now available inside any function invoked via :meth:`pyramid.config.Configurator.include`. This means the only config-time code that cannot rely on threadlocals is code executed from non-actions inside the main. This can be alleviated by invoking :meth:`pyramid.config.Configurator.begin` and :meth:`pyramid.config.Configurator.end` appropriately or using the new context manager feature of the configurator. See https://github.com/Pylons/pyramid/pull/2989

- The threadlocals are now available inside exception views invoked via :meth:`pyramid.request.Request.invoke_exception_view` even when the ``request`` argument is overridden. See https://github.com/Pylons/pyramid/pull/3060

- When unsupported predicates are supplied to :meth:`pyramid.config.Configurator.add_view`, :meth:`pyramid.config.Configurator.add_route` and :meth:`pyramid.config.Configurator.add_subscriber` a much more helpful error message is output with a guess as to which predicate was intended. See https://github.com/Pylons/pyramid/pull/3054

- Normalize the permission results to a proper class hierarchy. :class:`pyramid.security.ACLAllowed` is now a subclass of :class:`pyramid.security.Allowed` and :class:`pyramid.security.ACLDenied` is now a subclass of :class:`pyramid.security.Denied`. See https://github.com/Pylons/pyramid/pull/3084

- Add a ``quote_via`` argument to :func:`pyramid.encode.urlencode` to follow the stdlib's version and enable custom quoting functions. See https://github.com/Pylons/pyramid/pull/3088

- Support `_query=None` and `_anchor=None` in :meth:`pyramid.request.Request.route_url` as well as ``query=None`` and ``anchor=None`` in :meth:`pyramid.request.Request.resource_url`. Previously this would cause an `?` and a `#`, respectively, in the url with nothing after it. Now the unnecessary parts are dropped from the generated URL. See https://github.com/Pylons/pyramid/pull/3034

Deprecations
------------

- Pyramid currently depends on ``plaster_pastedeploy`` to simplify the transition to ``plaster`` by maintaining integrated support for INI files. This dependency on ``plaster_pastedeploy`` should be considered subject to Pyramid's deprecation policy and may be removed in the future. Applications should depend on the appropriate plaster binding to satisfy their needs.

- Retrieving CSRF token from the session has been deprecated in favor of equivalent methods in the :mod:`pyramid.csrf` module. The CSRF methods (``ISession.get_csrf_token`` and ``ISession.new_csrf_token``) are no longer required on the :class:`pyramid.interfaces.ISession` interface except when using the default :class:`pyramid.csrf.LegacySessionCSRFStoragePolicy`.

  Also, ``pyramid.session.check_csrf_token`` is now located at :func:`pyramid.csrf.check_csrf_token`.

  See https://github.com/Pylons/pyramid/pull/2854 and https://github.com/Pylons/pyramid/pull/3019

Backward Incompatibilities
--------------------------

- ``request.exception`` and ``request.exc_info`` will only be set if the response was generated by the EXCVIEW tween. This is to avoid any confusion where a response was generated elsewhere in the pipeline and not in direct relation to the original exception. If anyone upstream wants to catch and render responses for exceptions they should set ``request.exception`` and ``request.exc_info`` themselves to indicate the exception that was squashed when generating the response.

  Similar behavior occurs with :meth:`pyramid.request.Request.invoke_exception_view` in which the exception properties are set to reflect the exception if a response is successfully generated by the method.

  This is a very minor incompatibility. Most tweens right now would give priority to the raised exception and ignore ``request.exception``. This change just improves and clarifies that bookkeeping by trying to be more clear about the relationship between the response and its squashed exception. See https://github.com/Pylons/pyramid/pull/3029 and https://github.com/Pylons/pyramid/pull/3031

Documentation Enhancements
--------------------------

- Added the :term:`execution policy` to the routing diagram in :ref:`router_chapter`. See https://github.com/Pylons/pyramid/pull/2993
