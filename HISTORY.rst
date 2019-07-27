1.10 (2018-10-31)
=================

- No major changes from 1.10b1.

1.10b1 (2018-10-28)
===================

Bug Fixes
---------

- Fix the ``pyramid.testing.DummyRequest`` to support the new
  ``request.accept`` API so that ``acceptable_offers`` is available even
  when code sets the value to a string.
  See https://github.com/Pylons/pyramid/pull/3396

- Fix deprecated escape sequences in preparation for Python 3.8.
  See https://github.com/Pylons/pyramid/pull/3400

1.10a1 (2018-10-15)
===================

Features
--------

- Add a ``_depth`` and ``_category`` arguments to all of the venusian
  decorators. The ``_category`` argument can be used to affect which actions
  are registered when performing a ``config.scan(..., category=...)`` with a
  specific category. The ``_depth`` argument should be used when wrapping
  the decorator in your own. This change affects ``pyramid.view.view_config``,
  ``pyramid.view.exception_view_config``,
  ``pyramid.view.forbidden_view_config``, ``pyramid.view.notfound_view_config``,
  ``pyramid.events.subscriber`` and ``pyramid.response.response_adapter``
  decorators. See https://github.com/Pylons/pyramid/pull/3105 and
  https://github.com/Pylons/pyramid/pull/3122

- Fix the ``pyramid.request.Request`` class name after using
  ``set_property`` or ``config.add_request_method`` such that the
  ``str(request.__class__)`` would appear as ``pyramid.request.Request``
  instead of ``pyramid.util.Request``.
  See https://github.com/Pylons/pyramid/pull/3129

- In ``cherrypy_server_runner``, prefer imports from the ``cheroot`` package
  over the legacy imports from `cherrypy.wsgiserver`.
  See https://github.com/Pylons/pyramid/pull/3235

- Add a context manager ``route_prefix_context`` to the
  ``pyramid.config.Configurator`` to allow for convenient setting of the
  route_prefix for ``include`` and ``add_route`` calls inside the context.
  See https://github.com/Pylons/pyramid/pull/3279

- Modify the builtin session implementations to support ``SameSite`` options
  on cookies and set the default to ``'Lax'``. This affects
  ``pyramid.session.BaseCookieSessionFactory``,
  ``pyramid.session.SignedCookieSessionFactory``, and
  ``pyramid.session.UnencryptedCookieSessionFactoryConfig``.
  See https://github.com/Pylons/pyramid/pull/3300

- Modify ``pyramid.authentication.AuthTktAuthenticationPolicy`` and
  ``pyramid.csrf.CookieCSRFStoragePolicy`` to support the ``SameSite`` option
  on cookies and set the default to ``'Lax'``.
  See https://github.com/Pylons/pyramid/pull/3319

- Added new ``pyramid.httpexceptions.HTTPPermanentRedirect``
  exception/response object for a HTTP 308 redirect.
  See https://github.com/Pylons/pyramid/pull/3302

- Within ``pshell``, allow the user-defined ``setup`` function to be a
  generator, in which case it may wrap the command's lifecycle.
  See https://github.com/Pylons/pyramid/pull/3318

- Within ``pshell``, variables defined by the ``[pshell]`` settings are
  available within the user-defined ``setup`` function.
  See https://github.com/Pylons/pyramid/pull/3318

- Add support for Python 3.7. Add testing on Python 3.8 with allowed failures.
  See https://github.com/Pylons/pyramid/pull/3333

- Added the ``pyramid.config.Configurator.add_accept_view_order`` directive,
  allowing users to specify media type preferences in ambiguous situations
  such as when several views match. A default ordering is defined for media
  types that prefers human-readable html/text responses over JSON.
  See https://github.com/Pylons/pyramid/pull/3326

- Support a list of media types in the ``accept`` predicate used in
  ``pyramid.config.Configurator.add_route``.
  See https://github.com/Pylons/pyramid/pull/3326

- Added ``pyramid.session.JSONSerializer``. See "Upcoming Changes to ISession
  in Pyramid 2.0" in the "Sessions" chapter of the documentation for more
  information about this feature.
  See https://github.com/Pylons/pyramid/pull/3353

- Add a ``registry`` argument to ``pyramid.renderers.get_renderer``
  to allow users to avoid threadlocals during renderer lookup.
  See https://github.com/Pylons/pyramid/pull/3358

- Pyramid's test suite is no longer distributed with the universal wheel.
  See https://github.com/Pylons/pyramid/pull/3387

- All Python code is now formatted automatically using ``black``.
  See https://github.com/Pylons/pyramid/pull/3388

Bug Fixes
---------

- Set appropriate ``code`` and ``title`` attributes on the ``HTTPClientError``
  and ``HTTPServerError`` exception classes. This prevents inadvertently
  returning a 520 error code.
  See https://github.com/Pylons/pyramid/pull/3280

- Replace ``webob.acceptparse.MIMEAccept`` from WebOb with
  ``webob.acceptparse.create_accept_header`` in the HTTP exception handling
  code. The old ``MIMEAccept`` has been deprecated. The new methods follow the
  RFC's more closely. See https://github.com/Pylons/pyramid/pull/3251

- Catch extra errors like ``AttributeError`` when unpickling "trusted"
  session cookies with bad pickle data in them. This would occur when sharing
  a secret between projects that shouldn't actually share session cookies,
  like when reusing secrets between projects in development.
  See https://github.com/Pylons/pyramid/pull/3325

Deprecations
------------

- The ``pyramid.interfaces.ISession`` interface will move to require
  JSON-serializable objects in Pyramid 2.0. See
  "Upcoming Changes to ISession in Pyramid 2.0" in the "Sessions" chapter
  of the documentation for more information about this change.
  See https://github.com/Pylons/pyramid/pull/3353

- The ``pyramid.session.signed_serialize`` and
  ``pyramid.session.signed_deserialize`` functions will be removed in Pyramid
  2.0, along with the removal of
  ``pyramid.session.UnencryptedCookieSessionFactoryConfig`` which was
  deprecated in Pyramid 1.5. Please switch to using the
  ``SignedCookieSessionFactory``, copying the code, or another session
  implementation if you're still using these features.
  See https://github.com/Pylons/pyramid/pull/3353

- Media ranges are deprecated in the ``accept`` argument of
  ``pyramid.config.Configurator.add_route``. Use a list of explicit
  media types to ``add_route`` to support multiple types.

- Media ranges are deprecated in the ``accept`` argument of
  ``pyramid.config.Configurator.add_view``.  There is no replacement for
  ranges to ``add_view``, but after much discussion the workflow is
  fundamentally ambiguous in the face of various client-supplied values for
  the ``Accept`` header.
  See https://github.com/Pylons/pyramid/pull/3326

Backward Incompatibilities
--------------------------

- On Python 3.4+ the ``repoze.lru`` dependency is dropped. If you were using
  this package directly in your apps you should make sure that you are
  depending on it directly within your project.
  See https://github.com/Pylons/pyramid/pull/3140

- Remove the ``permission`` argument from
  ``pyramid.config.Configurator.add_route``. This was an argument left over
  from a feature removed in Pyramid 1.5 and has had no effect since then.
  See https://github.com/Pylons/pyramid/pull/3299

- Modify the builtin session implementations to set ``SameSite='Lax'`` on
  cookies. This affects ``pyramid.session.BaseCookieSessionFactory``,
  ``pyramid.session.SignedCookieSessionFactory``, and
  ``pyramid.session.UnencryptedCookieSessionFactoryConfig``.
  See https://github.com/Pylons/pyramid/pull/3300

- Variables defined in the ``[pshell]`` section of the settings will no
  longer override those set by the ``setup`` function.
  See https://github.com/Pylons/pyramid/pull/3318

- ``pyramid.config.Configurator.add_notfound_view`` uses default redirect
  class exception ``pyramid.httpexceptions.HTTPTemporaryRedirect`` instead
  of previous ``pyramid.httpexceptions.HTTPFound``.
  See https://github.com/Pylons/pyramid/pull/3328

- Removed ``pyramid.config.Configurator.set_request_property`` which had been
  deprecated since Pyramid 1.5. Instead use
  ``pyramid.config.Configurator.add_request_method`` with ``reify=True`` or
  ``property=True``.
  See https://github.com/Pylons/pyramid/pull/3368

- Removed the ``principal`` keyword argument from
  ``pyramid.security.remember`` which had been deprecated since Pyramid 1.6
  and replaced by the ``userid`` argument.
  See https://github.com/Pylons/pyramid/pull/3369

- Removed the ``pyramid.tests`` subpackage that used to contain the Pyramid
  test suite. These changes also changed the format of the repository to move
  the code into a ``src`` folder.
  See https://github.com/Pylons/pyramid/pull/3387

Documentation Changes
---------------------

- Ad support for Read The Docs Ethical Ads.
  See https://github.com/Pylons/pyramid/pull/3360 and
  https://docs.readthedocs.io/en/latest/advertising/ethical-advertising.html

- Add support for alembic to the pyramid-cookiecutter-alchemy cookiecutter
  and update the wiki2 tutorial to explain how it works.
  See https://github.com/Pylons/pyramid/pull/3307 and
  https://github.com/Pylons/pyramid-cookiecutter-alchemy/pull/7

- Bump Sphinx to >= 1.7.4 in setup.py to support ``emphasize-lines`` in PDFs
  and to pave the way for xelatex support.  See
  https://github.com/Pylons/pyramid/pull/3271,
  https://github.com/Pylons/pyramid/issues/667, and
  https://github.com/Pylons/pyramid/issues/2572

- Added extra tests to the quick tutorial.
  See https://github.com/Pylons/pyramid/pull/3375

1.9 (2017-06-26)
================

- No major changes from 1.9b1.

- Updated documentation links for ``docs.pylonsproject.org`` to use HTTPS.

1.9b1 (2017-06-19)
==================

- Add an informative error message when unknown predicates are supplied. The
  new message suggests alternatives based on the list of known predicates.
  See https://github.com/Pylons/pyramid/pull/3054

- Added integrity attributes for JavaScripts in cookiecutters, scaffolds, and
  resulting source files in tutorials.
  See https://github.com/Pylons/pyramid/issues/2548

- Update RELEASING.txt for updating cookiecutters. Change cookiecutter URLs to
  use shortcut.
  See https://github.com/Pylons/pyramid/issues/3042

- Ensure the correct threadlocals are pushed during view execution when
  invoked from ``request.invoke_exception_view``.
  See https://github.com/Pylons/pyramid/pull/3060

- Fix a bug in which ``pyramid.security.ALL_PERMISSIONS`` failed to return
  a valid iterator in its ``__iter__`` implementation.
  See https://github.com/Pylons/pyramid/pull/3074

- Normalize the permission results to a proper class hierarchy.
  ``pyramid.security.ACLAllowed`` is now a subclass of
  ``pyramid.security.Allowed`` and ``pyramid.security.ACLDenied`` is now a
  subclass of ``pyramid.security.Denied``.
  See https://github.com/Pylons/pyramid/pull/3084

- Add a ``quote_via`` argument to ``pyramid.encode.urlencode`` to follow
  the stdlib's version and enable custom quoting functions.
  See https://github.com/Pylons/pyramid/pull/3088

- Support `_query=None` and `_anchor=None` in ``request.route_url`` as well
  as ``query=None`` and ``anchor=None`` in ``request.resource_url``.
  Previously this would cause an `?` and a `#`, respectively, in the url
  with nothing after it. Now the unnecessary parts are dropped from the
  generated URL. See https://github.com/Pylons/pyramid/pull/3034

- Revamp the ``IRouter`` API used by ``IExecutionPolicy`` to force
  pushing/popping the request threadlocals. The
  ``IRouter.make_request(environ)`` API has been replaced by
  ``IRouter.request_context(environ)`` which should be used as a context
  manager. See https://github.com/Pylons/pyramid/pull/3086

1.9a2 (2017-05-09)
==================

Backward Incompatibilities
--------------------------

- ``request.exception`` and ``request.exc_info`` will only be set if the
  response was generated by the EXCVIEW tween. This is to avoid any confusion
  where a response was generated elsewhere in the pipeline and not in
  direct relation to the original exception. If anyone upstream wants to
  catch and render responses for exceptions they should set
  ``request.exception`` and ``request.exc_info`` themselves to indicate
  the exception that was squashed when generating the response.

  Similar behavior occurs with ``request.invoke_exception_view`` in which
  the exception properties are set to reflect the exception if a response
  is successfully generated by the method.

  This is a very minor incompatibility. Most tweens right now would give
  priority to the raised exception and ignore ``request.exception``. This
  change just improves and clarifies that bookkeeping by trying to be
  more clear about the relationship between the response and its squashed
  exception. See https://github.com/Pylons/pyramid/pull/3029 and
  https://github.com/Pylons/pyramid/pull/3031

1.9a1 (2017-05-01)
==================

Major Features
--------------

- The file format used by all ``p*`` command line scripts such as ``pserve``
  and ``pshell``, as well as the ``pyramid.paster.bootstrap`` function
  is now replaceable thanks to a new dependency on
  `plaster <https://docs.pylonsproject.org/projects/plaster/en/latest/>`_.

  For now, Pyramid is still shipping with integrated support for the
  PasteDeploy INI format by depending on the
  `plaster_pastedeploy <https://github.com/Pylons/plaster_pastedeploy>`_
  binding library. This may change in the future.

  See https://github.com/Pylons/pyramid/pull/2985

- Added an execution policy hook to the request pipeline. An execution
  policy has the ability to control creation and execution of the request
  objects before they enter the rest of the pipeline. This means for a single
  request environ the policy may create more than one request object.

  The first library to use this feature is
  `pyramid_retry
  <https://docs.pylonsproject.org/projects/pyramid-retry/en/latest/>`_.

  See https://github.com/Pylons/pyramid/pull/2964

- CSRF support has been refactored out of sessions and into its own
  independent API in the ``pyramid.csrf`` module. It supports a pluggable
  ``pyramid.interfaces.ICSRFStoragePolicy`` which can be used to define your
  own mechanism for generating and validating CSRF tokens. By default,
  Pyramid continues to use the ``pyramid.csrf.LegacySessionCSRFStoragePolicy``
  that uses the ``request.session.get_csrf_token`` and
  ``request.session.new_csrf_token`` APIs under the hood to preserve
  compatibility. Two new policies are shipped as well,
  ``pyramid.csrf.SessionCSRFStoragePolicy`` and
  ``pyramid.csrf.CookieCSRFStoragePolicy`` which will store the CSRF tokens
  in the session and in a standalone cookie, respectively. The storage policy
  can be changed by using the new
  ``pyramid.config.Configurator.set_csrf_storage_policy`` config directive.

  CSRF tokens should be used via the new ``pyramid.csrf.get_csrf_token``,
  ``pyramid.csrf.new_csrf_token`` and ``pyramid.csrf.check_csrf_token`` APIs
  in order to continue working if the storage policy is changed. Also, the
  ``pyramid.csrf.get_csrf_token`` function is injected into templates to be
  used conveniently in UI code.

  See https://github.com/Pylons/pyramid/pull/2854 and
  https://github.com/Pylons/pyramid/pull/3019

Minor Features
--------------

- Support an ``open_url`` config setting in the ``pserve`` section of the
  config file. This url is used to open a web browser when ``pserve --browser``
  is invoked. When this setting is unavailable the ``pserve`` script will
  attempt to guess the port the server is using from the
  ``server:<server_name>`` section of the config file but there is no
  requirement that the server is being run in this format so it may fail.
  See https://github.com/Pylons/pyramid/pull/2984

- The ``pyramid.config.Configurator`` can now be used as a context manager
  which will automatically push/pop threadlocals (similar to
  ``config.begin()`` and ``config.end()``). It will also automatically perform
  a ``config.commit()`` and thus it is only recommended to be used at the
  top-level of your app. See https://github.com/Pylons/pyramid/pull/2874

- The threadlocals are now available inside any function invoked via
  ``config.include``. This means the only config-time code that cannot rely
  on threadlocals is code executed from non-actions inside the main. This
  can be alleviated by invoking ``config.begin()`` and ``config.end()``
  appropriately or using the new context manager feature of the configurator.
  See https://github.com/Pylons/pyramid/pull/2989

Bug Fixes
---------

- HTTPException's accepts a detail kwarg that may be used to pass additional
  details to the exception. You may now pass objects so long as they have a
  valid __str__ method. See https://github.com/Pylons/pyramid/pull/2951

- Fix a reference cycle causing memory leaks in which the registry
  would keep a ``Configurator`` instance alive even after the configurator
  was discarded. Another fix was also added for the ``global_registries``
  object in which the registry was stored in a closure preventing it from
  being deallocated. See https://github.com/Pylons/pyramid/pull/2967

- Fix a bug directly invoking ``pyramid.scripts.pserve.main`` with the
  ``--reload`` option in which ``sys.argv`` is always used in the subprocess
  instead of the supplied ``argv``.
  See https://github.com/Pylons/pyramid/pull/2962

Deprecations
------------

- Pyramid currently depends on ``plaster_pastedeploy`` to simplify the
  transition to ``plaster`` by maintaining integrated support for INI files.
  This dependency on ``plaster_pastedeploy`` should be considered subject to
  Pyramid's deprecation policy and may be removed in the future.
  Applications should depend on the appropriate plaster binding to satisfy
  their needs.

- Retrieving CSRF token from the session has been deprecated in favor of
  equivalent methods in the ``pyramid.csrf`` module. The CSRF methods
  (``ISession.get_csrf_token`` and ``ISession.new_csrf_token``) are no longer
  required on the ``ISession`` interface except when using the default
  ``pyramid.csrf.LegacySessionCSRFStoragePolicy``.

  Also, ``pyramid.session.check_csrf_token`` is now located at
  ``pyramid.csrf.check_csrf_token``.

  See https://github.com/Pylons/pyramid/pull/2854 and
  https://github.com/Pylons/pyramid/pull/3019

Documentation Changes
---------------------

- Added the execution policy to the routing diagram in the Request Processing
  chapter. See https://github.com/Pylons/pyramid/pull/2993

1.8 (2017-01-21)
================

- No major changes from 1.8b1.

1.8b1 (2017-01-17)
==================

Features
--------

- Added an ``override`` option to ``config.add_translation_dirs`` to allow
  later calls to place translation directories at a higher priority than
  earlier calls. See https://github.com/Pylons/pyramid/pull/2902

Documentation Changes
---------------------

- Improve registry documentation to discuss uses as a component registry
  and as a dictionary. See https://github.com/Pylons/pyramid/pull/2893

- Quick Tour, Quick Tutorial, and most other remaining documentation updated to
  use cookiecutters instead of pcreate and scaffolds.
  See https://github.com/Pylons/pyramid/pull/2888 and
  https://github.com/Pylons/pyramid/pull/2889

- Fix unittests in wiki2 to work without different dependencies between
  py2 and py3. See https://github.com/Pylons/pyramid/pull/2899

- Update Windows documentation to track newer Python 3 improvements to the
  installer. See https://github.com/Pylons/pyramid/pull/2900

- Updated the ``mod_wsgi`` tutorial to use cookiecutters and Apache 2.4+.
  See https://github.com/Pylons/pyramid/pull/2901

1.8a1 (2016-12-25)
==================

Backward Incompatibilities
--------------------------

- Support for the ``IContextURL`` interface that was deprecated in Pyramid 1.3
  has been removed.  See https://github.com/Pylons/pyramid/pull/2822

- Following the Pyramid deprecation period (1.6 -> 1.8),
  daemon support for pserve has been removed. This includes removing the
  daemon commands (start, stop, restart, status) as well as the following
  arguments: ``--daemon``, ``--pid-file``, ``--log-file``,
  ``--monitor-restart``, ``--status``, ``--user``, ``--group``,
  ``--stop-daemon``

  To run your server as a daemon you should use a process manager instead of
  pserve.

  See https://github.com/Pylons/pyramid/pull/2615

- ``pcreate`` is now interactive by default. You will be prompted if a file
  already exists with different content. Previously if there were similar
  files it would silently skip them unless you specified ``--interactive``
  or ``--overwrite``.
  See https://github.com/Pylons/pyramid/pull/2775

- Removed undocumented argument ``cachebust_match`` from
  ``pyramid.static.static_view``. This argument was shipped accidentally
  in Pyramid 1.6. See https://github.com/Pylons/pyramid/pull/2681

- Change static view to avoid setting the ``Content-Encoding`` response header
  to an encoding guessed using Python's ``mimetypes`` module. This was causing
  clients to decode the content of gzipped files when downloading them. The
  client would end up with a ``foo.txt.gz`` file on disk that was already
  decoded, thus should really be ``foo.txt``. Also, the ``Content-Encoding``
  should only have been used if the client itself broadcast support for the
  encoding via ``Accept-Encoding`` request headers.
  See https://github.com/Pylons/pyramid/pull/2810

- Settings are no longer accessible as attributes on the settings object
  (e.g. ``request.registry.settings.foo``). This was deprecated in Pyramid 1.2.
  See https://github.com/Pylons/pyramid/pull/2823

Features
--------

- Python 3.6 compatibility.
  https://github.com/Pylons/pyramid/issues/2835

- ``pcreate`` learned about ``--package-name`` to allow you to create a new
  project in an existing folder with a different package name than the project
  name. See https://github.com/Pylons/pyramid/pull/2783

- The ``_get_credentials`` private method of ``BasicAuthAuthenticationPolicy``
  has been extracted into standalone function ``extract_http_basic_credentials``
  in ``pyramid.authentication`` module, this function extracts HTTP Basic
  credentials from a ``request`` object, and returns them as a named tuple.
  See https://github.com/Pylons/pyramid/pull/2662

- Pyramid 1.4 silently dropped a feature of the configurator that has been
  restored. It's again possible for action discriminators to conflict across
  different action orders.
  See https://github.com/Pylons/pyramid/pull/2757

- ``pyramid.paster.bootstrap`` and its sibling ``pyramid.scripting.prepare``
  can now be used as context managers to automatically invoke the ``closer``
  and pop threadlocals off of the stack to prevent memory leaks.
  See https://github.com/Pylons/pyramid/pull/2760

- Added ``pyramid.config.Configurator.add_exception_view`` and the
  ``pyramid.view.exception_view_config`` decorator. It is now possible using
  these methods or via the new ``exception_only=True`` option to ``add_view``
  to add a view which will only be matched when handling an exception.
  Previously any exception views were also registered for a traversal
  context that inherited from the exception class which prevented any
  exception-only optimizations.
  See https://github.com/Pylons/pyramid/pull/2660

- Added the ``exception_only`` boolean to
  ``pyramid.interfaces.IViewDeriverInfo`` which can be used by view derivers
  to determine if they are wrapping a view which only handles exceptions.
  This means that it is no longer necessary to perform request-time checks
  for ``request.exception`` to determine if the view is handling an exception
  - the pipeline can be optimized at config-time.
  See https://github.com/Pylons/pyramid/pull/2660

- ``pserve`` should now work with ``gevent`` and other workers that need
  to monkeypatch the process, assuming the server and / or the app do so
  as soon as possible before importing the rest of pyramid.
  See https://github.com/Pylons/pyramid/pull/2797

- Pyramid no longer copies the settings object passed to the
  ``pyramid.config.Configurator(settings=)``. The original ``dict`` is kept.
  See https://github.com/Pylons/pyramid/pull/2823

- The csrf trusted origins setting may now be a whitespace-separated list of
  domains. Previously only a python list was allowed. Also, it can now be set
  using the ``PYRAMID_CSRF_TRUSTED_ORIGINS`` environment variable similar to
  other settings. See https://github.com/Pylons/pyramid/pull/2823

- ``pserve --reload`` now uses the
  `hupper <http://docs.pylonsproject.org/projects/hupper/en/latest/>`
  library to monitor file changes. This comes with many improvements:

  - If the `watchdog <http://pythonhosted.org/watchdog/>`_ package is
    installed then monitoring will be done using inotify instead of
    cpu and disk-intensive polling.

  - The monitor is now a separate process that will not crash and starts up
    before any of your code.

  - The monitor will not restart the process after a crash until a file is
    saved.

  - The monitor works on windows.

  - You can now trigger a reload manually from a pyramid view or any other
    code via ``hupper.get_reloader().trigger_reload()``. Kind of neat.

  - You can trigger a reload by issuing a ``SIGHUP`` to the monitor process.

  See https://github.com/Pylons/pyramid/pull/2805

- A new ``[pserve]`` section is supported in your config files with a
  ``watch_files`` key that can configure ``pserve --reload`` to monitor custom
  file paths. See https://github.com/Pylons/pyramid/pull/2827

- Allow streaming responses to be made from subclasses of
  ``pyramid.httpexceptions.HTTPException``. Previously the response would
  be unrolled while testing for a body, making it impossible to stream
  a response.
  See https://github.com/Pylons/pyramid/pull/2863

- Update starter, alchemy and zodb scaffolds to support IPv6 by using the
  new ``listen`` directives in waitress.
  See https://github.com/Pylons/pyramid/pull/2853

- All p* scripts now use argparse instead of optparse. This improves their
  ``--help`` output as well as enabling nicer documentation of their options.
  See https://github.com/Pylons/pyramid/pull/2864

- Any deferred configuration action registered via ``config.action`` may now
  depend on threadlocal state, such as asset overrides, being active when
  the action is executed.
  See https://github.com/Pylons/pyramid/pull/2873

- Asset specifications for directories passed to
  ``config.add_translation_dirs`` now support overriding the entire asset
  specification, including the folder name. Previously only the package name
  was supported and the folder would always need to have the same name.
  See https://github.com/Pylons/pyramid/pull/2873

- ``config.begin()`` will propagate the current threadlocal request through
  as long as the registry is the same. For example:

  .. code-block:: python

     request = Request.blank(...)
     config.begin(request)  # pushes a request
     config.begin()         # propagates the previous request through unchanged
     assert get_current_request() is request

  See https://github.com/Pylons/pyramid/pull/2873

- Added a new ``callback`` option to ``config.set_default_csrf_options`` which
  can be used to determine per-request whether CSRF checking should be enabled
  to allow for a mix authentication methods. Only cookie-based methods
  generally require CSRF checking.
  See https://github.com/Pylons/pyramid/pull/2778

Bug Fixes
---------

- Fixed bug in ``proutes`` such that it now shows the correct view when a
  class and ``attr`` is involved.
  See: https://github.com/Pylons/pyramid/pull/2687

- Fix a ``FutureWarning`` in Python 3.5 when using ``re.split`` on the
  ``format`` setting to the ``proutes`` script.
  See https://github.com/Pylons/pyramid/pull/2714

- Fix a ``RuntimeWarning`` emitted by WebOb when using arbitrary objects
  as the ``userid`` in the ``AuthTktAuthenticationPolicy``. This is now caught
  by the policy and the object is serialized as a base64 string to avoid
  the cryptic warning. Since the userid will be read back as a string on
  subsequent requests a more useful warning is emitted encouraging you to
  use a primitive type instead.
  See https://github.com/Pylons/pyramid/pull/2715

- Pyramid 1.6 introduced the ability for an action to invoke another action.
  There was a bug in the way that ``config.add_view`` would interact with
  custom view derivers introduced in Pyramid 1.7 because the view's
  discriminator cannot be computed until view derivers and view predicates
  have been created in earlier orders. Invoking an action from another action
  would trigger an unrolling of the pipeline and would compute discriminators
  before they were ready. The new behavior respects the ``order`` of the action
  and ensures the discriminators are not computed until dependent actions
  from previous orders have executed.
  See https://github.com/Pylons/pyramid/pull/2757

- Fix bug in i18n where the default domain would always use the Germanic plural
  style, even if a different plural function is defined in the relevant
  messages file. See https://github.com/Pylons/pyramid/pull/2859

- The ``config.override_asset`` method now occurs during
  ``pyramid.config.PHASE1_CONFIG`` such that it is ordered to execute before
  any calls to ``config.add_translation_dirs``.
  See https://github.com/Pylons/pyramid/pull/2873

Deprecations
------------

- The ``pcreate`` script and related scaffolds have been deprecated in favor
  of the popular
  `cookiecutter <https://cookiecutter.readthedocs.io/en/latest/>`_ project.

  All of Pyramid's official scaffolds as well as the tutorials have been
  ported to cookiecutters:

  - `pyramid-cookiecutter-starter
    <https://github.com/Pylons/pyramid-cookiecutter-starter>`_

  - `pyramid-cookiecutter-alchemy
    <https://github.com/Pylons/pyramid-cookiecutter-alchemy>`_

  - `pyramid-cookiecutter-zodb
    <https://github.com/Pylons/pyramid-cookiecutter-zodb>`_

  See https://github.com/Pylons/pyramid/pull/2780

Documentation Changes
---------------------

- Update Typographical Conventions.
  https://github.com/Pylons/pyramid/pull/2838

- Add `pyramid_nacl_session
  <http://docs.pylonsproject.org/projects/pyramid-nacl-session/en/latest/>`_
  to session factories. See https://github.com/Pylons/pyramid/issues/2791

- Update ``HACKING.txt`` from stale branch that was never merged to master.
  See https://github.com/Pylons/pyramid/pull/2782

- Updated Windows installation instructions and related bits.
  See https://github.com/Pylons/pyramid/issues/2661

- Fix an inconsistency in the documentation between view predicates and
  route predicates and highlight the differences in their APIs.
  See https://github.com/Pylons/pyramid/pull/2764

- Clarify a possible misuse of the ``headers`` kwarg to subclasses of
  ``pyramid.httpexceptions.HTTPException`` in which more appropriate
  kwargs from the parent class ``pyramid.response.Response`` should be
  used instead. See https://github.com/Pylons/pyramid/pull/2750

- The SQLAlchemy + URL Dispatch + Jinja2 (``wiki2``) and
  ZODB + Traversal + Chameleon (``wiki``) tutorials have been updated to
  utilize the new cookiecutters and drop support for the ``pcreate``
  scaffolds.

  See https://github.com/Pylons/pyramid/pull/2881 and
  https://github.com/Pylons/pyramid/pull/2883.

- Improve output of p* script descriptions for help.
  See https://github.com/Pylons/pyramid/pull/2886

- Quick Tour updated to use cookiecutters instead of pcreate and scaffolds.
  See https://github.com/Pylons/pyramid/pull/2888

1.7 (2016-05-19)
================

- Fix a bug in the wiki2 tutorial where bcrypt is always expecting byte
  strings. See https://github.com/Pylons/pyramid/pull/2576

- Simplify windows detection code and remove some duplicated data.
  See https://github.com/Pylons/pyramid/pull/2585 and
  https://github.com/Pylons/pyramid/pull/2586

1.7b4 (2016-05-12)
==================

- Fixed the exception view tween to re-raise the original exception if
  no exception view could be found to handle the exception. This better
  allows tweens further up the chain to handle exceptions that were
  left unhandled. Previously they would be converted into a
  ``PredicateMismatch`` exception if predicates failed to allow the view to
  handle the exception.
  See https://github.com/Pylons/pyramid/pull/2567

- Exposed the ``pyramid.interfaces.IRequestFactory`` interface to mirror
  the public ``pyramid.interfaces.IResponseFactory`` interface.

1.7b3 (2016-05-10)
==================

- Fix ``request.invoke_exception_view`` to raise an ``HTTPNotFound``
  exception if no view is matched. Previously ``None`` would be returned
  if no views were matched and a ``PredicateMismatch`` would be raised if
  a view "almost" matched (a view was found matching the context).
  See https://github.com/Pylons/pyramid/pull/2564

- Add defaults for py.test configuration and coverage to all three scaffolds,
  and update documentation accordingly.
  See https://github.com/Pylons/pyramid/pull/2550

- Add ``linkcheck`` to ``Makefile`` for Sphinx. To check the documentation for
  broken links, use the command ``make linkcheck
  SPHINXBUILD=$VENV/bin/sphinx-build``. Also removed and fixed dozens of broken
  external links.

- Fix the internal runner for scaffold tests to ensure they work with pip
  and py.test.
  See https://github.com/Pylons/pyramid/pull/2565

1.7b2 (2016-05-01)
==================

- Removed inclusion of pyramid_tm in development.ini for alchemy scaffold
  See https://github.com/Pylons/pyramid/issues/2538

- A default permission set via ``config.set_default_permission`` will no
  longer be enforced on an exception view. This has been the case for a while
  with the default exception views (``config.add_notfound_view`` and
  ``config.add_forbidden_view``), however for any other exception view a
  developer had to remember to set ``permission=NO_PERMISSION_REQUIRED`` or
  be surprised when things didn't work. It is still possible to force a
  permission check on an exception view by setting the ``permission`` argument
  manually to ``config.add_view``. This behavior is consistent with the new
  CSRF features added in the 1.7 series.
  See https://github.com/Pylons/pyramid/pull/2534

1.7b1 (2016-04-25)
==================

- This release announces the beta period for 1.7.

- Fix an issue where some files were being included in the alchemy scafffold
  which had been removed from the 1.7 series.
  See https://github.com/Pylons/pyramid/issues/2525

1.7a2 (2016-04-19)
==================

Features
--------

- Automatic CSRF checks are now disabled by default on exception views. They
  can be turned back on by setting the appropriate `require_csrf` option on
  the view.
  See https://github.com/Pylons/pyramid/pull/2517

- The automatic CSRF API was reworked to use a config directive for
  setting the options. The ``pyramid.require_default_csrf`` setting is
  no longer supported. Instead, a new ``config.set_default_csrf_options``
  directive has been introduced that allows the developer to specify
  the default value for ``require_csrf`` as well as change the CSRF token,
  header and safe request methods. The ``pyramid.csrf_trusted_origins``
  setting is still supported.
  See https://github.com/Pylons/pyramid/pull/2518

Bug fixes
---------

- CSRF origin checks had a bug causing the checks to always fail.
  See https://github.com/Pylons/pyramid/pull/2512

- Fix the test suite to pass on windows.
  See https://github.com/Pylons/pyramid/pull/2520

1.7a1 (2016-04-16)
==================

Backward Incompatibilities
--------------------------

- Following the Pyramid deprecation period (1.4 -> 1.6),
  AuthTktAuthenticationPolicy's default hashing algorithm is changing from md5
  to sha512. If you are using the authentication policy and need to continue
  using md5, please explicitly set hashalg to 'md5'.

  This change does mean that any existing auth tickets (and associated cookies)
  will no longer be valid, and users will no longer be logged in, and have to
  login to their accounts again.

  See https://github.com/Pylons/pyramid/pull/2496

- The ``check_csrf_token`` function no longer validates a csrf token in the
  query string of a request. Only headers and request bodies are supported.
  See https://github.com/Pylons/pyramid/pull/2500

Features
--------

- Added a new setting, ``pyramid.require_default_csrf`` which may be used
  to turn on CSRF checks globally for every POST request in the application.
  This should be considered a good default for websites built on Pyramid.
  It is possible to opt-out of CSRF checks on a per-view basis by setting
  ``require_csrf=False`` on those views.
  See https://github.com/Pylons/pyramid/pull/2413

- Added a ``require_csrf`` view option which will enforce CSRF checks on any
  request with an unsafe method as defined by RFC2616. If the CSRF check fails
  a ``BadCSRFToken`` exception will be raised and may be caught by exception
  views (the default response is a ``400 Bad Request``). This option should be
  used in place of the deprecated ``check_csrf`` view predicate which would
  normally result in unexpected ``404 Not Found`` response to the client
  instead of a catchable exception.  See
  https://github.com/Pylons/pyramid/pull/2413 and
  https://github.com/Pylons/pyramid/pull/2500

- Added an additional CSRF validation that checks the origin/referrer of a
  request and makes sure it matches the current ``request.domain``. This
  particular check is only active when accessing a site over HTTPS as otherwise
  browsers don't always send the required information. If this additional CSRF
  validation fails a ``BadCSRFOrigin`` exception will be raised and may be
  caught by exception views (the default response is ``400 Bad Request``).
  Additional allowed origins may be configured by setting
  ``pyramid.csrf_trusted_origins`` to a list of domain names (with ports if on
  a non standard port) to allow. Subdomains are not allowed unless the domain
  name has been prefixed with a ``.``. See
  https://github.com/Pylons/pyramid/pull/2501

- Added a new ``pyramid.session.check_csrf_origin`` API for validating the
  origin or referrer headers against the request's domain.
  See https://github.com/Pylons/pyramid/pull/2501

- Pyramid HTTPExceptions will now take into account the best match for the
  clients Accept header, and depending on what is requested will return
  text/html, application/json or text/plain. The default for */* is still
  text/html, but if application/json is explicitly mentioned it will now
  receive a valid JSON response. See
  https://github.com/Pylons/pyramid/pull/2489

- A new event and interface (BeforeTraversal) has been introduced that will
  notify listeners before traversal starts in the router. See
  https://github.com/Pylons/pyramid/pull/2469 and
  https://github.com/Pylons/pyramid/pull/1876

- Add a new "view deriver" concept to Pyramid to allow framework authors to
  inject elements into the standard Pyramid view pipeline and affect all
  views in an application. This is similar to a decorator except that it
  has access to options passed to ``config.add_view`` and can affect other
  stages of the pipeline such as the raw response from a view or prior to
  security checks. See https://github.com/Pylons/pyramid/pull/2021

- Allow a leading ``=`` on the key of the request param predicate.
  For example, '=abc=1' is equivalent down to
  ``request.params['=abc'] == '1'``.
  See https://github.com/Pylons/pyramid/pull/1370

- A new ``request.invoke_exception_view(...)`` method which can be used to
  invoke an exception view and get back a response. This is useful for
  rendering an exception view outside of the context of the excview tween
  where you may need more control over the request.
  See https://github.com/Pylons/pyramid/pull/2393

- Allow using variable substitutions like ``%(LOGGING_LOGGER_ROOT_LEVEL)s``
  for logging sections of the .ini file and populate these variables from
  the ``pserve`` command line -- e.g.:
  ``pserve development.ini LOGGING_LOGGER_ROOT_LEVEL=DEBUG``
  See https://github.com/Pylons/pyramid/pull/2399

Documentation Changes
---------------------

- A complete overhaul of the docs:

  - Use pip instead of easy_install.
  - Become opinionated by preferring Python 3.4 or greater to simplify
    installation of Python and its required packaging tools.
  - Use venv for the tool, and virtual environment for the thing created,
    instead of virtualenv.
  - Use py.test and pytest-cov instead of nose and coverage.
  - Further updates to the scaffolds as well as tutorials and their src files.

  See https://github.com/Pylons/pyramid/pull/2468

- A complete overhaul of the ``alchemy`` scaffold as well as the
  Wiki2 SQLAlchemy + URLDispatch tutorial to introduce more modern features
  into the usage of SQLAlchemy with Pyramid and provide a better starting
  point for new projects.
  See https://github.com/Pylons/pyramid/pull/2024

Bug Fixes
---------

- Fix ``pserve --browser`` to use the ``--server-name`` instead of the
  app name when selecting a section to use. This was only working for people
  who had server and app sections with the same name, for example
  ``[app:main]`` and ``[server:main]``.
  See https://github.com/Pylons/pyramid/pull/2292

Deprecations
------------

- The ``check_csrf`` view predicate has been deprecated. Use the
  new ``require_csrf`` option or the ``pyramid.require_default_csrf`` setting
  to ensure that the ``BadCSRFToken`` exception is raised.
  See https://github.com/Pylons/pyramid/pull/2413

- Support for Python 3.3 will be removed in Pyramid 1.8.
  https://github.com/Pylons/pyramid/issues/2477

- Python 2.6 is no longer supported by Pyramid. See
  https://github.com/Pylons/pyramid/issues/2368

- Dropped Python 3.2 support.
  See https://github.com/Pylons/pyramid/pull/2256

1.6 (2016-01-03)
================

Deprecations
------------

- Continue removal of ``pserve`` daemon/process management features
  by deprecating ``--user`` and ``--group`` options.
  See https://github.com/Pylons/pyramid/pull/2190

1.6b3 (2015-12-17)
==================

Backward Incompatibilities
--------------------------

- Remove the ``cachebust`` option from ``config.add_static_view``. See
  ``config.add_cache_buster`` for the new way to attach cache busters to
  static assets.
  See https://github.com/Pylons/pyramid/pull/2186

- Modify the ``pyramid.interfaces.ICacheBuster`` API to be a simple callable
  instead of an object with ``match`` and ``pregenerate`` methods. Cache
  busters are now focused solely on generation. Matching has been dropped.

  Note this affects usage of ``pyramid.static.QueryStringCacheBuster`` and
  ``pyramid.static.ManifestCacheBuster``.

  See https://github.com/Pylons/pyramid/pull/2186

Features
--------

- Add a new ``config.add_cache_buster`` API for attaching cache busters to
  static assets. See https://github.com/Pylons/pyramid/pull/2186

Bug Fixes
---------

- Ensure that ``IAssetDescriptor.abspath`` always returns an absolute path.
  There were cases depending on the process CWD that a relative path would
  be returned. See https://github.com/Pylons/pyramid/issues/2188

1.6b2 (2015-10-15)
==================

Features
--------

- Allow asset specifications to be supplied to
  ``pyramid.static.ManifestCacheBuster`` instead of requiring a
  filesystem path.

1.6b1 (2015-10-15)
==================

Backward Incompatibilities
--------------------------

- IPython and BPython support have been removed from pshell in the core.
  To continue using them on Pyramid 1.6+ you must install the binding
  packages explicitly::

    $ pip install pyramid_ipython

    or

    $ pip install pyramid_bpython

- Remove default cache busters introduced in 1.6a1 including
  ``PathSegmentCacheBuster``, ``PathSegmentMd5CacheBuster``, and
  ``QueryStringMd5CacheBuster``.
  See https://github.com/Pylons/pyramid/pull/2116

Features
--------

- Additional shells for ``pshell`` can now be registered as entrypoints. See
  https://github.com/Pylons/pyramid/pull/1891 and
  https://github.com/Pylons/pyramid/pull/2012

- The variables injected into ``pshell`` are now displayed with their
  docstrings instead of the default ``str(obj)`` when possible.
  See https://github.com/Pylons/pyramid/pull/1929

- Add new ``pyramid.static.ManifestCacheBuster`` for use with external
  asset pipelines as well as examples of common usages in the narrative.
  See https://github.com/Pylons/pyramid/pull/2116

- Fix ``pserve --reload`` to not crash on syntax errors!!!
  See https://github.com/Pylons/pyramid/pull/2125

- Fix an issue when user passes unparsed strings to ``pyramid.session.CookieSession``
  and ``pyramid.authentication.AuthTktCookieHelper`` for time related parameters
  ``timeout``, ``reissue_time``, ``max_age`` that expect an integer value.
  See https://github.com/Pylons/pyramid/pull/2050

Bug Fixes
---------

- ``pyramid.httpexceptions.HTTPException`` now defaults to
  ``520 Unknown Error`` instead of ``None None`` to conform with changes in
  WebOb 1.5.
  See https://github.com/Pylons/pyramid/pull/1865

- ``pshell`` will now preserve the capitalization of variables in the
  ``[pshell]`` section of the INI file. This makes exposing classes to the
  shell a little more straightforward.
  See https://github.com/Pylons/pyramid/pull/1883

- Fixed usage of ``pserve --monitor-restart --daemon`` which would fail in
  horrible ways. See https://github.com/Pylons/pyramid/pull/2118

- Explicitly prevent ``pserve --reload --daemon`` from being used. It's never
  been supported but would work and fail in weird ways.
  See https://github.com/Pylons/pyramid/pull/2119

- Fix an issue on Windows when running ``pserve --reload`` in which the
  process failed to fork because it could not find the pserve script to
  run. See https://github.com/Pylons/pyramid/pull/2138

Deprecations
------------

- Deprecate ``pserve --monitor-restart`` in favor of user's using a real
  process manager such as Systemd or Upstart as well as Python-based
  solutions like Circus and Supervisor.
  See https://github.com/Pylons/pyramid/pull/2120

1.6a2 (2015-06-30)
==================

Bug Fixes
---------

- Ensure that ``pyramid.httpexceptions.exception_response`` returns the
  appropriate "concrete" class for ``400`` and ``500`` status codes.
  See https://github.com/Pylons/pyramid/issues/1832

- Fix an infinite recursion bug introduced in 1.6a1 when
  ``pyramid.view.render_view_to_response`` was called directly or indirectly.
  See https://github.com/Pylons/pyramid/issues/1643

- Further fix the JSONP renderer by prefixing the returned content with
  a comment. This should mitigate attacks from Flash (See CVE-2014-4671).
  See https://github.com/Pylons/pyramid/pull/1649

- Allow periods and brackets (``[]``) in the JSONP callback. The original
  fix was overly-restrictive and broke Angular.
  See https://github.com/Pylons/pyramid/pull/1649

1.6a1 (2015-04-15)
==================

Features
--------

- pcreate will now ask for confirmation if invoked with
  an argument for a project name that already exists or
  is importable in the current environment.
  See https://github.com/Pylons/pyramid/issues/1357 and
  https://github.com/Pylons/pyramid/pull/1837

- Make it possible to subclass ``pyramid.request.Request`` and also use
  ``pyramid.request.Request.add_request.method``.  See
  https://github.com/Pylons/pyramid/issues/1529

- The ``pyramid.config.Configurator`` has grown the ability to allow
  actions to call other actions during a commit-cycle. This enables much more
  logic to be placed into actions, such as the ability to invoke other actions
  or group them for improved conflict detection. We have also exposed and
  documented the config phases that Pyramid uses in order to further assist
  in building conforming addons.
  See https://github.com/Pylons/pyramid/pull/1513

- Add ``pyramid.request.apply_request_extensions`` function which can be
  used in testing to apply any request extensions configured via
  ``config.add_request_method``. Previously it was only possible to test
  the extensions by going through Pyramid's router.
  See https://github.com/Pylons/pyramid/pull/1581

- pcreate when run without a scaffold argument will now print information on
  the missing flag, as well as a list of available scaffolds.
  See https://github.com/Pylons/pyramid/pull/1566 and
  https://github.com/Pylons/pyramid/issues/1297

- Added support / testing for 'pypy3' under Tox and Travis.
  See https://github.com/Pylons/pyramid/pull/1469

- Automate code coverage metrics across py2 and py3 instead of just py2.
  See https://github.com/Pylons/pyramid/pull/1471

- Cache busting for static resources has been added and is available via a new
  argument to ``pyramid.config.Configurator.add_static_view``: ``cachebust``.
  Core APIs are shipped for both cache busting via query strings and
  path segments and may be extended to fit into custom asset pipelines.
  See https://github.com/Pylons/pyramid/pull/1380 and
  https://github.com/Pylons/pyramid/pull/1583

- Add ``pyramid.config.Configurator.root_package`` attribute and init
  parameter to assist with includeable packages that wish to resolve
  resources relative to the package in which the ``Configurator`` was created.
  This is especially useful for addons that need to load asset specs from
  settings, in which case it is may be natural for a developer to define
  imports or assets relative to the top-level package.
  See https://github.com/Pylons/pyramid/pull/1337

- Added line numbers to the log formatters in the scaffolds to assist with
  debugging. See https://github.com/Pylons/pyramid/pull/1326

- Add new HTTP exception objects for status codes
  ``428 Precondition Required``, ``429 Too Many Requests`` and
  ``431 Request Header Fields Too Large`` in ``pyramid.httpexceptions``.
  See https://github.com/Pylons/pyramid/pull/1372/files

- The ``pshell`` script will now load a ``PYTHONSTARTUP`` file if one is
  defined in the environment prior to launching the interpreter.
  See https://github.com/Pylons/pyramid/pull/1448

- Make it simple to define notfound and forbidden views that wish to use
  the default exception-response view but with altered predicates and other
  configuration options. The ``view`` argument is now optional in
  ``config.add_notfound_view`` and ``config.add_forbidden_view``..
  See https://github.com/Pylons/pyramid/issues/494

- Greatly improve the readability of the ``pcreate`` shell script output.
  See https://github.com/Pylons/pyramid/pull/1453

- Improve robustness to timing attacks in the ``AuthTktCookieHelper`` and
  the ``SignedCookieSessionFactory`` classes by using the stdlib's
  ``hmac.compare_digest`` if it is available (such as Python 2.7.7+ and 3.3+).
  See https://github.com/Pylons/pyramid/pull/1457

- Assets can now be overidden by an absolute path on the filesystem when using
  the ``config.override_asset`` API. This makes it possible to fully support
  serving up static content from a mutable directory while still being able
  to use the ``request.static_url`` API and ``config.add_static_view``.
  Previously it was not possible to use ``config.add_static_view`` with an
  absolute path **and** generate urls to the content. This change replaces
  the call, ``config.add_static_view('/abs/path', 'static')``, with
  ``config.add_static_view('myapp:static', 'static')`` and
  ``config.override_asset(to_override='myapp:static/',
  override_with='/abs/path/')``. The ``myapp:static`` asset spec is completely
  made up and does not need to exist - it is used for generating urls
  via ``request.static_url('myapp:static/foo.png')``.
  See https://github.com/Pylons/pyramid/issues/1252

- Added ``pyramid.config.Configurator.set_response_factory`` and the
  ``response_factory`` keyword argument to the ``Configurator`` for defining
  a factory that will return a custom ``Response`` class.
  See https://github.com/Pylons/pyramid/pull/1499

- Allow an iterator to be returned from a renderer. Previously it was only
  possible to return bytes or unicode.
  See https://github.com/Pylons/pyramid/pull/1417

- ``pserve`` can now take a ``-b`` or ``--browser`` option to open the server
  URL in a web browser. See https://github.com/Pylons/pyramid/pull/1533

- Overall improvements for the ``proutes`` command. Added ``--format`` and
  ``--glob`` arguments to the command, introduced the ``method``
  column for displaying available request methods, and improved the ``view``
  output by showing the module instead of just ``__repr__``.
  See https://github.com/Pylons/pyramid/pull/1488

- Support keyword-only arguments and function annotations in views in
  Python 3. See https://github.com/Pylons/pyramid/pull/1556

- ``request.response`` will no longer be mutated when using the
  ``pyramid.renderers.render_to_response()`` API.  It is now necessary to
  pass in a ``response=`` argument to ``render_to_response`` if you wish to
  supply the renderer with a custom response object for it to use. If you
  do not pass one then a response object will be created using the
  application's ``IResponseFactory``. Almost all renderers
  mutate the ``request.response`` response object (for example, the JSON
  renderer sets ``request.response.content_type`` to ``application/json``).
  However, when invoking ``render_to_response`` it is not expected that the
  response object being returned would be the same one used later in the
  request. The response object returned from ``render_to_response`` is now
  explicitly different from ``request.response``. This does not change the
  API of a renderer. See https://github.com/Pylons/pyramid/pull/1563

- The ``append_slash`` argument of ```Configurator().add_notfound_view()`` will
  now accept anything that implements the ``IResponse`` interface and will use
  that as the response class instead of the default ``HTTPFound``.  See
  https://github.com/Pylons/pyramid/pull/1610

Bug Fixes
---------

- The JSONP renderer created JavaScript code in such a way that a callback
  variable could be used to arbitrarily inject javascript into the response
  object. https://github.com/Pylons/pyramid/pull/1627

- Work around an issue where ``pserve --reload`` would leave terminal echo
  disabled if it reloaded during a pdb session.
  See https://github.com/Pylons/pyramid/pull/1577,
  https://github.com/Pylons/pyramid/pull/1592

- ``pyramid.wsgi.wsgiapp`` and ``pyramid.wsgi.wsgiapp2`` now raise
  ``ValueError`` when accidentally passed ``None``.
  See https://github.com/Pylons/pyramid/pull/1320

- Fix an issue whereby predicates would be resolved as maybe_dotted in the
  introspectable but not when passed for registration. This would mean that
  ``add_route_predicate`` for example can not take a string and turn it into
  the actual callable function.
  See https://github.com/Pylons/pyramid/pull/1306

- Fix ``pyramid.testing.setUp`` to return a ``Configurator`` with a proper
  package. Previously it was not possible to do package-relative includes
  using the returned ``Configurator`` during testing. There is now a
  ``package`` argument that can override this behavior as well.
  See https://github.com/Pylons/pyramid/pull/1322

- Fix an issue where a ``pyramid.response.FileResponse`` may apply a charset
  where it does not belong. See https://github.com/Pylons/pyramid/pull/1251

- Work around a bug introduced in Python 2.7.7 on Windows where
  ``mimetypes.guess_type`` returns Unicode rather than str for the content
  type, unlike any previous version of Python.  See
  https://github.com/Pylons/pyramid/issues/1360 for more information.

- ``pcreate`` now normalizes the package name by converting hyphens to
  underscores. See https://github.com/Pylons/pyramid/pull/1376

- Fix an issue with the final response/finished callback being unable to
  add another callback to the list. See
  https://github.com/Pylons/pyramid/pull/1373

- Fix a failing unittest caused by differing mimetypes across various OSs.
  See https://github.com/Pylons/pyramid/issues/1405

- Fix route generation for static view asset specifications having no path.
  See https://github.com/Pylons/pyramid/pull/1377

- Allow the ``pyramid.renderers.JSONP`` renderer to work even if there is no
  valid request object. In this case it will not wrap the object in a
  callback and thus behave just like the ``pyramid.renderers.JSON`` renderer.
  See https://github.com/Pylons/pyramid/pull/1561

- Prevent "parameters to load are deprecated" ``DeprecationWarning``
  from setuptools>=11.3. See https://github.com/Pylons/pyramid/pull/1541

- Avoiding sharing the ``IRenderer`` objects across threads when attached to
  a view using the `renderer=` argument. These renderers were instantiated
  at time of first render and shared between requests, causing potentially
  subtle effects like `pyramid.reload_templates = true` failing to work
  in `pyramid_mako`. See https://github.com/Pylons/pyramid/pull/1575
  and https://github.com/Pylons/pyramid/issues/1268

- Avoiding timing attacks against CSRF tokens.
  See https://github.com/Pylons/pyramid/pull/1574

- ``request.finished_callbacks`` and ``request.response_callbacks`` now
  default to an iterable instead of ``None``. It may be checked for a length
  of 0. This was the behavior in 1.5.

Deprecations
------------

- The ``pserve`` command's daemonization features have been deprecated. This
  includes the ``[start,stop,restart,status]`` subcommands as well as the
  ``--daemon``, ``--stop-server``, ``--pid-file``, and ``--status`` flags.

  Please use a real process manager in the future instead of relying on the
  ``pserve`` to daemonize itself. Many options exist including your Operating
  System's services such as Systemd or Upstart, as well as Python-based
  solutions like Circus and Supervisor.

  See https://github.com/Pylons/pyramid/pull/1641

- Renamed the ``principal`` argument to ``pyramid.security.remember()`` to
  ``userid`` in order to clarify its intended purpose.
  See https://github.com/Pylons/pyramid/pull/1399

Docs
----

- Moved the documentation for ``accept`` on ``Configurator.add_view`` to no
  longer be part of the predicate list. See
  https://github.com/Pylons/pyramid/issues/1391 for a bug report stating
  ``not_`` was failing on ``accept``. Discussion with @mcdonc led to the
  conclusion that it should not be documented as a predicate.
  See https://github.com/Pylons/pyramid/pull/1487 for this PR

- Removed logging configuration from Quick Tutorial ini files except for
  scaffolding- and logging-related chapters to avoid needing to explain it too
  early.

- Clarify a previously-implied detail of the ``ISession.invalidate`` API
  documentation.

- Improve and clarify the documentation on what Pyramid defines as a
  ``principal`` and a ``userid`` in its security APIs.
  See https://github.com/Pylons/pyramid/pull/1399

- Add documentation of command line programs (``p*`` scripts). See
  https://github.com/Pylons/pyramid/pull/2191

Scaffolds
---------

- Update scaffold generating machinery to return the version of pyramid and
  pyramid docs for use in scaffolds. Updated starter, alchemy and zodb
  templates to have links to correctly versioned documentation and reflect
  which pyramid was used to generate the scaffold.

- Removed non-ascii copyright symbol from templates, as this was
  causing the scaffolds to fail for project generation.

- You can now run the scaffolding func tests via ``tox py2-scaffolds`` and
  ``tox py3-scaffolds``.


1.5 (2014-04-08)
================

- Python 3.4 compatibility.

- Avoid crash in ``pserve --reload`` under Py3k, when iterating over possibly
  mutated ``sys.modules``.

- ``UnencryptedCookieSessionFactoryConfig`` failed if the secret contained
  higher order characters. See https://github.com/Pylons/pyramid/issues/1246

- Fixed a bug in ``UnencryptedCookieSessionFactoryConfig`` and
  ``SignedCookieSessionFactory`` where ``timeout=None`` would cause a new
  session to always be created. Also in ``SignedCookieSessionFactory`` a
  ``reissue_time=None`` would cause an exception when modifying the session.
  See https://github.com/Pylons/pyramid/issues/1247

- Updated docs and scaffolds to keep in step with new 2.0 release of
  ``Lingua``.  This included removing all ``setup.cfg`` files from scaffolds
  and documentation environments.

1.5b1 (2014-02-08)
==================

Features
--------

- We no longer eagerly clear ``request.exception`` and ``request.exc_info`` in
  the exception view tween.  This makes it possible to inspect exception
  information within a finished callback.  See
  https://github.com/Pylons/pyramid/issues/1223.

1.5a4 (2014-01-28)
==================

Features
--------

- Updated scaffolds with new theme, fixed documentation and sample project.

Bug Fixes
---------

- Depend on a newer version of WebOb so that we pull in some crucial bug-fixes
  that were showstoppers for functionality in Pyramid.

- Add a trailing semicolon to the JSONP response. This fixes JavaScript syntax
  errors for old IE versions. See https://github.com/Pylons/pyramid/pull/1205

- Fix a memory leak when the configurator's ``set_request_property`` method was
  used or when the configurator's ``add_request_method`` method was used with
  the ``property=True`` attribute.  See
  https://github.com/Pylons/pyramid/issues/1212 .

1.5a3 (2013-12-10)
==================

Features
--------

- An authorization API has been added as a method of the
  request: ``request.has_permission``.

  ``request.has_permission`` is a method-based alternative to the
  ``pyramid.security.has_permission`` API and works exactly the same.  The
  older API is now deprecated.

- Property API attributes have been added to the request for easier access to
  authentication data: ``request.authenticated_userid``,
  ``request.unauthenticated_userid``, and ``request.effective_principals``.

  These are analogues, respectively, of
  ``pyramid.security.authenticated_userid``,
  ``pyramid.security.unauthenticated_userid``, and
  ``pyramid.security.effective_principals``.  They operate exactly the same,
  except they are attributes of the request instead of functions accepting a
  request.  They are properties, so they cannot be assigned to.  The older
  function-based APIs are now deprecated.

- Pyramid's console scripts (``pserve``, ``pviews``, etc) can now be run
  directly, allowing custom arguments to be sent to the python interpreter
  at runtime. For example::

      python -3 -m pyramid.scripts.pserve development.ini

- Added a specific subclass of ``HTTPBadRequest`` named
  ``pyramid.exceptions.BadCSRFToken`` which will now be raised in response
  to failures in ``check_csrf_token``.
  See https://github.com/Pylons/pyramid/pull/1149

- Added a new ``SignedCookieSessionFactory`` which is very similar to the
  ``UnencryptedCookieSessionFactoryConfig`` but with a clearer focus on signing
  content. The custom serializer arguments to this function should only focus
  on serializing, unlike its predecessor which required the serializer to also
  perform signing.  See https://github.com/Pylons/pyramid/pull/1142 .  Note
  that cookies generated using ``SignedCookieSessionFactory`` are not
  compatible with cookies generated using ``UnencryptedCookieSessionFactory``,
  so existing user session data will be destroyed if you switch to it.

- Added a new ``BaseCookieSessionFactory`` which acts as a generic cookie
  factory that can be used by framework implementors to create their own
  session implementations. It provides a reusable API which focuses strictly
  on providing a dictionary-like object that properly handles renewals,
  timeouts, and conformance with the ``ISession`` API.
  See https://github.com/Pylons/pyramid/pull/1142

- The anchor argument to ``pyramid.request.Request.route_url`` and
  ``pyramid.request.Request.resource_url`` and their derivatives will now be
  escaped via URL quoting to ensure minimal conformance.  See
  https://github.com/Pylons/pyramid/pull/1183

- Allow sending of ``_query`` and ``_anchor`` options to
  ``pyramid.request.Request.static_url`` when an external URL is being
  generated.
  See https://github.com/Pylons/pyramid/pull/1183

- You can now send a string as the ``_query`` argument to
  ``pyramid.request.Request.route_url`` and
  ``pyramid.request.Request.resource_url`` and their derivatives.  When a
  string is sent instead of a list or dictionary. it is URL-quoted however it
  does not need to be in ``k=v`` form.  This is useful if you want to be able
  to use a different query string format than ``x-www-form-urlencoded``.  See
  https://github.com/Pylons/pyramid/pull/1183

- ``pyramid.testing.DummyRequest`` now has a ``domain`` attribute to match the
  new WebOb 1.3 API.  Its value is ``example.com``.

Bug Fixes
---------

- Fix the ``pcreate`` script so that when the target directory name ends with a
  slash it does not produce a non-working project directory structure.
  Previously saying ``pcreate -s starter /foo/bar/`` produced different output
  than  saying ``pcreate -s starter /foo/bar``.  The former did not work
  properly.

- Fix the ``principals_allowed_by_permission`` method of
  ``ACLAuthorizationPolicy`` so it anticipates a callable ``__acl__``
  on resources.  Previously it did not try to call the ``__acl__``
  if it was callable.

- The ``pviews`` script did not work when a url required custom request
  methods in order to perform traversal. Custom methods and descriptors added
  via ``pyramid.config.Configurator.add_request_method`` will now be present,
  allowing traversal to continue.
  See https://github.com/Pylons/pyramid/issues/1104

- Remove unused ``renderer`` argument from ``Configurator.add_route``.

- Allow the ``BasicAuthenticationPolicy`` to work with non-ascii usernames
  and passwords. The charset is not passed as part of the header and different
  browsers alternate between UTF-8 and Latin-1, so the policy now attempts
  to decode with UTF-8 first, and will fallback to Latin-1.
  See https://github.com/Pylons/pyramid/pull/1170

- The ``@view_defaults`` now apply to notfound and forbidden views
  that are defined as methods of a decorated class.
  See https://github.com/Pylons/pyramid/issues/1173

Documentation
-------------

- Added a "Quick Tutorial" to go with the Quick Tour

- Removed mention of ``pyramid_beaker`` from docs.  Beaker is no longer
  maintained.  Point people at ``pyramid_redis_sessions`` instead.

- Add documentation for ``pyramid.interfaces.IRendererFactory`` and
  ``pyramid.interfaces.IRenderer``.

Backwards Incompatibilities
---------------------------

- The key/values in the ``_query`` parameter of ``request.route_url`` and the
  ``query`` parameter of ``request.resource_url`` (and their variants), used
  to encode a value of ``None`` as the string ``'None'``, leaving the resulting
  query string to be ``a=b&key=None``. The value is now dropped in this
  situation, leaving a query string of ``a=b&key=``.
  See https://github.com/Pylons/pyramid/issues/1119

Deprecations
------------

- Deprecate the ``pyramid.interfaces.ITemplateRenderer`` interface. It was
  ill-defined and became unused when Mako and Chameleon template bindings were
  split into their own packages.

- The ``pyramid.session.UnencryptedCookieSessionFactoryConfig`` API has been
  deprecated and is superseded by the
  ``pyramid.session.SignedCookieSessionFactory``.  Note that while the cookies
  generated by the ``UnencryptedCookieSessionFactoryConfig``
  are compatible with cookies generated by old releases, cookies generated by
  the SignedCookieSessionFactory are not. See
  https://github.com/Pylons/pyramid/pull/1142

- The ``pyramid.security.has_permission`` API is now deprecated.  Instead, use
  the newly-added ``has_permission`` method of the request object.

- The ``pyramid.security.effective_principals`` API is now deprecated.
  Instead, use the newly-added ``effective_principals`` attribute of the
  request object.

- The ``pyramid.security.authenticated_userid`` API is now deprecated.
  Instead, use the newly-added ``authenticated_userid`` attribute of the
  request object.

- The ``pyramid.security.unauthenticated_userid`` API is now deprecated.
  Instead, use the newly-added ``unauthenticated_userid`` attribute of the
  request object.

Dependencies
------------

- Pyramid now depends on WebOb>=1.3 (it uses ``webob.cookies.CookieProfile``
  from 1.3+).

1.5a2 (2013-09-22)
==================

Features
--------

- Users can now provide dotted Python names to as the ``factory`` argument
  the Configurator methods named ``add_{view,route,subscriber}_predicate``
  (instead of passing the predicate factory directly, you can pass a
  dotted name which refers to the factory).

Bug Fixes
---------

- Fix an exception in ``pyramid.path.package_name`` when resolving the package
  name for namespace packages that had no ``__file__`` attribute.

Backwards Incompatibilities
---------------------------

- Pyramid no longer depends on or configures the Mako and Chameleon templating
  system renderers by default.  Disincluding these templating systems by
  default means that the Pyramid core has fewer dependencies and can run on
  future platforms without immediate concern for the compatibility of its
  templating add-ons.  It also makes maintenance slightly more effective, as
  different people can maintain the templating system add-ons that they
  understand and care about without needing commit access to the Pyramid core,
  and it allows users who just don't want to see any packages they don't use
  come along for the ride when they install Pyramid.

  This means that upon upgrading to Pyramid 1.5a2+, projects that use either
  of these templating systems will see a traceback that ends something like
  this when their application attempts to render a Chameleon or Mako template::

     ValueError: No such renderer factory .pt

  Or::

     ValueError: No such renderer factory .mako

  Or::

     ValueError: No such renderer factory .mak

  Support for Mako templating has been moved into an add-on package named
  ``pyramid_mako``, and support for Chameleon templating has been moved into
  an add-on package named ``pyramid_chameleon``.  These packages are drop-in
  replacements for the old built-in support for these templating langauges.
  All you have to do is install them and make them active in your configuration
  to register renderer factories for ``.pt`` and/or ``.mako`` (or ``.mak``) to
  make your application work again.

  To re-add support for Chameleon and/or Mako template renderers into your
  existing projects, follow the below steps.

  If you depend on Mako templates:

  * Make sure the ``pyramid_mako`` package is installed.  One way to do this
    is by adding ``pyramid_mako`` to the ``install_requires`` section of your
    package's ``setup.py`` file and afterwards rerunning ``setup.py develop``::

        setup(
            #...
            install_requires=[
                'pyramid_mako',         # new dependency
                'pyramid',
                #...
            ],
        )

  * Within the portion of your application which instantiates a Pyramid
    ``pyramid.config.Configurator`` (often the ``main()`` function in
    your project's ``__init__.py`` file), tell Pyramid to include the
    ``pyramid_mako`` includeme::

        config = Configurator(.....)
        config.include('pyramid_mako')

  If you depend on Chameleon templates:

  * Make sure the ``pyramid_chameleon`` package is installed.  One way to do
    this is by adding ``pyramid_chameleon`` to the ``install_requires`` section
    of your package's ``setup.py`` file and afterwards rerunning
    ``setup.py develop``::

        setup(
            #...
            install_requires=[
                'pyramid_chameleon',         # new dependency
                'pyramid',
                #...
            ],
        )

  * Within the portion of your application which instantiates a Pyramid
    ``~pyramid.config.Configurator`` (often the ``main()`` function in
    your project's ``__init__.py`` file), tell Pyramid to include the
    ``pyramid_chameleon`` includeme::

        config = Configurator(.....)
        config.include('pyramid_chameleon')

  Note that it's also fine to install these packages into *older* Pyramids for
  forward compatibility purposes.  Even if you don't upgrade to Pyramid 1.5
  immediately, performing the above steps in a Pyramid 1.4 installation is
  perfectly fine, won't cause any difference, and will give you forward
  compatibility when you eventually do upgrade to Pyramid 1.5.

  With the removal of Mako and Chameleon support from the core, some
  unit tests that use the ``pyramid.renderers.render*`` methods may begin to
  fail.  If any of your unit tests are invoking either
  ``pyramid.renderers.render()``  or ``pyramid.renderers.render_to_response()``
  with either Mako or Chameleon templates then the
  ``pyramid.config.Configurator`` instance in effect during
  the unit test should be also be updated to include the addons, as shown
  above. For example::

        class ATest(unittest.TestCase):
            def setUp(self):
                self.config = pyramid.testing.setUp()
                self.config.include('pyramid_mako')

            def test_it(self):
                result = pyramid.renderers.render('mypkg:templates/home.mako', {})

  Or::

        class ATest(unittest.TestCase):
            def setUp(self):
                self.config = pyramid.testing.setUp()
                self.config.include('pyramid_chameleon')

            def test_it(self):
                result = pyramid.renderers.render('mypkg:templates/home.pt', {})

- If you're using the Pyramid debug toolbar, when you upgrade Pyramid to
  1.5a2+, you'll also need to upgrade the ``pyramid_debugtoolbar`` package to
  at least version 1.0.8, as older toolbar versions are not compatible with
  Pyramid 1.5a2+ due to the removal of Mako support from the core.  It's
  fine to use this newer version of the toolbar code with older Pyramids too.

- Removed the ``request.response_*`` varying attributes. These attributes
  have been deprecated since Pyramid 1.1, and as per the deprecation policy,
  have now been removed.

- ``request.response`` will no longer be mutated when using the
  ``pyramid.renderers.render()`` API.  Almost all renderers mutate the
  ``request.response`` response object (for example, the JSON renderer sets
  ``request.response.content_type`` to ``application/json``), but this is
  only necessary when the renderer is generating a response; it was a bug
  when it was done as a side effect of calling ``pyramid.renderers.render()``.

- Removed the ``bfg2pyramid`` fixer script.

- The ``pyramid.events.NewResponse`` event is now sent **after** response
  callbacks are executed.  It previously executed before response callbacks
  were executed.  Rationale: it's more useful to be able to inspect the response
  after response callbacks have done their jobs instead of before.

- Removed the class named ``pyramid.view.static`` that had been deprecated
  since Pyramid 1.1.  Instead use ``pyramid.static.static_view`` with
  ``use_subpath=True`` argument.

- Removed the ``pyramid.view.is_response`` function that had been deprecated
  since Pyramid 1.1.  Use the ``pyramid.request.Request.is_response`` method
  instead.

- Removed the ability to pass the following arguments to
  ``pyramid.config.Configurator.add_route``: ``view``, ``view_context``.
  ``view_for``, ``view_permission``, ``view_renderer``, and ``view_attr``.
  Using these arguments had been deprecated since Pyramid 1.1.  Instead of
  passing view-related arguments to ``add_route``, use a separate call to
  ``pyramid.config.Configurator.add_view`` to associate a view with a route
  using its ``route_name`` argument.  Note that this impacts the
  ``pyramid.config.Configurator.add_static_view`` function too, because it
  delegates to ``add_route``.

- Removed the ability to influence and query a ``pyramid.request.Request``
  object as if it were a dictionary.  Previously it was possible to use methods
  like ``__getitem__``, ``get``, ``items``, and other dictlike methods to
  access values in the WSGI environment.  This behavior had been deprecated
  since Pyramid 1.1.  Use methods of ``request.environ`` (a real dictionary)
  instead.

- Removed ancient backwards compatibility hack in
  ``pyramid.traversal.DefaultRootFactory`` which populated the ``__dict__`` of
  the factory with the matchdict values for compatibility with BFG 0.9.

- The ``renderer_globals_factory`` argument to the
  ``pyramid.config.Configurator` constructor and its ``setup_registry`` method
  has been removed.  The ``set_renderer_globals_factory`` method of
  ``pyramid.config.Configurator`` has also been removed.  The (internal)
  ``pyramid.interfaces.IRendererGlobals`` interface was also removed.  These
  arguments, methods and interfaces had been deprecated since 1.1.  Use a
  ``BeforeRender`` event subscriber as documented in the "Hooks" chapter of the
  Pyramid narrative documentation instead of providing renderer globals values
  to the configurator.

Deprecations
------------

- The ``pyramid.config.Configurator.set_request_property`` method now issues
  a deprecation warning when used.  It had been docs-deprecated in 1.4
  but did not issue a deprecation warning when used.

1.5a1 (2013-08-30)
==================

Features
--------

- A new http exception subclass named ``pyramid.httpexceptions.HTTPSuccessful``
  was added.  You can use this class as the ``context`` of an exception
  view to catch all 200-series "exceptions" (e.g. "raise HTTPOk").  This
  also allows you to catch *only* the ``HTTPOk`` exception itself; previously
  this was impossible because a number of other exceptions
  (such as ``HTTPNoContent``) inherited from ``HTTPOk``, but now they do not.

- You can now generate "hybrid" urldispatch/traversal URLs more easily
  by using the new ``route_name``, ``route_kw`` and ``route_remainder_name``
  arguments to  ``request.resource_url`` and ``request.resource_path``.  See
  the new section of the "Combining Traversal and URL Dispatch" documentation
  chapter entitled  "Hybrid URL Generation".

- It is now possible to escape double braces in Pyramid scaffolds (unescaped,
  these represent replacement values).  You can use ``\{\{a\}\}`` to
  represent a "bare" ``{{a}}``.  See
  https://github.com/Pylons/pyramid/pull/862

- Add ``localizer`` and ``locale_name`` properties (reified) to the request.
  See https://github.com/Pylons/pyramid/issues/508.  Note that the
  ``pyramid.i18n.get_localizer`` and ``pyramid.i18n.get_locale_name`` functions
  now simply look up these properties on the request.

- Add ``pdistreport`` script, which prints the Python version in use, the
  Pyramid version in use, and the version number and location of all Python
  distributions currently installed.

- Add the ability to invert the result of any view, route, or subscriber
  predicate using the ``not_`` class.  For example::

     from pyramid.config import not_

     @view_config(route_name='myroute', request_method=not_('POST'))
     def myview(request): ...

  The above example will ensure that the view is called if the request method
  is not POST (at least if no other view is more specific).

  The ``pyramid.config.not_`` class can be used against any value that is
  a predicate value passed in any of these contexts:

  - ``pyramid.config.Configurator.add_view``

  - ``pyramid.config.Configurator.add_route``

  - ``pyramid.config.Configurator.add_subscriber``

  - ``pyramid.view.view_config``

  - ``pyramid.events.subscriber``

- ``scripts/prequest.py``: add support for submitting ``PUT`` and ``PATCH``
  requests.  See https://github.com/Pylons/pyramid/pull/1033.  add support for
  submitting ``OPTIONS`` and ``PROPFIND`` requests, and  allow users to specify
  basic authentication credentials in the request via a ``--login`` argument to
  the script.  See https://github.com/Pylons/pyramid/pull/1039.

- ``ACLAuthorizationPolicy`` supports ``__acl__`` as a callable. This
  removes the ambiguity between the potential ``AttributeError`` that would
  be raised on the ``context`` when the property was not defined and the
  ``AttributeError`` that could be raised from any user-defined code within
  a dynamic property. It is recommended to define a dynamic ACL as a callable
  to avoid this ambiguity. See https://github.com/Pylons/pyramid/issues/735.

- Allow a protocol-relative URL (e.g. ``//example.com/images``) to be passed to
  ``pyramid.config.Configurator.add_static_view``. This allows
  externally-hosted static URLs to be generated based on the current protocol.

- The ``AuthTktAuthenticationPolicy`` has two new options to configure its
  domain usage:

  * ``parent_domain``: if set the authentication cookie is set on
    the parent domain. This is useful if you have multiple sites sharing the
    same domain.
  * ``domain``: if provided the cookie is always set for this domain, bypassing
    all usual logic.

  See https://github.com/Pylons/pyramid/pull/1028,
  https://github.com/Pylons/pyramid/pull/1072 and
  https://github.com/Pylons/pyramid/pull/1078.

- The ``AuthTktAuthenticationPolicy`` now supports IPv6 addresses when using
  the ``include_ip=True`` option. This is possibly incompatible with
  alternative ``auth_tkt`` implementations, as the specification does not
  define how to properly handle IPv6. See
  https://github.com/Pylons/pyramid/issues/831.

- Make it possible to use variable arguments via
  ``pyramid.paster.get_appsettings``. This also allowed the generated
  ``initialize_db`` script from the ``alchemy`` scaffold to grow support
  for options in the form ``a=1 b=2`` so you can fill in
  values in a parameterized ``.ini`` file, e.g.
  ``initialize_myapp_db etc/development.ini a=1 b=2``.
  See https://github.com/Pylons/pyramid/pull/911

- The ``request.session.check_csrf_token()`` method and the ``check_csrf`` view
  predicate now take into account the value of the HTTP header named
  ``X-CSRF-Token`` (as well as the ``csrf_token`` form parameter, which they
  always did).  The header is tried when the form parameter does not exist.

- View lookup will now search for valid views based on the inheritance
  hierarchy of the context. It tries to find views based on the most
  specific context first, and upon predicate failure, will move up the
  inheritance chain to test views found by the super-type of the context.
  In the past, only the most specific type containing views would be checked
  and if no matching view could be found then a PredicateMismatch would be
  raised. Now predicate mismatches don't hide valid views registered on
  super-types. Here's an example that now works::

     class IResource(Interface):

         ...

     @view_config(context=IResource)
     def get(context, request):

         ...

     @view_config(context=IResource, request_method='POST')
     def post(context, request):

         ...

     @view_config(context=IResource, request_method='DELETE')
     def delete(context, request):

         ...

     @implementer(IResource)
     class MyResource:

         ...

     @view_config(context=MyResource, request_method='POST')
     def override_post(context, request):

         ...

  Previously the override_post view registration would hide the get
  and delete views in the context of MyResource -- leading to a
  predicate mismatch error when trying to use GET or DELETE
  methods. Now the views are found and no predicate mismatch is
  raised.
  See https://github.com/Pylons/pyramid/pull/786 and
  https://github.com/Pylons/pyramid/pull/1004 and
  https://github.com/Pylons/pyramid/pull/1046

- The ``pserve`` command now takes a ``-v`` (or ``--verbose``) flag and a
  ``-q`` (or ``--quiet``) flag.  Output from running ``pserve`` can be
  controlled using these flags.  ``-v`` can be specified multiple times to
  increase verbosity.  ``-q`` sets verbosity to ``0`` unconditionally.  The
  default verbosity level is ``1``.

- The ``alchemy`` scaffold tests now provide better coverage.  See
  https://github.com/Pylons/pyramid/pull/1029

- The ``pyramid.config.Configurator.add_route`` method now supports being
  called with an external URL as pattern. See
  https://github.com/Pylons/pyramid/issues/611 and the documentation section
  in the "URL Dispatch" chapter entitled "External Routes" for more information.

Bug Fixes
---------

- It was not possible to use ``pyramid.httpexceptions.HTTPException`` as
  the ``context`` of an exception view as very general catchall for
  http-related exceptions when you wanted that exception view to override the
  default exception view.  See https://github.com/Pylons/pyramid/issues/985

- When the ``pyramid.reload_templates`` setting was true, and a Chameleon
  template was reloaded, and the renderer specification named a macro
  (e.g. ``foo#macroname.pt``), renderings of the template after the template
  was reloaded due to a file change would produce the entire template body
  instead of just a rendering of the macro.  See
  https://github.com/Pylons/pyramid/issues/1013.

- Fix an obscure problem when combining a virtual root with a route with a
  ``*traverse`` in its pattern.  Now the traversal path generated in
  such a configuration will be correct, instead of an element missing
  a leading slash.

- Fixed a Mako renderer bug returning a tuple with a previous defname value
  in some circumstances. See https://github.com/Pylons/pyramid/issues/1037
  for more information.

- Make the ``pyramid.config.assets.PackageOverrides`` object implement the API
  for ``__loader__`` objects specified in PEP 302.  Proxies to the
  ``__loader__`` set by the importer, if present; otherwise, raises
  ``NotImplementedError``.  This makes Pyramid static view overrides work
  properly under Python 3.3 (previously they would not).  See
  https://github.com/Pylons/pyramid/pull/1015 for more information.

- ``mako_templating``: added defensive workaround for non-importability of
  ``mako`` due to upstream ``markupsafe`` dropping Python 3.2 support.  Mako
  templating will no longer work under the combination of MarkupSafe 0.17 and
  Python 3.2 (although the combination of MarkupSafe 0.17 and Python 3.3 or any
  supported Python 2 version will work OK).

- Spaces and dots may now be in mako renderer template paths. This was
  broken when support for the new makodef syntax was added in 1.4a1.
  See https://github.com/Pylons/pyramid/issues/950

- ``pyramid.debug_authorization=true`` will now correctly print out
  ``Allowed`` for views registered with ``NO_PERMISSION_REQUIRED`` instead
  of invoking the ``permits`` method of the authorization policy.
  See https://github.com/Pylons/pyramid/issues/954

- Pyramid failed to install on some systems due to being packaged with
  some test files containing higher order characters in their names. These
  files have now been removed. See
  https://github.com/Pylons/pyramid/issues/981

- ``pyramid.testing.DummyResource`` didn't define ``__bool__``, so code under
  Python 3 would use ``__len__`` to find truthiness; this usually caused an
  instance of DummyResource to be "falsy" instead of "truthy".  See
  https://github.com/Pylons/pyramid/pull/1032

- The ``alchemy`` scaffold would break when the database was MySQL during
  tables creation.  See https://github.com/Pylons/pyramid/pull/1049

- The ``current_route_url`` method now attaches the query string to the URL by
  default. See
  https://github.com/Pylons/pyramid/issues/1040

- Make ``pserve.cherrypy_server_runner`` Python 3 compatible. See
  https://github.com/Pylons/pyramid/issues/718

Backwards Incompatibilities
---------------------------

- Modified the ``current_route_url`` method in pyramid.Request. The method
  previously returned the URL without the query string by default, it now does
  attach the query string unless it is overriden.

- The ``route_url`` and ``route_path`` APIs no longer quote ``/``
  to ``%2F`` when a replacement value contains a ``/``.  This was pointless,
  as WSGI servers always unquote the slash anyway, and Pyramid never sees the
  quoted value.

- It is no longer possible to set a ``locale_name`` attribute of the request,
  nor is it possible to set a ``localizer`` attribute of the request.  These
  are now "reified" properties that look up a locale name and localizer
  respectively using the machinery described in the "Internationalization"
  chapter of the documentation.

- If you send an ``X-Vhm-Root`` header with a value that ends with a slash (or
  any number of slashes), the trailing slash(es) will be removed before a URL
  is generated when you use use ``request.resource_url`` or
  ``request.resource_path``.  Previously the virtual root path would not have
  trailing slashes stripped, which would influence URL generation.

- The ``pyramid.interfaces.IResourceURL`` interface has now grown two new
  attributes: ``virtual_path_tuple`` and ``physical_path_tuple``.  These should
  be the tuple form of the resource's path (physical and virtual).

1.4 (2012-12-18)
================

Docs
----

- Fix functional tests in the ZODB tutorial

1.4b3 (2012-12-10)
==================

- Packaging release only, no code changes.  1.4b2 was a brownbag release due to
  missing directories in the tarball.

1.4b2 (2012-12-10)
==================

Docs
----

- Scaffolding is now PEP-8 compliant (at least for a brief shining moment).

- Tutorial improvements.

Backwards Incompatibilities
---------------------------

- Modified the ``_depth`` argument to ``pyramid.view.view_config`` to accept
  a value relative to the invocation of ``view_config`` itself. Thus, when it
  was previously expecting a value of ``1`` or greater, to reflect that
  the caller of ``view_config`` is 1 stack frame away from ``venusian.attach``,
  this implementation detail is now hidden.

- Modified the ``_backframes`` argument to ``pyramid.util.action_method`` in a
  similar way to the changes described to ``_depth`` above.  This argument
  remains undocumented, but might be used in the wild by some insane person.

1.4b1 (2012-11-21)
==================

Features
--------

- Small microspeed enhancement which anticipates that a
  ``pyramid.response.Response`` object is likely to be returned from a view.
  Some code is shortcut if the class of the object returned by a view is this
  class.  A similar microoptimization was done to
  ``pyramid.request.Request.is_response``.

- Make it possible to use variable arguments on ``p*`` commands (``pserve``,
  ``pshell``, ``pviews``, etc) in the form ``a=1 b=2`` so you can fill in
  values in parameterized ``.ini`` file, e.g. ``pshell etc/development.ini
  http_port=8080``.  See https://github.com/Pylons/pyramid/pull/714

- A somewhat advanced and obscure feature of Pyramid event handlers is their
  ability to handle "multi-interface" notifications.  These notifications have
  traditionally presented multiple objects to the subscriber callable.  For
  instance, if an event was sent by code like this::

     registry.notify(event, context)

  In the past, in order to catch such an event, you were obligated to write and
  register an event subscriber that mentioned both the event and the context in
  its argument list::

     @subscriber([SomeEvent, SomeContextType])
     def asubscriber(event, context):
         pass

  In many subscriber callables registered this way, it was common for the logic
  in the subscriber callable to completely ignore the second and following
  arguments (e.g. ``context`` in the above example might be ignored), because
  they usually existed as attributes of the event anyway.  You could usually
  get the same value by doing ``event.context`` or similar.

  The fact that you needed to put an extra argument which you usually ignored
  in the subscriber callable body was only a minor annoyance until we added
  "subscriber predicates", used to narrow the set of circumstances under which
  a subscriber will be executed, in a prior 1.4 alpha release.  Once those were
  added, the annoyance was escalated, because subscriber predicates needed to
  accept the same argument list and arity as the subscriber callables that they
  were configured against.  So, for example, if you had these two subscriber
  registrations in your code::

     @subscriber([SomeEvent, SomeContextType])
     def asubscriber(event, context):
         pass

     @subscriber(SomeOtherEvent)
     def asubscriber(event):
         pass

  And you wanted to use a subscriber predicate::

     @subscriber([SomeEvent, SomeContextType], mypredicate=True)
     def asubscriber1(event, context):
         pass

     @subscriber(SomeOtherEvent, mypredicate=True)
     def asubscriber2(event):
         pass

  If an existing ``mypredicate`` subscriber predicate had been written in such
  a way that it accepted only one argument in its ``__call__``, you could not
  use it against a subscription which named more than one interface in its
  subscriber interface list.  Similarly, if you had written a subscriber
  predicate that accepted two arguments, you couldn't use it against a
  registration that named only a single interface type.

  For example, if you created this predicate::

    class MyPredicate(object):
        # portions elided...
        def __call__(self, event):
            return self.val == event.context.foo

  It would not work against a multi-interface-registered subscription, so in
  the above example, when you attempted to use it against ``asubscriber1``, it
  would fail at runtime with a TypeError, claiming something was attempting to
  call it with too many arguments.

  To hack around this limitation, you were obligated to design the
  ``mypredicate`` predicate to expect to receive in its ``__call__`` either a
  single ``event`` argument (a SomeOtherEvent object) *or* a pair of arguments
  (a SomeEvent object and a SomeContextType object), presumably by doing
  something like this::

    class MyPredicate(object):
        # portions elided...
        def __call__(self, event, context=None):
            return self.val == event.context.foo

  This was confusing and bad.

  In order to allow people to ignore unused arguments to subscriber callables
  and to normalize the relationship between event subscribers and subscriber
  predicates, we now allow both subscribers and subscriber predicates to accept
  only a single ``event`` argument even if they've been subscribed for
  notifications that involve multiple interfaces.  Subscribers and subscriber
  predicates that accept only one argument will receive the first object passed
  to ``notify``; this is typically (but not always) the event object.  The
  other objects involved in the subscription lookup will be discarded.  You can
  now write an event subscriber that accepts only ``event`` even if it
  subscribes to multiple interfaces::

     @subscriber([SomeEvent, SomeContextType])
     def asubscriber(event):
         # this will work!

  This prevents you from needing to match the subscriber callable parameters to
  the subscription type unnecessarily, especially when you don't make use of
  any argument in your subscribers except for the event object itself.

  Note, however, that if the event object is not the first
  object in the call to ``notify``, you'll run into trouble.  For example, if
  notify is called with the context argument first::

     registry.notify(context, event)

  You won't be able to take advantage of the event-only feature.  It will
  "work", but the object received by your event handler won't be the event
  object, it will be the context object, which won't be very useful::

     @subscriber([SomeContextType, SomeEvent])
     def asubscriber(event):
         # bzzt! you'll be getting the context here as ``event``, and it'll
         # be useless

  Existing multiple-argument subscribers continue to work without issue, so you
  should continue use those if your system notifies using multiple interfaces
  and the first interface is not the event interface.  For example::

     @subscriber([SomeContextType, SomeEvent])
     def asubscriber(context, event):
         # this will still work!

  The event-only feature makes it possible to use a subscriber predicate that
  accepts only a request argument within both multiple-interface subscriber
  registrations and single-interface subscriber registrations.  You needn't
  make slightly different variations of predicates depending on the
  subscription type arguments.  Instead, just write all your subscriber
  predicates so they only accept ``event`` in their ``__call__`` and they'll be
  useful across all registrations for subscriptions that use an event as their
  first argument, even ones which accept more than just ``event``.

  However, the same caveat applies to predicates as to subscriber callables: if
  you're subscribing to a multi-interface event, and the first interface is not
  the event interface, the predicate won't work properly.  In such a case,
  you'll need to match the predicate ``__call__`` argument ordering and
  composition to the ordering of the interfaces.  For example, if the
  registration for the subscription uses ``[SomeContext, SomeEvent]``, you'll
  need to reflect that in the ordering of the parameters of the predicate's
  ``__call__`` method::

        def __call__(self, context, event):
            return event.request.path.startswith(self.val)

  tl;dr: 1) When using multi-interface subscriptions, always use the event type
  as the first subscription registration argument and 2) When 1 is true, use
  only ``event`` in your subscriber and subscriber predicate parameter lists,
  no matter how many interfaces the subscriber is notified with.  This
  combination will result in the maximum amount of reusability of subscriber
  predicates and the least amount of thought on your part.  Drink responsibly.

Bug Fixes
---------

- A failure when trying to locate the attribute ``__text__`` on route and view
  predicates existed when the ``debug_routematch`` setting was true or when the
  ``pviews`` command was used. See https://github.com/Pylons/pyramid/pull/727

Documentation
-------------

- Sync up tutorial source files with the files that are rendered by the
  scaffold that each uses.

1.4a4 (2012-11-14)
==================

Features
--------

- ``pyramid.authentication.AuthTktAuthenticationPolicy`` has been updated to
  support newer hashing algorithms such as ``sha512``. Existing applications
  should consider updating if possible for improved security over the default
  md5 hashing.

- Added an ``effective_principals`` route and view predicate.

- Do not allow the userid returned from the ``authenticated_userid`` or the
  userid that is one of the list of principals returned by
  ``effective_principals`` to be either of the strings ``system.Everyone`` or
  ``system.Authenticated`` when any of the built-in authorization policies that
  live in ``pyramid.authentication`` are in use.  These two strings are
  reserved for internal usage by Pyramid and they will not be accepted as valid
  userids.

- Slightly better debug logging from
  ``pyramid.authentication.RepozeWho1AuthenticationPolicy``.

- ``pyramid.security.view_execution_permitted`` used to return ``True`` if no
  view could be found. It now raises a ``TypeError`` exception in that case, as
  it doesn't make sense to assert that a nonexistent view is
  execution-permitted. See https://github.com/Pylons/pyramid/issues/299.

- Allow a ``_depth`` argument to ``pyramid.view.view_config``, which will
  permit limited composition reuse of the decorator by other software that
  wants to provide custom decorators that are much like view_config.

- Allow an iterable of decorators to be passed to
  ``pyramid.config.Configurator.add_view``. This allows views to be wrapped
  by more than one decorator without requiring combining the decorators
  yourself.

Bug Fixes
---------

- In the past if a renderer returned ``None``, the body of the resulting
  response would be set explicitly to the empty string.  Instead, now, the body
  is left unchanged, which allows the renderer to set a body itself by using
  e.g. ``request.response.body = b'foo'``.  The body set by the renderer will
  be unmolested on the way out.  See
  https://github.com/Pylons/pyramid/issues/709

- In uncommon cases, the ``pyramid_excview_tween_factory`` might have
  inadvertently raised a ``KeyError`` looking for ``request_iface`` as an
  attribute of the request.  It no longer fails in this case.  See
  https://github.com/Pylons/pyramid/issues/700

- Be more tolerant of potential error conditions in ``match_param`` and
  ``physical_path`` predicate implementations; instead of raising an exception,
  return False.

- ``pyramid.view.render_view`` was not functioning properly under Python 3.x
  due to a byte/unicode discrepancy. See
  https://github.com/Pylons/pyramid/issues/721

Deprecations
------------

- ``pyramid.authentication.AuthTktAuthenticationPolicy`` will emit a warning if
  an application is using the policy without explicitly passing a ``hashalg``
  argument. This is because the default is "md5" which is considered
  theoretically subject to collision attacks. If you really want "md5" then you
  must specify it explicitly to get rid of the warning.

Documentation
-------------

- All of the tutorials that use
  ``pyramid.authentication.AuthTktAuthenticationPolicy`` now explicitly pass
  ``sha512`` as a ``hashalg`` argument.


Internals
---------

- Move ``TopologicalSorter`` from ``pyramid.config.util`` to ``pyramid.util``,
  move ``CyclicDependencyError`` from ``pyramid.config.util`` to
  ``pyramid.exceptions``, rename ``Singleton`` to ``Sentinel`` and move from
  ``pyramid.config.util`` to ``pyramid.util``; this is in an effort to
  move that stuff that may be an API one day out of ``pyramid.config.util``,
  because that package should never be imported from non-Pyramid code.
  TopologicalSorter is still not an API, but may become one.

- Get rid of shady monkeypatching of ``pyramid.request.Request`` and
  ``pyramid.response.Response`` done within the ``__init__.py`` of Pyramid.
  Webob no longer relies on this being done.  Instead, the ResponseClass
  attribute of the Pyramid Request class is assigned to the Pyramid response
  class; that's enough to satisfy WebOb and behave as it did before with the
  monkeypatching.

1.4a3 (2012-10-26)
==================

Bug Fixes
---------

- The match_param predicate's text method was fixed to sort its values.
  Part of https://github.com/Pylons/pyramid/pull/705

- 1.4a ``pyramid.scripting.prepare`` behaved differently than 1.3 series
  function of same name.  In particular, if passed a request, it would not
  set the ``registry`` attribute of the request like 1.3 did.  A symptom
  would be that passing a request to ``pyramid.paster.bootstrap`` (which uses
  the function) that did not have a ``registry`` attribute could assume that
  the registry would be attached to the request by Pyramid.  This assumption
  could be made in 1.3, but not in 1.4.  The assumption can now be made in
  1.4 too (a registry is attached to a request passed to bootstrap or
  prepare).

- When registering a view configuration that named a Chameleon ZPT renderer
  with a macro name in it (e.g. ``renderer='some/template#somemacro.pt``) as
  well as a view configuration without a macro name in it that pointed to the
  same template (e.g. ``renderer='some/template.pt'``), internal caching could
  confuse the two, and your code might have rendered one instead of the
  other.

Features
--------

- Allow multiple values to be specified to the ``request_param`` view/route
  predicate as a sequence.  Previously only a single string value was allowed.
  See https://github.com/Pylons/pyramid/pull/705

- Comments with references to documentation sections placed in scaffold
  ``.ini`` files.

- Added an HTTP Basic authentication policy
  at ``pyramid.authentication.BasicAuthAuthenticationPolicy``.

- The Configurator ``testing_securitypolicy`` method now returns the policy
  object it creates.

- The Configurator ``testing_securitypolicy`` method accepts two new
  arguments: ``remember_result`` and ``forget_result``.  If supplied, these
  values influence the result of the policy's ``remember`` and ``forget``
  methods, respectively.

- The DummySecurityPolicy created by ``testing_securitypolicy`` now sets a
  ``forgotten`` value on the policy (the value ``True``) when its ``forget``
  method is called.

- The DummySecurityPolicy created by ``testing_securitypolicy`` now sets a
  ``remembered`` value on the policy, which is the value of the ``principal``
  argument it's called with when its ``remember`` method is called.

- New ``physical_path`` view predicate.  If specified, this value should be a
  string or a tuple representing the physical traversal path of the context
  found via traversal for this predicate to match as true.  For example:
  ``physical_path='/'`` or ``physical_path='/a/b/c'`` or ``physical_path=('',
  'a', 'b', 'c')``.  This is not a path prefix match or a regex, it's a
  whole-path match.  It's useful when you want to always potentially show a
  view when some object is traversed to, but you can't be sure about what kind
  of object it will be, so you can't use the ``context`` predicate.  The
  individual path elements in between slash characters or in tuple elements
  should be the Unicode representation of the name of the resource and should
  not be encoded in any way.

1.4a2 (2012-09-27)
==================

Bug Fixes
---------

- When trying to determine Mako defnames and Chameleon macro names in asset
  specifications, take into account that the filename may have a hyphen in
  it.  See https://github.com/Pylons/pyramid/pull/692

Features
--------

- A new ``pyramid.session.check_csrf_token`` convenience function was added.

- A ``check_csrf`` view predicate was added.  For example, you can now do
  ``config.add_view(someview, check_csrf=True)``.  When the predicate is
  checked, if the ``csrf_token`` value in ``request.params`` matches the CSRF
  token in the request's session, the view will be permitted to execute.
  Otherwise, it will not be permitted to execute.

- Add ``Base.metadata.bind = engine`` to alchemy template, so that tables
  defined imperatively will work.

Documentation
-------------

- update wiki2 SQLA tutorial with the changes required after inserting
  ``Base.metadata.bind = engine`` into the alchemy scaffold.

1.4a1 (2012-09-16)
==================

Bug Fixes
---------

- Forward port from 1.3 branch: When no authentication policy was configured,
  a call to ``pyramid.security.effective_principals`` would unconditionally
  return the empty list.  This was incorrect, it should have unconditionally
  returned ``[Everyone]``, and now does.

- Explicit url dispatch regexes can now contain colons.
  https://github.com/Pylons/pyramid/issues/629

- On at least one 64-bit Ubuntu system under Python 3.2, using the
  ``view_config`` decorator caused a ``RuntimeError: dictionary changed size
  during iteration`` exception.  It no longer does.  See
  https://github.com/Pylons/pyramid/issues/635 for more information.

- In Mako Templates lookup, check if the uri is already adjusted and bring
  it back to an asset spec. Normally occurs with inherited templates or
  included components.
  https://github.com/Pylons/pyramid/issues/606
  https://github.com/Pylons/pyramid/issues/607

- In Mako Templates lookup, check for absolute uri (using mako directories)
  when mixing up inheritance with asset specs.
  https://github.com/Pylons/pyramid/issues/662

- HTTP Accept headers were not being normalized causing potentially
  conflicting view registrations to go unnoticed. Two views that only
  differ in the case ('text/html' vs. 'text/HTML') will now raise an error.
  https://github.com/Pylons/pyramid/pull/620

- Forward-port from 1.3 branch: when registering multiple views with an
  ``accept`` predicate in a Pyramid application running under Python 3, you
  might have received a ``TypeError: unorderable types: function() <
  function()`` exception.

Features
--------

- Python 3.3 compatibility.

- Configurator.add_directive now accepts arbitrary callables like partials or
  objects implementing ``__call__`` which dont have ``__name__`` and
  ``__doc__`` attributes.  See https://github.com/Pylons/pyramid/issues/621
  and https://github.com/Pylons/pyramid/pull/647.

- Third-party custom view, route, and subscriber predicates can now be added
  for use by view authors via
  ``pyramid.config.Configurator.add_view_predicate``,
  ``pyramid.config.Configurator.add_route_predicate`` and
  ``pyramid.config.Configurator.add_subscriber_predicate``.  So, for example,
  doing this::

     config.add_view_predicate('abc', my.package.ABCPredicate)

  Might allow a view author to do this in an application that configured that
  predicate::

     @view_config(abc=1)

  Similar features exist for ``add_route``, and ``add_subscriber``.  See
  "Adding A Third Party View, Route, or Subscriber Predicate" in the Hooks
  chapter for more information.

  Note that changes made to support the above feature now means that only
  actions registered using the same "order" can conflict with one another.
  It used to be the case that actions registered at different orders could
  potentially conflict, but to my knowledge nothing ever depended on this
  behavior (it was a bit silly).

- Custom objects can be made easily JSON-serializable in Pyramid by defining
  a ``__json__`` method on the object's class. This method should return
  values natively serializable by ``json.dumps`` (such as ints, lists,
  dictionaries, strings, and so forth).

- The JSON renderer now allows for the definition of custom type adapters to
  convert unknown objects to JSON serializations.

- As of this release, the ``request_method`` predicate, when used, will also
  imply that ``HEAD`` is implied when you use ``GET``.  For example, using
  ``@view_config(request_method='GET')`` is equivalent to using
  ``@view_config(request_method=('GET', 'HEAD'))``.  Using
  ``@view_config(request_method=('GET', 'POST')`` is equivalent to using
  ``@view_config(request_method=('GET', 'HEAD', 'POST')``.  This is because
  HEAD is a variant of GET that omits the body, and WebOb has special support
  to return an empty body when a HEAD is used.

- ``config.add_request_method`` has been introduced to support extending
  request objects with arbitrary callables. This method expands on the
  previous ``config.set_request_property`` by supporting methods as well as
  properties. This method now causes less code to be executed at
  request construction time than ``config.set_request_property`` in
  version 1.3.

- Don't add a ``?`` to URLs generated by ``request.resource_url`` if the
  ``query`` argument is provided but empty.

- Don't add a ``?`` to URLs generated by ``request.route_url`` if the
  ``_query`` argument is provided but empty.

- The static view machinery now raises (rather than returns) ``HTTPNotFound``
  and ``HTTPMovedPermanently`` exceptions, so these can be caught by the
  Not Found View (and other exception views).

- The Mako renderer now supports a def name in an asset spec.  When the def
  name is present in the asset spec, the system will render the template def
  within the template and will return the result. An example asset spec is
  ``package:path/to/template#defname.mako``. This will render the def named
  ``defname`` inside the ``template.mako`` template instead of rendering the
  entire template.  The old way of returning a tuple in the form
  ``('defname', {})`` from the view is supported for backward compatibility,

- The Chameleon ZPT renderer now accepts a macro name in an asset spec.  When
  the macro name is present in the asset spec, the system will render the
  macro listed as a ``define-macro`` and return the result instead of
  rendering the entire template.  An example asset spec:
  ``package:path/to/template#macroname.pt``.  This will render the macro
  defined as ``macroname`` within the ``template.pt`` template instead of the
  entire templae.

- When there is a predicate mismatch exception (seen when no view matches for
  a given request due to predicates not working), the exception now contains
  a textual description of the predicate which didn't match.

- An ``add_permission`` directive method was added to the Configurator.  This
  directive registers a free-standing permission introspectable into the
  Pyramid introspection system.  Frameworks built atop Pyramid can thus use
  the ``permissions`` introspectable category data to build a
  comprehensive list of permissions supported by a running system.  Before
  this method was added, permissions were already registered in this
  introspectable category as a side effect of naming them in an ``add_view``
  call, this method just makes it possible to arrange for a permission to be
  put into the ``permissions`` introspectable category without naming it
  along with an associated view.  Here's an example of usage of
  ``add_permission``::

      config = Configurator()
      config.add_permission('view')

- The ``UnencryptedCookieSessionFactoryConfig`` now accepts
  ``signed_serialize`` and ``signed_deserialize`` hooks which may be used
  to influence how the sessions are marshalled (by default this is done
  with HMAC+pickle).

- ``pyramid.testing.DummyRequest`` now supports methods supplied by the
  ``pyramid.util.InstancePropertyMixin`` class such as ``set_property``.

- Request properties and methods added via ``config.set_request_property`` or
  ``config.add_request_method`` are now available to tweens.

- Request properties and methods added via ``config.set_request_property`` or
  ``config.add_request_method`` are now available in the request object
  returned from ``pyramid.paster.bootstrap``.

- ``request.context`` of environment request during ``bootstrap`` is now the
  root object if a context isn't already set on a provided request.

- The ``pyramid.decorator.reify`` function is now an API, and was added to
  the API documentation.

- Added the ``pyramid.testing.testConfig`` context manager, which can be used
  to generate a configurator in a test, e.g. ``with testing.testConfig(...):``.

- Users can now invoke a subrequest from within view code using a new
  ``request.invoke_subrequest`` API.

Deprecations
------------

- The ``pyramid.config.Configurator.set_request_property`` has been
  documentation-deprecated.  The method remains usable but the more
  featureful ``pyramid.config.Configurator.add_request_method`` should be
  used in its place (it has all of the same capabilities but can also extend
  the request object with methods).

Backwards Incompatibilities
---------------------------

- The Pyramid router no longer adds the values ``bfg.routes.route`` or
  ``bfg.routes.matchdict`` to the request's WSGI environment dictionary.
  These values were docs-deprecated in ``repoze.bfg`` 1.0 (effectively seven
  minor releases ago).  If your code depended on these values, use
  request.matched_route and request.matchdict instead.

- It is no longer possible to pass an environ dictionary directly to
  ``pyramid.traversal.ResourceTreeTraverser.__call__`` (aka
  ``ModelGraphTraverser.__call__``).  Instead, you must pass a request
  object.  Passing an environment instead of a request has generated a
  deprecation warning since Pyramid 1.1.

- Pyramid will no longer work properly if you use the
  ``webob.request.LegacyRequest`` as a request factory.  Instances of the
  LegacyRequest class have a ``request.path_info`` which return a string.
  This Pyramid release assumes that ``request.path_info`` will
  unconditionally be Unicode.

- The functions from ``pyramid.chameleon_zpt`` and ``pyramid.chameleon_text``
  named ``get_renderer``, ``get_template``, ``render_template``, and
  ``render_template_to_response`` have been removed.  These have issued a
  deprecation warning upon import since Pyramid 1.0.  Use
  ``pyramid.renderers.get_renderer()``,
  ``pyramid.renderers.get_renderer().implementation()``,
  ``pyramid.renderers.render()`` or ``pyramid.renderers.render_to_response``
  respectively instead of these functions.

- The ``pyramid.configuration`` module was removed.  It had been deprecated
  since Pyramid 1.0 and printed a deprecation warning upon its use.  Use
  ``pyramid.config`` instead.

- The ``pyramid.paster.PyramidTemplate`` API was removed.  It had been
  deprecated since Pyramid 1.1 and issued a warning on import.  If your code
  depended on this, adjust your code to import
  ``pyramid.scaffolds.PyramidTemplate`` instead.

- The ``pyramid.settings.get_settings()`` API was removed.  It had been
  printing a deprecation warning since Pyramid 1.0.  If your code depended on
  this API, use ``pyramid.threadlocal.get_current_registry().settings``
  instead or use the ``settings`` attribute of the registry available from
  the request (``request.registry.settings``).

- These APIs from the ``pyramid.testing`` module were removed.  They have
  been printing deprecation warnings since Pyramid 1.0:

  * ``registerDummySecurityPolicy``, use
    ``pyramid.config.Configurator.testing_securitypolicy`` instead.

  * ``registerResources`` (aka ``registerModels``, use
    ``pyramid.config.Configurator.testing_resources`` instead.

  * ``registerEventListener``, use
    ``pyramid.config.Configurator.testing_add_subscriber`` instead.

  * ``registerTemplateRenderer`` (aka `registerDummyRenderer``), use
    ``pyramid.config.Configurator.testing_add_template`` instead.

  * ``registerView``, use ``pyramid.config.Configurator.add_view`` instead.

  * ``registerUtility``, use
    ``pyramid.config.Configurator.registry.registerUtility`` instead.

  * ``registerAdapter``, use
    ``pyramid.config.Configurator.registry.registerAdapter`` instead.

  * ``registerSubscriber``, use
    ``pyramid.config.Configurator.add_subscriber`` instead.

  * ``registerRoute``, use
    ``pyramid.config.Configurator.add_route`` instead.

  * ``registerSettings``, use
    ``pyramid.config.Configurator.add_settings`` instead.

- In Pyramid 1.3 and previous, the ``__call__`` method of a Response object
  was invoked before any finished callbacks were executed.  As of this
  release, the ``__call__`` method of a Response object is invoked *after*
  finished callbacks are executed.  This is in support of the
  ``request.invoke_subrequest`` feature.

- The 200-series exception responses named ``HTTPCreated``, ``HTTPAccepted``, 
  ``HTTPNonAuthoritativeInformation``, ``HTTPNoContent``, ``HTTPResetContent``,
  and ``HTTPPartialContent`` in ``pyramid.httpexceptions`` no longer inherit
  from ``HTTPOk``.  Instead they inherit from a new base class named 
  ``HTTPSuccessful``.  This will have no effect on you unless you've registered
  an exception view for ``HTTPOk`` and expect that exception view to
  catch all the aforementioned exceptions.

Documentation
-------------

- Added an "Upgrading Pyramid" chapter to the narrative documentation.  It
  describes how to cope with deprecations and removals of Pyramid APIs and
  how to show Pyramid-generated deprecation warnings while running tests and
  while running a server.

- Added a "Invoking a Subrequest" chapter to the documentation.  It describes
  how to use the new ``request.invoke_subrequest`` API.

Dependencies
------------

- Pyramid now requires WebOb 1.2b3+ (the prior Pyramid release only relied on
  1.2dev+).  This is to ensure that we obtain a version of WebOb that returns
  ``request.path_info`` as text.

1.3 (2012-03-21)
================

Bug Fixes
---------

- When ``pyramid.wsgi.wsgiapp2`` calls the downstream WSGI app, the app's
  environ will no longer have (deprecated and potentially misleading)
  ``bfg.routes.matchdict`` or ``bfg.routes.route`` keys in it.  A symptom of
  this bug would be a ``wsgiapp2``-wrapped Pyramid app finding the wrong view
  because it mistakenly detects that a route was matched when, in fact, it
  was not.

- The fix for issue https://github.com/Pylons/pyramid/issues/461 (which made
  it possible for instance methods to be used as view callables) introduced a
  backwards incompatibility when methods that declared only a request
  argument were used.  See https://github.com/Pylons/pyramid/issues/503

1.3b3 (2012-03-17)
==================

Bug Fixes
---------

- ``config.add_view(<aninstancemethod>)`` raised AttributeError involving
  ``__text__``.  See https://github.com/Pylons/pyramid/issues/461

- Remove references to do-nothing ``pyramid.debug_templates`` setting in all
  Pyramid-provided ``.ini`` files.  This setting previously told Chameleon to
  render better exceptions; now Chameleon always renders nice exceptions
  regardless of the value of this setting.

Scaffolds
---------

- The ``alchemy`` scaffold now shows an informative error message in the
  browser if the person creating the project forgets to run the
  initialization script.

- The ``alchemy`` scaffold initialization script is now called
  ``initialize_<projectname>_db`` instead of ``populate_<projectname>``.

Documentation
-------------

- Wiki tutorials improved due to collaboration at PyCon US 2012 sprints.

1.3b2 (2012-03-02)
==================

Bug Fixes
---------

- The method ``pyramid.request.Request.partial_application_url`` is no longer
  in the API docs.  It was meant to be a private method; its publication in
  the documentation as an API method was a mistake, and it has been renamed
  to something private.

- When a static view was registered using an absolute filesystem path on
  Windows, the ``request.static_url`` function did not work to generate URLs
  to its resources.  Symptom: "No static URL definition matching
  c:\\foo\\bar\\baz".

- Make all tests pass on Windows XP.

- Bug in ACL authentication checking on Python 3: the ``permits`` and
  ``principals_allowed_by_permission`` method of
  ``pyramid.authorization.ACLAuthenticationPolicy`` could return an
  inappropriate ``True`` value when a permission on an ACL was a string
  rather than a sequence, and then only if the ACL permission string was a
  substring of the ``permission`` value passed to the function.

  This bug effects no Pyramid deployment under Python 2; it is a bug that
  exists only in deployments running on Python 3.  It has existed since
  Pyramid 1.3a1.

  This bug was due to the presence of an ``__iter__`` attribute on strings
  under Python 3 which is not present under strings in Python 2.

1.3b1 (2012-02-26)
==================

Bug Fixes
---------

- ``pyramid.config.Configurator.with_package`` didn't work if the
  Configurator was an old-style ``pyramid.configuration.Configurator``
  instance.

- Pyramid authorization policies did not show up in the introspector.

Deprecations
------------

- All references to the ``tmpl_context`` request variable were removed from
  the docs.  Its existence in Pyramid is confusing for people who were never
  Pylons users.  It was added as a porting convenience for Pylons users in
  Pyramid 1.0, but it never caught on because the Pyramid rendering system is
  a lot different than Pylons' was, and alternate ways exist to do what it
  was designed to offer in Pylons.  It will continue to exist "forever" but
  it will not be recommended or mentioned in the docs.

1.3a9 (2012-02-22)
==================

Features
--------

- Add an ``introspection`` boolean to the Configurator constructor.  If this
  is ``True``, actions registered using the Configurator will be registered
  with the introspector.  If it is ``False``, they won't.  The default is
  ``True``.  Setting it to ``False`` during action processing will prevent
  introspection for any following registration statements, and setting it to
  ``True`` will start them up again.  This addition is to service a
  requirement that the debug toolbar's own views and methods not show up in
  the introspector.

- New API: ``pyramid.config.Configurator.add_notfound_view``.  This is a
  wrapper for ``pyramid.Config.configurator.add_view`` which provides easy
  append_slash support and does the right thing about permissions.  It should
  be preferred over calling ``add_view`` directly with
  ``context=HTTPNotFound`` as was previously recommended.

- New API: ``pyramid.view.notfound_view_config``.  This is a decorator
  constructor like ``pyramid.view.view_config`` that calls
  ``pyramid.config.Configurator.add_notfound_view`` when scanned.  It should
  be preferred over using ``pyramid.view.view_config`` with
  ``context=HTTPNotFound`` as was previously recommended.

- New API: ``pyramid.config.Configurator.add_forbidden_view``.  This is a
  wrapper for ``pyramid.Config.configurator.add_view`` which does the right
  thing about permissions.  It should be preferred over calling ``add_view``
  directly with ``context=HTTPForbidden`` as was previously recommended.

- New API: ``pyramid.view.forbidden_view_config``.  This is a decorator
  constructor like ``pyramid.view.view_config`` that calls
  ``pyramid.config.Configurator.add_forbidden_view`` when scanned.  It should
  be preferred over using ``pyramid.view.view_config`` with
  ``context=HTTPForbidden`` as was previously recommended.

- New APIs: ``pyramid.response.FileResponse`` and
  ``pyramid.response.FileIter``, for usage in views that must serve files
  "manually".

Backwards Incompatibilities
---------------------------

- Remove ``pyramid.config.Configurator.with_context`` class method.  It was
  never an API, it is only used by ``pyramid_zcml`` and its functionality has
  been moved to that package's latest release.  This means that you'll need
  to use the 0.9.2 or later release of ``pyramid_zcml`` with this release of
  Pyramid.

- The ``introspector`` argument to the ``pyramid.config.Configurator``
  constructor API has been removed.  It has been replaced by the boolean
  ``introspection`` flag.

- The ``pyramid.registry.noop_introspector`` API object has been removed.

- The older deprecated ``set_notfound_view`` Configurator method is now an
  alias for the new ``add_notfound_view`` Configurator method.  Likewise, the
  older deprecated ``set_forbidden_view`` is now an alias for the new
  ``add_forbidden_view``. This has the following impact: the ``context`` sent
  to views with a ``(context, request)`` call signature registered via the
  ``set_notfound_view`` or ``set_forbidden_view`` will now be an exception
  object instead of the actual resource context found.  Use
  ``request.context`` to get the actual resource context.  It's also
  recommended to disuse ``set_notfound_view`` in favor of
  ``add_notfound_view``, and disuse ``set_forbidden_view`` in favor of
  ``add_forbidden_view`` despite the aliasing.

Deprecations
------------

- The API documentation for ``pyramid.view.append_slash_notfound_view`` and
  ``pyramid.view.AppendSlashNotFoundViewFactory`` was removed.  These names
  still exist and are still importable, but they are no longer APIs.  Use
  ``pyramid.config.Configurator.add_notfound_view(append_slash=True)`` or
  ``pyramid.view.notfound_view_config(append_slash=True)`` to get the same
  behavior.

- The ``set_forbidden_view`` and ``set_notfound_view`` methods of the
  Configurator were removed from the documentation.  They have been
  deprecated since Pyramid 1.1.

Bug Fixes
---------

- The static file response object used by ``config.add_static_view`` opened
  the static file twice, when it only needed to open it once.

- The AppendSlashNotFoundViewFactory used request.path to match routes.  This
  was wrong because request.path contains the script name, and this would
  cause it to fail in circumstances where the script name was not empty.  It
  should have used request.path_info, and now does.

Documentation
-------------

- Updated the "Creating a Not Found View" section of the "Hooks" chapter,
  replacing explanations of registering a view using ``add_view`` or
  ``view_config`` with ones using ``add_notfound_view`` or
  ``notfound_view_config``.

- Updated the "Creating a Not Forbidden View" section of the "Hooks" chapter,
  replacing explanations of registering a view using ``add_view`` or
  ``view_config`` with ones using ``add_forbidden_view`` or
  ``forbidden_view_config``.

- Updated the "Redirecting to Slash-Appended Routes" section of the "URL
  Dispatch" chapter, replacing explanations of registering a view using
  ``add_view`` or ``view_config`` with ones using ``add_notfound_view`` or
  ``notfound_view_config``

- Updated all tutorials to use ``pyramid.view.forbidden_view_config`` rather
  than ``pyramid.view.view_config`` with an HTTPForbidden context.

1.3a8 (2012-02-19)
==================

Features
--------

- The ``scan`` method of a ``Configurator`` can be passed an ``ignore``
  argument, which can be a string, a callable, or a list consisting of
  strings and/or callables.  This feature allows submodules, subpackages, and
  global objects from being scanned.  See
  http://readthedocs.org/docs/venusian/en/latest/#ignore-scan-argument for
  more information about how to use the ``ignore`` argument to ``scan``.

- Better error messages when a view callable returns a value that cannot be
  converted to a response (for example, when a view callable returns a
  dictionary without a renderer defined, or doesn't return any value at all).
  The error message now contains information about the view callable itself
  as well as the result of calling it.

- Better error message when a .pyc-only module is ``config.include`` -ed.
  This is not permitted due to error reporting requirements, and a better
  error message is shown when it is attempted.  Previously it would fail with
  something like "AttributeError: 'NoneType' object has no attribute
  'rfind'".

- Add ``pyramid.config.Configurator.add_traverser`` API method.  See the
  Hooks narrative documentation section entitled "Changing the Traverser" for
  more information.  This is not a new feature, it just provides an API for
  adding a traverser without needing to use the ZCA API.

- Add ``pyramid.config.Configurator.add_resource_url_adapter`` API method.
  See the Hooks narrative documentation section entitled "Changing How
  pyramid.request.Request.resource_url Generates a URL" for more information.
  This is not a new feature, it just provides an API for adding a resource
  url adapter without needing to use the ZCA API.

- The system value ``req`` is now supplied to renderers as an alias for
  ``request``.  This means that you can now, for example, in a template, do
  ``req.route_url(...)`` instead of ``request.route_url(...)``.  This is
  purely a change to reduce the amount of typing required to use request
  methods and attributes from within templates.  The value ``request`` is
  still available too, this is just an alternative.

- A new interface was added: ``pyramid.interfaces.IResourceURL``.  An adapter
  implementing its interface can be used to override resource URL generation
  when ``request.resource_url`` is called.  This interface replaces the
  now-deprecated ``pyramid.interfaces.IContextURL`` interface.

- The dictionary passed to a resource's ``__resource_url__`` method (see
  "Overriding Resource URL Generation" in the "Resources" chapter) now
  contains an ``app_url`` key, representing the application URL generated
  during ``request.resource_url``.  It represents a potentially customized
  URL prefix, containing potentially custom scheme, host and port information
  passed by the user to ``request.resource_url``.  It should be used instead
  of ``request.application_url`` where necessary.

- The ``request.resource_url`` API now accepts these arguments: ``app_url``,
  ``scheme``, ``host``, and ``port``.  The app_url argument can be used to
  replace the URL prefix wholesale during url generation.  The ``scheme``,
  ``host``, and ``port`` arguments can be used to replace the respective
  default values of ``request.application_url`` partially.

- A new API named ``request.resource_path`` now exists.  It works like
  ``request.resource_url`` but produces a relative URL rather than an
  absolute one.

- The ``request.route_url`` API now accepts these arguments: ``_app_url``,
  ``_scheme``, ``_host``, and ``_port``.  The ``_app_url`` argument can be
  used to replace the URL prefix wholesale during url generation.  The
  ``_scheme``, ``_host``, and ``_port`` arguments can be used to replace the
  respective default values of ``request.application_url`` partially.

Backwards Incompatibilities
---------------------------

- The ``pyramid.interfaces.IContextURL`` interface has been deprecated.
  People have been instructed to use this to register a resource url adapter
  in the "Hooks" chapter to use to influence ``request.resource_url`` URL
  generation for resources found via custom traversers since Pyramid 1.0.

  The interface still exists and registering such an adapter still works, but
  this interface will be removed from the software after a few major Pyramid
  releases.  You should replace it with an equivalent
  ``pyramid.interfaces.IResourceURL`` adapter, registered using the new
  ``pyramid.config.Configurator.add_resource_url_adapter`` API.  A
  deprecation warning is now emitted when a
  ``pyramid.interfaces.IContextURL`` adapter is found when
  ``request.resource_url`` is called.

Documentation
-------------

- Don't create a ``session`` instance in SQLA Wiki tutorial, use raw
  ``DBSession`` instead (this is more common in real SQLA apps).

Scaffolding
-----------

- Put ``pyramid.includes`` targets within ini files in scaffolds on separate
  lines in order to be able to tell people to comment out only the
  ``pyramid_debugtoolbar`` line when they want to disable the toolbar.

Dependencies
------------

- Depend on ``venusian`` >= 1.0a3 to provide scan ``ignore`` support.

Internal
--------

- Create a "MakoRendererFactoryHelper" that provides customizable settings
  key prefixes.  Allows settings prefixes other than "mako." to be used to
  create different factories that don't use the global mako settings.  This
  will be useful for the debug toolbar, which can currently be sabotaged by
  someone using custom mako configuration settings.

1.3a7 (2012-02-07)
==================

Features
--------

- More informative error message when a ``config.include`` cannot find an
  ``includeme``.  See https://github.com/Pylons/pyramid/pull/392.

- Internal: catch unhashable discriminators early (raise an error instead of
  allowing them to find their way into resolveConflicts).

- The `match_param` view predicate now accepts a string or a tuple.
  This replaces the broken behavior of accepting a dict. See
  https://github.com/Pylons/pyramid/issues/425 for more information.

Bug Fixes
---------

- The process will now restart when ``pserve`` is used with the ``--reload``
  flag when the ``development.ini`` file (or any other .ini file in use) is
  changed.  See https://github.com/Pylons/pyramid/issues/377 and
  https://github.com/Pylons/pyramid/pull/411

- The ``prequest`` script would fail when used against URLs which did not
  return HTML or text.  See https://github.com/Pylons/pyramid/issues/381

Backwards Incompatibilities
---------------------------

- The `match_param` view predicate no longer accepts a dict. This will
  have no negative affect because the implementation was broken for
  dict-based arguments.

Documentation
-------------

- Add a traversal hello world example to the narrative docs.

1.3a6 (2012-01-20)
==================

Features
--------

- New API: ``pyramid.config.Configurator.set_request_property``. Add lazy
  property descriptors to a request without changing the request factory.
  This method provides conflict detection and is the suggested way to add
  properties to a request.

- Responses generated by Pyramid's ``static_view`` now use
  a ``wsgi.file_wrapper`` (see
  http://www.python.org/dev/peps/pep-0333/#optional-platform-specific-file-handling)
  when one is provided by the web server.

Bug Fixes
---------

- Views registered with an ``accept`` could not be overridden correctly with
  a different view that had the same predicate arguments.  See
  https://github.com/Pylons/pyramid/pull/404 for more information.

- When using a dotted name for a ``view`` argument to
  ``Configurator.add_view`` that pointed to a class with a ``view_defaults``
  decorator, the view defaults would not be applied.  See
  https://github.com/Pylons/pyramid/issues/396 .

- Static URL paths were URL-quoted twice.  See
  https://github.com/Pylons/pyramid/issues/407 .

1.3a5 (2012-01-09)
==================

Bug Fixes
---------

- The ``pyramid.view.view_defaults`` decorator did not work properly when
  more than one view relied on the defaults being different for configuration
  conflict resolution.  See https://github.com/Pylons/pyramid/issues/394.

Backwards Incompatibilities
---------------------------

- The ``path_info`` route and view predicates now match against
  ``request.upath_info`` (Unicode) rather than ``request.path_info``
  (indeterminate value based on Python 3 vs. Python 2).  This has to be done
  to normalize matching on Python 2 and Python 3.

1.3a4 (2012-01-05)
==================

Features
--------

- New API: ``pyramid.request.Request.set_property``. Add lazy property
  descriptors to a request without changing the request factory. New
  properties may be reified, effectively caching the value for the lifetime
  of the instance. Common use-cases for this would be to get a database
  connection for the request or identify the current user.

- Use the ``waitress`` WSGI server instead of ``wsgiref`` in scaffolding.

Bug Fixes
---------

- The documentation of ``pyramid.events.subscriber`` indicated that using it
  as a decorator with no arguments like this::

    @subscriber()
    def somefunc(event):
        pass

  Would register ``somefunc`` to receive all events sent via the registry,
  but this was untrue.  Instead, it would receive no events at all.  This has
  now been fixed and the code matches the documentation.  See also
  https://github.com/Pylons/pyramid/issues/386

- Literal portions of route patterns were not URL-quoted when ``route_url``
  or ``route_path`` was used to generate a URL or path.

- The result of ``route_path`` or ``route_url`` might have been ``unicode``
  or ``str`` depending on the input.  It is now guaranteed to always be
  ``str``.

- URL matching when the pattern contained non-ASCII characters in literal
  parts was indeterminate.  Now the pattern supplied to ``add_route`` is
  assumed to be either: a ``unicode`` value, or a ``str`` value that contains
  only ASCII characters.  If you now want to match the path info from a URL
  that contains high order characters, you can pass the Unicode
  representation of the decoded path portion in the pattern.

- When using a ``traverse=`` route predicate, traversal would fail with a
  URLDecodeError if there were any high-order characters in the traversal
  pattern or in the matched dynamic segments.

- Using a dynamic segment named ``traverse`` in a route pattern like this::

    config.add_route('trav_route', 'traversal/{traverse:.*}')

  Would cause a ``UnicodeDecodeError`` when the route was matched and the
  matched portion of the URL contained any high-order characters.  See
  https://github.com/Pylons/pyramid/issues/385 .

- When using a ``*traverse`` stararg in a route pattern, a URL that matched
  that possessed a ``@@`` in its name (signifying a view name) would be
  inappropriately quoted by the traversal machinery during traversal,
  resulting in the view not being found properly. See
  https://github.com/Pylons/pyramid/issues/382 and
  https://github.com/Pylons/pyramid/issues/375 .

Backwards Incompatibilities
---------------------------

- String values passed to ``route_url`` or ``route_path`` that are meant to
  replace "remainder" matches will now be URL-quoted except for embedded
  slashes. For example::

     config.add_route('remain', '/foo*remainder')
     request.route_path('remain', remainder='abc / def')
     # -> '/foo/abc%20/%20def'

  Previously string values passed as remainder replacements were tacked on
  untouched, without any URL-quoting.  But this doesn't really work logically
  if the value passed is Unicode (raw unicode cannot be placed in a URL or in
  a path) and it is inconsistent with the rest of the URL generation
  machinery if the value is a string (it won't be quoted unless by the
  caller).

  Some folks will have been relying on the older behavior to tack on query
  string elements and anchor portions of the URL; sorry, you'll need to
  change your code to use the ``_query`` and/or ``_anchor`` arguments to
  ``route_path`` or ``route_url`` to do this now.

- If you pass a bytestring that contains non-ASCII characters to
  ``add_route`` as a pattern, it will now fail at startup time.  Use Unicode
  instead.

1.3a3 (2011-12-21)
==================

Features
--------

- Added a ``prequest`` script (along the lines of ``paster request``).  It is
  documented in the "Command-Line Pyramid" chapter in the section entitled
  "Invoking a Request".

- Add undocumented ``__discriminator__`` API to derived view callables.
  e.g. ``adapters.lookup(...).__discriminator__(context, request)``.  It will
  be used by superdynamic systems that require the discriminator to be used
  for introspection after manual view lookup.

Bug Fixes
---------

- Normalized exit values and ``-h`` output for all ``p*`` scripts
  (``pviews``, ``proutes``, etc).

Documentation
-------------

- Added a section named "Making Your Script into a Console Script" in the
  "Command-Line Pyramid" chapter.

- Removed the "Running Pyramid on Google App Engine" tutorial from the main
  docs.  It survives on in the Cookbook
  (http://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/deployment/gae.html).
  Rationale: it provides the correct info for the Python 2.5 version of GAE
  only, and this version of Pyramid does not support Python 2.5.

1.3a2 (2011-12-14)
==================

Features
--------

- New API: ``pyramid.view.view_defaults``. If you use a class as a view, you
  can use the new ``view_defaults`` class decorator on the class to provide
  defaults to the view configuration information used by every
  ``@view_config`` decorator that decorates a method of that class.  It also
  works against view configurations involving a class made imperatively.

- Added a backwards compatibility knob to ``pcreate`` to emulate ``paster
  create`` handling for the ``--list-templates`` option.

- Changed scaffolding machinery around a bit to make it easier for people who
  want to have extension scaffolds that can work across Pyramid 1.0.X, 1.1.X,
  1.2.X and 1.3.X.  See the new "Creating Pyramid Scaffolds" chapter in the
  narrative documentation for more info.

Documentation
-------------

- Added documentation to "View Configuration" narrative documentation chapter
  about ``view_defaults`` class decorator.

- Added API docs for ``view_defaults`` class decorator.

- Added an API docs chapter for ``pyramid.scaffolds``.

- Added a narrative docs chapter named "Creating Pyramid Scaffolds".

Backwards Incompatibilities
---------------------------

- The ``template_renderer`` method of ``pyramid.scaffolds.PyramidScaffold``
  was renamed to ``render_template``.  If you were overriding it, you're a
  bad person, because it wasn't an API before now.  But we're nice so we're
  letting you know.

1.3a1 (2011-12-09)
==================

Features
--------

- Python 3.2 compatibility.

- New ``pyramid.compat`` module and API documentation which provides Python
  2/3 straddling support for Pyramid add-ons and development environments.

- A ``mako.directories`` setting is no longer required to use Mako templates
  Rationale: Mako template renderers can be specified using an absolute asset
  spec.  An entire application can be written with such asset specs,
  requiring no ordered lookup path.

- ``bpython`` interpreter compatibility in ``pshell``.  See the "Command-Line
  Pyramid" narrative docs chapter for more information.

- Added ``get_appsettings`` API function to the ``pyramid.paster`` module.
  This function returns the settings defined within an ``[app:...]`` section
  in a PasteDeploy ini file.

- Added ``setup_logging`` API function to the ``pyramid.paster`` module.
  This function sets up Python logging according to the logging configuration
  in a PasteDeploy ini file.

- Configuration conflict reporting is reported in a more understandable way
  ("Line 11 in file..." vs. a repr of a tuple of similar info).

- A configuration introspection system was added; see the narrative
  documentation chapter entitled "Pyramid Configuration Introspection" for
  more information.  New APIs: ``pyramid.registry.Introspectable``,
  ``pyramid.config.Configurator.introspector``,
  ``pyramid.config.Configurator.introspectable``,
  ``pyramid.registry.Registry.introspector``.

- Allow extra keyword arguments to be passed to the
  ``pyramid.config.Configurator.action`` method.

- New APIs: ``pyramid.path.AssetResolver`` and
  ``pyramid.path.DottedNameResolver``.  The former can be used to resolve
  asset specifications, the latter can be used to resolve dotted names to
  modules or packages.

Bug Fixes
---------

- Make test suite pass on 32-bit systems; closes #286.  closes #306.
  See also https://github.com/Pylons/pyramid/issues/286

- The ``pyramid.view.view_config`` decorator did not accept a ``match_params``
  predicate argument.  See https://github.com/Pylons/pyramid/pull/308

- The AuthTktCookieHelper could potentially generate Unicode headers
  inappropriately when the ``tokens`` argument to remember was used.  See 
  https://github.com/Pylons/pyramid/pull/314.

- The AuthTktAuthenticationPolicy did not use a timing-attack-aware string
  comparator.  See https://github.com/Pylons/pyramid/pull/320 for more info.

- The DummySession in ``pyramid.testing`` now generates a new CSRF token if
  one doesn't yet exist.

- ``request.static_url`` now generates URL-quoted URLs when fed a ``path``
  argument which contains characters that are unsuitable for URLs.  See
  https://github.com/Pylons/pyramid/issues/349 for more info.

- Prevent a scaffold rendering from being named ``site`` (conflicts with
  Python internal site.py).

- Support for using instances as targets of the ``pyramid.wsgi.wsgiapp`` and
  ``pryramid.wsgi.wsgiapp2`` functions.
  See https://github.com/Pylons/pyramid/pull/370 for more info.

Backwards Incompatibilities
---------------------------

- Pyramid no longer runs on Python 2.5 (which includes the most recent
  release of Jython and the Python 2.5 version of GAE as of this writing).

- The ``paster`` command is no longer the documented way to create projects,
  start the server, or run debugging commands.  To create projects from
  scaffolds, ``paster create`` is replaced by the ``pcreate`` console script.
  To serve up a project, ``paster serve`` is replaced by the ``pserve``
  console script.  New console scripts named ``pshell``, ``pviews``,
  ``proutes``, and ``ptweens`` do what their ``paster <commandname>``
  equivalents used to do.  Rationale: the Paste and PasteScript packages do
  not run under Python 3.

- The default WSGI server run as the result of ``pserve`` from newly rendered
  scaffolding is now the ``wsgiref`` WSGI server instead of the
  ``paste.httpserver`` server.  Rationale: Rationale: the Paste and
  PasteScript packages do not run under Python 3.

- The ``pshell`` command (see "paster pshell") no longer accepts a
  ``--disable-ipython`` command-line argument.  Instead, it accepts a ``-p``
  or ``--python-shell`` argument, which can be any of the values ``python``,
  ``ipython`` or ``bpython``.

- Removed the ``pyramid.renderers.renderer_from_name`` function.  It has been
  deprecated since Pyramid 1.0, and was never an API.

- To use ZCML with versions of Pyramid >= 1.3, you will need ``pyramid_zcml``
  version >= 0.8 and ``zope.configuration`` version >= 3.8.0.  The
  ``pyramid_zcml`` package version 0.8 is backwards compatible all the way to
  Pyramid 1.0, so you won't be warned if you have older versions installed
  and upgrade Pyramid "in-place"; it may simply break instead.

Dependencies
------------

- Pyramid no longer depends on the ``zope.component`` package, except as a
  testing dependency.

- Pyramid now depends on a zope.interface>=3.8.0, WebOb>=1.2dev,
  repoze.lru>=0.4, zope.deprecation>=3.5.0, translationstring>=0.4 (for
  Python 3 compatibility purposes).  It also, as a testing dependency,
  depends on WebTest>=1.3.1 for the same reason.

- Pyramid no longer depends on the Paste or PasteScript packages.

Documentation
-------------

- The SQLAlchemy Wiki tutorial has been updated.  It now uses
  ``@view_config`` decorators and an explicit database population script.

- Minor updates to the ZODB Wiki tutorial.

- A narrative documentation chapter named "Extending Pyramid Configuration"
  was added; it describes how to add a new directive, and how use the
  ``pyramid.config.Configurator.action`` method within custom directives.  It
  also describes how to add introspectable objects.

- A narrative documentation chapter named "Pyramid Configuration
  Introspection" was added.  It describes how to query the introspection
  system.

Scaffolds
---------

- Rendered scaffolds have now been changed to be more relocatable (fewer
  mentions of the package name within files in the package).

- The ``routesalchemy`` scaffold has been renamed ``alchemy``, replacing the
  older (traversal-based) ``alchemy`` scaffold (which has been retired).

- The ``starter`` scaffold now uses URL dispatch by default.

1.2 (2011-09-12)
================

Features
--------

- Route pattern replacement marker names can now begin with an underscore.
  See https://github.com/Pylons/pyramid/issues/276.

1.2b3 (2011-09-11)
==================

Bug Fixes
---------

- The route prefix was not taken into account when a static view was added in
  an "include".  See https://github.com/Pylons/pyramid/issues/266 .

1.2b2 (2011-09-08)
==================

Bug Fixes
---------

- The 1.2b1 tarball was a brownbag (particularly for Windows users) because
  it contained filenames with stray quotation marks in inappropriate places.
  We depend on ``setuptools-git`` to produce release tarballs, and when it
  was run to produce the 1.2b1 tarball, it didn't yet cope well with files
  present in git repositories with high-order characters in their filenames.

Documentation
-------------

- Minor tweaks to the "Introduction" narrative chapter example app and
  wording.

1.2b1 (2011-09-08)
==================

Bug Fixes
---------

- Sometimes falling back from territory translations (``de_DE``) to language
  translations (``de``) would not work properly when using a localizer.  See
  https://github.com/Pylons/pyramid/issues/263

- The static file serving machinery could not serve files that started with a
  ``.`` (dot) character.

- Static files with high-order (super-ASCII) characters in their names could
  not be served by a static view.  The static file serving machinery
  inappropriately URL-quoted path segments in filenames when asking for files
  from the filesystem.

- Within ``pyramid.traversal.traversal_path`` , canonicalize URL segments
  from UTF-8 to Unicode before checking whether a segment matches literally
  one of ``.``, the empty string, or ``..`` in case there's some sneaky way
  someone might tunnel those strings via UTF-8 that don't match the literals
  before decoded.

Documentation
-------------

- Added a "What Makes Pyramid Unique" section to the Introduction narrative
  chapter.

1.2a6 (2011-09-06)
==================

Bug Fixes
---------

- AuthTktAuthenticationPolicy with a ``reissue_time`` interfered with logout.
  See https://github.com/Pylons/pyramid/issues/262.

Internal
--------

- Internalize code previously depended upon as imports from the
  ``paste.auth`` module (futureproof).

- Replaced use of ``paste.urlparser.StaticURLParser`` with a derivative of
  Chris Rossi's "happy" static file serving code (futureproof).

- Fixed test suite; on some systems tests would fail due to indeterminate
  test run ordering and a double-push-single-pop of a shared test variable.

Behavior Differences
--------------------

- An ETag header is no longer set when serving a static file.  A
  Last-Modified header is set instead.

- Static file serving no longer supports the ``wsgi.file_wrapper`` extension.

- Instead of returning a ``403 Forbidden`` error when a static file is served
  that cannot be accessed by the Pyramid process' user due to file
  permissions, an IOError (or similar) will be raised.

Scaffolds
---------

- All scaffolds now send the ``cache_max_age`` parameter to the
  ``add_static_view`` method.

1.2a5 (2011-09-04)
==================

Bug Fixes
---------

- The ``route_prefix`` of a configurator was not properly taken into account
  when registering routes in certain circumstances.  See
  https://github.com/Pylons/pyramid/issues/260

Dependencies
------------

- The ``zope.configuration`` package is no longer a dependency.

1.2a4 (2011-09-02)
==================

Features
--------

- Support an ``onerror`` keyword argument to
  ``pyramid.config.Configurator.scan()``.  This onerror keyword argument is
  passed to ``venusian.Scanner.scan()`` to influence error behavior when
  an exception is raised during scanning.

- The ``request_method`` predicate argument to
  ``pyramid.config.Configurator.add_view`` and
  ``pyramid.config.Configurator.add_route`` is now permitted to be a tuple of
  HTTP method names.  Previously it was restricted to being a string
  representing a single HTTP method name.

- Undeprecated ``pyramid.traversal.find_model``,
  ``pyramid.traversal.model_path``, ``pyramid.traversal.model_path_tuple``,
  and ``pyramid.url.model_url``, which were all deprecated in Pyramid 1.0.
  There's just not much cost to keeping them around forever as aliases to
  their renamed ``resource_*`` prefixed functions.

- Undeprecated ``pyramid.view.bfg_view``, which was deprecated in Pyramid
  1.0.  This is a low-cost alias to ``pyramid.view.view_config`` which we'll
  just keep around forever.

Dependencies
------------

- Pyramid now requires Venusian 1.0a1 or better to support the ``onerror``
  keyword argument to ``pyramid.config.Configurator.scan``.

1.2a3 (2011-08-29)
==================

Bug Fixes
---------

- Pyramid did not properly generate static URLs using
  ``pyramid.url.static_url`` when passed a caller-package relative path due
  to a refactoring done in 1.2a1.

- The ``settings`` object emitted a deprecation warning any time
  ``__getattr__`` was called upon it.  However, there are legitimate
  situations in which ``__getattr__`` is called on arbitrary objects
  (e.g. ``hasattr``).  Now, the ``settings`` object only emits the warning
  upon successful lookup.

Internal
--------

- Use ``config.with_package`` in view_config decorator rather than
  manufacturing a new renderer helper (cleanup).

1.2a2 (2011-08-27)
==================

Bug Fixes
---------

- When a ``renderers=`` argument is not specified to the Configurator
  constructor, eagerly register and commit the default renderer set.  This
  permits the overriding of the default renderers, which was broken in 1.2a1
  without a commit directly after Configurator construction.

- Mako rendering exceptions had the wrong value for an error message.

- An include could not set a root factory successfully because the
  Configurator constructor unconditionally registered one that would be
  treated as if it were "the word of the user".

Features
--------

- A session factory can now be passed in using the dotted name syntax.

1.2a1 (2011-08-24)
==================

Features
--------

- The ``[pshell]`` section in an ini configuration file now treats a
  ``setup`` key as a dotted name that points to a callable that is passed the
  bootstrap environment.  It can mutate the environment as necessary for
  great justice.

- A new configuration setting named ``pyramid.includes`` is now available.
  It is described in the "Environment Variables and ``.ini`` Files Settings"
  narrative documentation chapter.

- Added a ``route_prefix`` argument to the
  ``pyramid.config.Configurator.include`` method.  This argument allows you
  to compose URL dispatch applications together.  See the section entitled
  "Using a Route Prefix to Compose Applications" in the "URL Dispatch"
  narrative documentation chapter.

- Added a ``pyramid.security.NO_PERMISSION_REQUIRED`` constant for use in
  ``permission=`` statements to view configuration.  This constant has a
  value of the string ``__no_permission_required__``.  This string value was
  previously referred to in documentation; now the documentation uses the
  constant.

- Added a decorator-based way to configure a response adapter:
  ``pyramid.response.response_adapter``.  This decorator has the same use as
  ``pyramid.config.Configurator.add_response_adapter`` but it's declarative.

- The ``pyramid.events.BeforeRender`` event now has an attribute named
  ``rendering_val``.  This can be used to introspect the value returned by a
  view in a BeforeRender subscriber.

- New configurator directive: ``pyramid.config.Configurator.add_tween``.
  This directive adds a "tween".  A "tween" is used to wrap the Pyramid
  router's primary request handling function.  This is a feature may be used
  by Pyramid framework extensions, to provide, for example, view timing
  support and as a convenient place to hang bookkeeping code.

  Tweens are further described in the narrative docs section in the Hooks
  chapter, named "Registering Tweens".

- New paster command ``paster ptweens``, which prints the current "tween"
  configuration for an application.  See the section entitled "Displaying
  Tweens" in the Command-Line Pyramid chapter of the narrative documentation
  for more info.

- The Pyramid debug logger now uses the standard logging configuration
  (usually set up by Paste as part of startup).  This means that output from
  e.g. ``debug_notfound``, ``debug_authorization``, etc. will go to the
  normal logging channels.  The logger name of the debug logger will be the
  package name of the *caller* of the Configurator's constructor.

- A new attribute is available on request objects: ``exc_info``.  Its value
  will be ``None`` until an exception is caught by the Pyramid router, after
  which it will be the result of ``sys.exc_info()``.

- ``pyramid.testing.DummyRequest`` now implements the
  ``add_finished_callback`` and ``add_response_callback`` methods.

- New methods of the ``pyramid.config.Configurator`` class:
  ``set_authentication_policy`` and ``set_authorization_policy``.  These are
  meant to be consumed mostly by add-on authors.

- New Configurator method: ``set_root_factory``.

- Pyramid no longer eagerly commits some default configuration statements at
  Configurator construction time, which permits values passed in as
  constructor arguments (e.g. ``authentication_policy`` and
  ``authorization_policy``) to override the same settings obtained via an
  "include".

- Better Mako rendering exceptions via
  ``pyramid.mako_templating.MakoRenderingException``

- New request methods: ``current_route_url``, ``current_route_path``, and
  ``static_path``.

- New functions in ``pyramid.url``: ``current_route_path`` and
  ``static_path``.

- The ``pyramid.request.Request.static_url`` API (and its brethren
  ``pyramid.request.Request.static_path``, ``pyramid.url.static_url``, and
  ``pyramid.url.static_path``) now accept an asbolute filename as a "path"
  argument.  This will generate a URL to an asset as long as the filename is
  in a directory which was previously registered as a static view.
  Previously, trying to generate a URL to an asset using an absolute file
  path would raise a ValueError.

- The ``RemoteUserAuthenticationPolicy ``, ``AuthTktAuthenticationPolicy``,
  and ``SessionAuthenticationPolicy`` constructors now accept an additional
  keyword argument named ``debug``.  By default, this keyword argument is
  ``False``.  When it is ``True``, debug information will be sent to the
  Pyramid debug logger (usually on stderr) when the ``authenticated_userid``
  or ``effective_principals`` method is called on any of these policies.  The
  output produced can be useful when trying to diagnose
  authentication-related problems.

- New view predicate: ``match_param``.  Example: a view added via
  ``config.add_view(aview, match_param='action=edit')`` will be called only
  when the ``request.matchdict`` has a value inside it named ``action`` with
  a value of ``edit``.

Internal
--------

- The Pyramid "exception view" machinery is now implemented as a "tween"
  (``pyramid.tweens.excview_tween_factory``).

- WSGIHTTPException (HTTPFound, HTTPNotFound, etc) now has a new API named
  "prepare" which renders the body and content type when it is provided with
  a WSGI environ.  Required for debug toolbar.

- Once ``__call__`` or ``prepare`` is called on a WSGIHTTPException, the body
  will be set, and subsequent calls to ``__call__`` will always return the
  same body.  Delete the body attribute to rerender the exception body.

- Previously the ``pyramid.events.BeforeRender`` event *wrapped* a dictionary
  (it addressed it as its ``_system`` attribute).  Now it *is* a dictionary
  (it inherits from ``dict``), and it's the value that is passed to templates
  as a top-level dictionary.

- The ``route_url``, ``route_path``, ``resource_url``, ``static_url``, and
  ``current_route_url`` functions in the ``pyramid.url`` package now delegate
  to a method on the request they've been passed, instead of the other way
  around.  The pyramid.request.Request object now inherits from a mixin named
  pyramid.url.URLMethodsMixin to make this possible, and all url/path
  generation logic is embedded in this mixin.

- Refactor ``pyramid.config`` into a package.

- Removed the ``_set_security_policies`` method of the Configurator.

- Moved the ``StaticURLInfo`` class from ``pyramid.static`` to
  ``pyramid.config.views``.

- Move the ``Settings`` class from ``pyramid.settings`` to
  ``pyramid.config.settings``.

- Move the ``OverrideProvider``, ``PackageOverrides``, ``DirectoryOverride``,
  and ``FileOverride`` classes from ``pyramid.asset`` to
  ``pyramid.config.assets``.

Deprecations
------------

- All Pyramid-related deployment settings (e.g. ``debug_all``,
  ``debug_notfound``) are now meant to be prefixed with the prefix
  ``pyramid.``.  For example: ``debug_all`` -> ``pyramid.debug_all``.  The
  old non-prefixed settings will continue to work indefinitely but supplying
  them may eventually print a deprecation warning.  All scaffolds and
  tutorials have been changed to use prefixed settings.

- The ``settings`` dictionary now raises a deprecation warning when you
  attempt to access its values via ``__getattr__`` instead of
  via ``__getitem__``.

Backwards Incompatibilities
---------------------------

- If a string is passed as the ``debug_logger`` parameter to a Configurator,
  that string is considered to be the name of a global Python logger rather
  than a dotted name to an instance of a logger.

- The ``pyramid.config.Configurator.include`` method now accepts only a
  single ``callable`` argument (a sequence of callables used to be
  permitted).  If you are passing more than one ``callable`` to
  ``pyramid.config.Configurator.include``, it will break.  You now must now
  instead make a separate call to the method for each callable.  This change
  was introduced to support the ``route_prefix`` feature of include.

- It may be necessary to more strictly order configuration route and view
  statements when using an "autocommitting" Configurator.  In the past, it
  was possible to add a view which named a route name before adding a route
  with that name when you used an autocommitting configurator.  For example::

    config = Configurator(autocommit=True)
    config.add_view('my.pkg.someview', route_name='foo')
    config.add_route('foo', '/foo')

  The above will raise an exception when the view attempts to add itself.
  Now you must add the route before adding the view::

    config = Configurator(autocommit=True)
    config.add_route('foo', '/foo')
    config.add_view('my.pkg.someview', route_name='foo')

  This won't effect "normal" users, only people who have legacy BFG codebases
  that used an autocommitting configurator and possibly tests that use the
  configurator API (the configurator returned by ``pyramid.testing.setUp`` is
  an autocommitting configurator).  The right way to get around this is to
  use a non-autocommitting configurator (the default), which does not have
  these directive ordering requirements.

- The ``pyramid.config.Configurator.add_route`` directive no longer returns a
  route object.  This change was required to make route vs. view
  configuration processing work properly.

Documentation
-------------

- Narrative and API documentation which used the ``route_url``,
  ``route_path``, ``resource_url``, ``static_url``, and ``current_route_url``
  functions in the ``pyramid.url`` package have now been changed to use
  eponymous methods of the request instead.

- Added a section entitled "Using a Route Prefix to Compose Applications" to
  the "URL Dispatch" narrative documentation chapter.

- Added a new module to the API docs: ``pyramid.tweens``.

- Added a "Registering Tweens" section to the "Hooks" narrative chapter.

- Added a "Displaying Tweens" section to the "Command-Line Pyramid" narrative
  chapter.

- Added documentation for the ``pyramid.tweens`` and ``pyramid.includes``
  configuration settings to the "Environment Variables and ``.ini`` Files
  Settings" chapter.

- Added a Logging chapter to the narrative docs (based on the Pylons logging
  docs, thanks Phil).

- Added a Paste chapter to the narrative docs (moved content from the Project
  chapter).

- Added the ``pyramid.interfaces.IDict`` interface representing the methods
  of a dictionary, for documentation purposes only (IMultiDict and
  IBeforeRender inherit from it).

- All tutorials now use - The ``route_url``, ``route_path``,
  ``resource_url``, ``static_url``, and ``current_route_url`` methods of the
  request rather than the function variants imported from ``pyramid.url``.

- The ZODB wiki tutorial now uses the ``pyramid_zodbconn`` package rather
  than the ``repoze.zodbconn`` package to provide ZODB integration.

Dependency Changes
------------------

- Pyramid now relies on PasteScript >= 1.7.4.  This version contains a
  feature important for allowing flexible logging configuration.

Scaffolds
----------

- All scaffolds now use the ``pyramid_tm`` package rather than the
  ``repoze.tm2`` middleware to manage transaction management.

- The ZODB scaffold now uses the ``pyramid_zodbconn`` package rather than the
  ``repoze.zodbconn`` package to provide ZODB integration.

- All scaffolds now use the ``pyramid_debugtoolbar`` package rather than the
  ``WebError`` package to provide interactive debugging features.

- Projects created via a scaffold no longer depend on the ``WebError``
  package at all; configuration in the ``production.ini`` file which used to
  require its ``error_catcher`` middleware has been removed.  Configuring
  error catching / email sending is now the domain of the ``pyramid_exclog``
  package (see http://docs.pylonsproject.org/projects/pyramid_exclog/en/latest/).

Bug Fixes
---------

- Fixed an issue with the default renderer not working at certain times.  See
  https://github.com/Pylons/pyramid/issues/249


1.1 (2011-07-22)
================

Features
--------

- Added the ``pyramid.renderers.null_renderer`` object as an API.  The null
  renderer is an object that can be used in advanced integration cases as
  input to the view configuration ``renderer=`` argument.  When the null
  renderer is used as a view renderer argument, Pyramid avoids converting the
  view callable result into a Response object.  This is useful if you want to
  reuse the view configuration and lookup machinery outside the context of
  its use by the Pyramid router.  This feature was added for consumption by
  the ``pyramid_rpc`` package, which uses view configuration and lookup
  outside the context of a router in exactly this way.  ``pyramid_rpc`` has
  been broken under 1.1 since 1.1b1; adding it allows us to make it work
  again.

- Change all scaffolding templates that point to docs.pylonsproject.org to
  use ``/projects/pyramid/current`` rather than ``/projects/pyramid/dev``.

Internals
---------

- Remove ``compat`` code that served only the purpose of providing backwards
  compatibility with Python 2.4.

- Add a deprecation warning for non-API function
  ``pyramid.renderers.renderer_from_name`` which has seen use in the wild.

- Add a ``clone`` method to ``pyramid.renderers.RendererHelper`` for use by
  the ``pyramid.view.view_config`` decorator.

Documentation
-------------

- Fixed two typos in wiki2 (SQLA + URL Dispatch) tutorial.

- Reordered chapters in narrative section for better new user friendliness.

- Added more indexing markers to sections in documentation.

1.1b4 (2011-07-18)
==================

Documentation
-------------

- Added a section entitled "Writing a Script" to the "Command-Line Pyramid"
  chapter.

Backwards Incompatibilities
---------------------------

- We added the ``pyramid.scripting.make_request`` API too hastily in 1.1b3.
  It has been removed.  Sorry for any inconvenience.  Use the
  ``pyramid.request.Request.blank`` API instead.

Features
--------

- The ``paster pshell``, ``paster pviews``, and ``paster proutes`` commands
  each now under the hood uses ``pyramid.paster.bootstrap``, which makes it
  possible to supply an ``.ini`` file without naming the "right" section in
  the file that points at the actual Pyramid application.  Instead, you can
  generally just run ``paster {pshell|proutes|pviews} development.ini`` and
  it will do mostly the right thing.

Bug Fixes
---------

- Omit custom environ variables when rendering a custom exception template in
  ``pyramid.httpexceptions.WSGIHTTPException._set_default_attrs``;
  stringifying thse may trigger code that should not be executed; see
  https://github.com/Pylons/pyramid/issues/239

1.1b3 (2011-07-15)
==================

Features
--------

- Fix corner case to ease semifunctional testing of views: create a new
  rendererinfo to clear out old registry on a rescan.  See
  https://github.com/Pylons/pyramid/pull/234.

- New API class: ``pyramid.static.static_view``.  This supersedes the
  deprecated ``pyramid.view.static`` class.  ``pyramid.static.static_view``
  by default serves up documents as the result of the request's
  ``path_info``, attribute rather than it's ``subpath`` attribute (the
  inverse was true of ``pyramid.view.static``, and still is).
  ``pyramid.static.static_view`` exposes a ``use_subpath`` flag for use when
  you want the static view to behave like the older deprecated version.

- A new API function ``pyramid.paster.bootstrap`` has been added to make
  writing scripts that bootstrap a Pyramid environment easier, e.g.::

      from pyramid.paster import bootstrap
      info = bootstrap('/path/to/my/development.ini')
      request = info['request']
      print request.route_url('myroute')

- A new API function ``pyramid.scripting.prepare`` has been added.  It is a
  lower-level analogue of ``pyramid.paster.boostrap`` that accepts a request
  and a registry instead of a config file argument, and is used for the same
  purpose::

      from pyramid.scripting import prepare
      info = prepare(registry=myregistry)
      request = info['request']
      print request.route_url('myroute')

- A new API function ``pyramid.scripting.make_request`` has been added.  The
  resulting request will have a ``registry`` attribute.  It is meant to be
  used in conjunction with ``pyramid.scripting.prepare`` and/or
  ``pyramid.paster.bootstrap`` (both of which accept a request as an
  argument)::

      from pyramid.scripting import make_request
      request = make_request('/')

- New API attribute ``pyramid.config.global_registries`` is an iterable
  object that contains references to every Pyramid registry loaded into the
  current process via ``pyramid.config.Configurator.make_app``.  It also has
  a ``last`` attribute containing the last registry loaded.  This is used by
  the scripting machinery, and is available for introspection.

Deprecations
------------

- The ``pyramid.view.static`` class has been deprecated in favor of the newer
  ``pyramid.static.static_view`` class.  A deprecation warning is raised when
  it is used.  You should replace it with a reference to
  ``pyramid.static.static_view`` with the ``use_subpath=True`` argument.

Bug Fixes
---------

- Without a mo-file loaded for the combination of domain/locale,
  ``pyramid.i18n.Localizer.pluralize`` run using that domain/locale
  combination raised an inscrutable "translations object has no attr
  'plural'" error.  Now, instead it "works" (it uses a germanic pluralization
  by default).  It's nonsensical to try to pluralize something without
  translations for that locale/domain available, but this behavior matches
  the behavior of ``pyramid.i18n.Localizer.translate`` so it's at least
  consistent; see https://github.com/Pylons/pyramid/issues/235.

1.1b2 (2011-07-13)
==================

Features
--------

- New environment setting ``PYRAMID_PREVENT_HTTP_CACHE`` and new
  configuration file value ``prevent_http_cache``.  These are synomymous and
  allow you to prevent HTTP cache headers from being set by Pyramid's
  ``http_cache`` machinery globally in a process.  see the "Influencing HTTP
  Caching" section of the "View Configuration" narrative chapter and the
  detailed documentation for this setting in the "Environment Variables and
  Configuration Settings" narrative chapter.

Behavior Changes
----------------

- Previously, If a ``BeforeRender`` event subscriber added a value via the
  ``__setitem__`` or ``update`` methods of the event object with a key that
  already existed in the renderer globals dictionary, a ``KeyError`` was
  raised.  With the deprecation of the "add_renderer_globals" feature of the
  configurator, there was no way to override an existing value in the
  renderer globals dictionary that already existed.  Now, the event object
  will overwrite an older value that is already in the globals dictionary
  when its ``__setitem__`` or ``update`` is called (as well as the new
  ``setdefault`` method), just like a plain old dictionary.  As a result, for
  maximum interoperability with other third-party subscribers, if you write
  an event subscriber meant to be used as a BeforeRender subscriber, your
  subscriber code will now need to (using ``.get`` or ``__contains__`` of the
  event object) ensure no value already exists in the renderer globals
  dictionary before setting an overriding value.

Bug Fixes
---------

- The ``Configurator.add_route`` method allowed two routes with the same
  route to be added without an intermediate ``config.commit()``.  If you now
  receive a ``ConfigurationError`` at startup time that appears to be
  ``add_route`` related, you'll need to either a) ensure that all of your
  route names are unique or b) call ``config.commit()`` before adding a
  second route with the name of a previously added name or c) use a
  Configurator that works in ``autocommit`` mode.

- The ``pyramid_routesalchemy`` and ``pyramid_alchemy`` scaffolds
  inappropriately used ``DBSession.rollback()`` instead of
  ``transaction.abort()`` in one place.

- We now clear ``request.response`` before we invoke an exception view; an
  exception view will be working with a request.response that has not been
  touched by any code prior to the exception.

- Views associated with routes with spaces in the route name may not have
  been looked up correctly when using Pyramid with ``zope.interface`` 3.6.4
  and better.  See https://github.com/Pylons/pyramid/issues/232.

Documentation
-------------

- Wiki2 (SQLAlchemy + URL Dispatch) tutorial ``models.initialize_sql`` didn't
  match the ``pyramid_routesalchemy`` scaffold function of the same name; it
  didn't get synchronized when it was changed in the scaffold.

- New documentation section in View Configuration narrative chapter:
  "Influencing HTTP Caching".

1.1b1 (2011-07-10)
==================

Features
--------

- It is now possible to invoke ``paster pshell`` even if the paste ini file
  section name pointed to in its argument is not actually a Pyramid WSGI
  application.  The shell will work in a degraded mode, and will warn the
  user.  See "The Interactive Shell" in the "Creating a Pyramid Project"
  narrative documentation section.

- ``paster pshell`` now offers more built-in global variables by default
  (including ``app`` and ``settings``).  See "The Interactive Shell" in the
  "Creating a Pyramid Project" narrative documentation section.

- It is now possible to add a ``[pshell]`` section to your application's .ini
  configuration file, which influences the global names available to a pshell
  session.  See "Extending the Shell" in the "Creating a Pyramid Project"
  narrative documentation chapter.

- The ``config.scan`` method has grown a ``**kw`` argument.  ``kw`` argument
  represents a set of keyword arguments to pass to the Venusian ``Scanner``
  object created by Pyramid.  (See the Venusian documentation for more
  information about ``Scanner``).

- New request property: ``json_body``. This property will return the
  JSON-decoded variant of the request body.  If the request body is not
  well-formed JSON, this property will raise an exception.

- A new value ``http_cache`` can be used as a view configuration
  parameter.

  When you supply an ``http_cache`` value to a view configuration, the
  ``Expires`` and ``Cache-Control`` headers of a response generated by the
  associated view callable are modified.  The value for ``http_cache`` may be
  one of the following:

  - A nonzero integer.  If it's a nonzero integer, it's treated as a number
    of seconds.  This number of seconds will be used to compute the
    ``Expires`` header and the ``Cache-Control: max-age`` parameter of
    responses to requests which call this view.  For example:
    ``http_cache=3600`` instructs the requesting browser to 'cache this
    response for an hour, please'.

  - A ``datetime.timedelta`` instance.  If it's a ``datetime.timedelta``
    instance, it will be converted into a number of seconds, and that number
    of seconds will be used to compute the ``Expires`` header and the
    ``Cache-Control: max-age`` parameter of responses to requests which call
    this view.  For example: ``http_cache=datetime.timedelta(days=1)``
    instructs the requesting browser to 'cache this response for a day,
    please'.

  - Zero (``0``).  If the value is zero, the ``Cache-Control`` and
    ``Expires`` headers present in all responses from this view will be
    composed such that client browser cache (and any intermediate caches) are
    instructed to never cache the response.

  - A two-tuple.  If it's a two tuple (e.g. ``http_cache=(1,
    {'public':True})``), the first value in the tuple may be a nonzero
    integer or a ``datetime.timedelta`` instance; in either case this value
    will be used as the number of seconds to cache the response.  The second
    value in the tuple must be a dictionary.  The values present in the
    dictionary will be used as input to the ``Cache-Control`` response
    header.  For example: ``http_cache=(3600, {'public':True})`` means 'cache
    for an hour, and add ``public`` to the Cache-Control header of the
    response'.  All keys and values supported by the
    ``webob.cachecontrol.CacheControl`` interface may be added to the
    dictionary.  Supplying ``{'public':True}`` is equivalent to calling
    ``response.cache_control.public = True``.

  Providing a non-tuple value as ``http_cache`` is equivalent to calling
  ``response.cache_expires(value)`` within your view's body.

  Providing a two-tuple value as ``http_cache`` is equivalent to calling
  ``response.cache_expires(value[0], **value[1])`` within your view's body.

  If you wish to avoid influencing, the ``Expires`` header, and instead wish
  to only influence ``Cache-Control`` headers, pass a tuple as ``http_cache``
  with the first element of ``None``, e.g.: ``(None, {'public':True})``.

Bug Fixes
---------

- Framework wrappers of the original view (such as http_cached and so on)
  relied on being able to trust that the response they were receiving was an
  IResponse.  It wasn't always, because the response was resolved by the
  router instead of early in the view wrapping process.  This has been fixed.

Documentation
-------------

- Added a section in the "Webob" chapter named "Dealing With A JSON-Encoded
  Request Body" (usage of ``request.json_body``).

Behavior Changes
----------------

- The ``paster pshell``, ``paster proutes``, and ``paster pviews`` commands
  now take a single argument in the form ``/path/to/config.ini#sectionname``
  rather than the previous 2-argument spelling ``/path/to/config.ini
  sectionname``.  ``#sectionname`` may be omitted, in which case ``#main`` is
  assumed.

1.1a4 (2011-07-01)
==================

Bug Fixes
---------

- ``pyramid.testing.DummyRequest`` now raises deprecation warnings when
  attributes deprecated for ``pyramid.request.Request`` are accessed (like
  ``response_content_type``).  This is for the benefit of folks running unit
  tests which use DummyRequest instead of a "real" request, so they know
  things are deprecated without necessarily needing a functional test suite.

- The ``pyramid.events.subscriber`` directive behaved contrary to the
  documentation when passed more than one interface object to its
  constructor.  For example, when the following listener was registered::

     @subscriber(IFoo, IBar)
     def expects_ifoo_events_and_ibar_events(event):
         print event

  The Events chapter docs claimed that the listener would be registered and
  listening for both ``IFoo`` and ``IBar`` events.  Instead, it registered an
  "object event" subscriber which would only be called if an IObjectEvent was
  emitted where the object interface was ``IFoo`` and the event interface was
  ``IBar``.

  The behavior now matches the documentation. If you were relying on the
  buggy behavior of the 1.0 ``subscriber`` directive in order to register an
  object event subscriber, you must now pass a sequence to indicate you'd
  like to register a subscriber for an object event. e.g.::

     @subscriber([IFoo, IBar])
     def expects_object_event(object, event):
         print object, event

Features
--------

- Add JSONP renderer (see "JSONP renderer" in the Renderers chapter of the
  documentation).

Deprecations
------------

- Deprecated the ``set_renderer_globals_factory`` method of the Configurator
  and the ``renderer_globals`` Configurator constructor parameter.

Documentation
-------------

- The Wiki and Wiki2 tutorial "Tests" chapters each had two bugs: neither did
  told the user to depend on WebTest, and 2 tests failed in each as the
  result of changes to Pyramid itself.  These issues have been fixed.

- Move 1.0.X CHANGES.txt entries to HISTORY.txt.

1.1a3 (2011-06-26)
==================

Features
--------

- Added ``mako.preprocessor`` config file parameter; allows for a Mako
  preprocessor to be specified as a Python callable or Python dotted name.
  See https://github.com/Pylons/pyramid/pull/183 for rationale.

Bug fixes
---------

- Pyramid would raise an AttributeError in the Configurator when attempting
  to set a ``__text__`` attribute on a custom predicate that was actually a
  classmethod.  See https://github.com/Pylons/pyramid/pull/217 .

- Accessing or setting deprecated response_* attrs on request
  (e.g. ``response_content_type``) now issues a deprecation warning at access
  time rather than at rendering time.

1.1a2 (2011-06-22)
==================

Bug Fixes
---------

- 1.1a1 broke Akhet by not providing a backwards compatibility import shim
  for ``pyramid.paster.PyramidTemplate``.  Now one has been added, although a
  deprecation warning is emitted when Akhet imports it.

- If multiple specs were provided in a single call to
  ``config.add_translation_dirs``, the directories were inserted into the
  beginning of the directory list in the wrong order: they were inserted in
  the reverse of the order they were provided in the ``*specs`` list (items
  later in the list were added before ones earlier in the list).  This is now
  fixed.

Backwards Incompatibilities
---------------------------

- The pyramid Router attempted to set a value into the key
  ``environ['repoze.bfg.message']`` when it caught a view-related exception
  for backwards compatibility with applications written for ``repoze.bfg``
  during error handling.  It did this by using code that looked like so::

                    # "why" is an exception object
                    try: 
                        msg = why[0]
                    except:
                        msg = ''

                    environ['repoze.bfg.message'] = msg

  Use of the value ``environ['repoze.bfg.message']`` was docs-deprecated in
  Pyramid 1.0.  Our standing policy is to not remove features after a
  deprecation for two full major releases, so this code was originally slated
  to be removed in Pyramid 1.2.  However, computing the
  ``repoze.bfg.message`` value was the source of at least one bug found in
  the wild (https://github.com/Pylons/pyramid/issues/199), and there isn't a
  foolproof way to both preserve backwards compatibility and to fix the bug.
  Therefore, the code which sets the value has been removed in this release.
  Code in exception views which relies on this value's presence in the
  environment should now use the ``exception`` attribute of the request
  (e.g. ``request.exception[0]``) to retrieve the message instead of relying
  on ``request.environ['repoze.bfg.message']``.

1.1a1 (2011-06-20)
==================

Documentation
-------------

- The term "template" used to refer to both "paster templates" and "rendered
  templates" (templates created by a rendering engine.  i.e. Mako, Chameleon,
  Jinja, etc.).  "Paster templates" will now be referred to as "scaffolds",
  whereas the name for "rendered templates" will remain as "templates."

- The ``wiki`` (ZODB+Traversal) tutorial was updated slightly.

- The ``wiki2`` (SQLA+URL Dispatch) tutorial was updated slightly.

- Make ``pyramid.interfaces.IAuthenticationPolicy`` and
  ``pyramid.interfaces.IAuthorizationPolicy`` public interfaces, and refer to
  them within the ``pyramid.authentication`` and ``pyramid.authorization``
  API docs.

- Render the function definitions for each exposed interface in
  ``pyramid.interfaces``.

- Add missing docs reference to
  ``pyramid.config.Configurator.set_view_mapper`` and refer to it within
  Hooks chapter section named "Using a View Mapper".

- Added section to the "Environment Variables and ``.ini`` File Settings"
  chapter in the narrative documentation section entitled "Adding a Custom
  Setting".

- Added documentation for a "multidict" (e.g. the API of ``request.POST``) as
  interface API documentation.

- Added a section to the "URL Dispatch" narrative chapter regarding the new
  "static" route feature.

- Added "What's New in Pyramid 1.1" to HTML rendering of documentation.

- Added API docs for ``pyramid.authentication.SessionAuthenticationPolicy``.

- Added API docs for ``pyramid.httpexceptions.exception_response``.

- Added "HTTP Exceptions" section to Views narrative chapter including a
  description of ``pyramid.httpexceptions.exception_response``.

Features
--------

- Add support for language fallbacks: when trying to translate for a
  specific territory (such as ``en_GB``) fall back to translations
  for the language (ie ``en``). This brings the translation behaviour in line
  with GNU gettext and fixes partially translated texts when using C
  extensions.

- New authentication policy:
  ``pyramid.authentication.SessionAuthenticationPolicy``, which uses a session
  to store credentials.

- Accessing the ``response`` attribute of a ``pyramid.request.Request``
  object (e.g. ``request.response`` within a view) now produces a new
  ``pyramid.response.Response`` object.  This feature is meant to be used
  mainly when a view configured with a renderer needs to set response
  attributes: all renderers will use the Response object implied by
  ``request.response`` as the response object returned to the router.

  ``request.response`` can also be used by code in a view that does not use a
  renderer, however the response object that is produced by
  ``request.response`` must be returned when a renderer is not in play (it is
  not a "global" response).

- Integers and longs passed as ``elements`` to ``pyramid.url.resource_url``
  or ``pyramid.request.Request.resource_url`` e.g. ``resource_url(context,
  request, 1, 2)`` (``1`` and ``2`` are the ``elements``) will now be
  converted implicitly to strings in the result.  Previously passing integers
  or longs as elements would cause a TypeError.

- ``pyramid_alchemy`` paster template now uses ``query.get`` rather than
  ``query.filter_by`` to take better advantage of identity map caching.

- ``pyramid_alchemy`` paster template now has unit tests.

- Added ``pyramid.i18n.make_localizer`` API (broken out from
  ``get_localizer`` guts).

- An exception raised by a NewRequest event subscriber can now be caught by
  an exception view.

- It is now possible to get information about why Pyramid raised a Forbidden
  exception from within an exception view.  The ``ACLDenied`` object returned
  by the ``permits`` method of each stock authorization policy
  (``pyramid.interfaces.IAuthorizationPolicy.permits``) is now attached to
  the Forbidden exception as its ``result`` attribute.  Therefore, if you've
  created a Forbidden exception view, you can see the ACE, ACL, permission,
  and principals involved in the request as
  eg. ``context.result.permission``, ``context.result.acl``, etc within the
  logic of the Forbidden exception view.

- Don't explicitly prevent the ``timeout`` from being lower than the
  ``reissue_time`` when setting up an ``AuthTktAuthenticationPolicy``
  (previously such a configuration would raise a ``ValueError``, now it's
  allowed, although typically nonsensical).  Allowing the nonsensical
  configuration made the code more understandable and required fewer tests.

- A new paster command named ``paster pviews`` was added.  This command
  prints a summary of potentially matching views for a given path.  See the
  section entitled "Displaying Matching Views for a Given URL" in the "View
  Configuration" chapter of the narrative documentation for more information.

- The ``add_route`` method of the Configurator now accepts a ``static``
  argument.  If this argument is ``True``, the added route will never be
  considered for matching when a request is handled.  Instead, it will only
  be useful for URL generation via ``route_url`` and ``route_path``.  See the
  section entitled "Static Routes" in the URL Dispatch narrative chapter for
  more information.

- A default exception view for the context
  ``pyramid.interfaces.IExceptionResponse`` is now registered by default.
  This means that an instance of any exception response class imported from
  ``pyramid.httpexceptions`` (such as ``HTTPFound``) can now be raised from
  within view code; when raised, this exception view will render the
  exception to a response.

- A function named ``pyramid.httpexceptions.exception_response`` is a
  shortcut that can be used to create HTTP exception response objects using
  an HTTP integer status code.

- The Configurator now accepts an additional keyword argument named
  ``exceptionresponse_view``.  By default, this argument is populated with a
  default exception view function that will be used when a response is raised
  as an exception. When ``None`` is passed for this value, an exception view
  for responses will not be registered.  Passing ``None`` returns the
  behavior of raising an HTTP exception to that of Pyramid 1.0 (the exception
  will propagate to middleware and to the WSGI server).

- The ``pyramid.request.Request`` class now has a ``ResponseClass`` interface
  which points at ``pyramid.response.Response``.

- The ``pyramid.response.Response`` class now has a ``RequestClass``
  interface which points at ``pyramid.request.Request``.

- It is now possible to return an arbitrary object from a Pyramid view
  callable even if a renderer is not used, as long as a suitable adapter to
  ``pyramid.interfaces.IResponse`` is registered for the type of the returned
  object by using the new
  ``pyramid.config.Configurator.add_response_adapter`` API.  See the section
  in the Hooks chapter of the documentation entitled "Changing How Pyramid
  Treats View Responses".

- The Pyramid router will now, by default, call the ``__call__`` method of
  WebOb response objects when returning a WSGI response.  This means that,
  among other things, the ``conditional_response`` feature of WebOb response
  objects will now behave properly.

- New method named ``pyramid.request.Request.is_response``.  This method
  should be used instead of the ``pyramid.view.is_response`` function, which
  has been deprecated.

Bug Fixes
---------

- URL pattern markers used in URL dispatch are permitted to specify a custom
  regex. For example, the pattern ``/{foo:\d+}`` means to match ``/12345``
  (foo==12345 in the match dictionary) but not ``/abc``. However, custom
  regexes in a pattern marker which used squiggly brackets did not work. For
  example, ``/{foo:\d{4}}`` would fail to match ``/1234`` and
  ``/{foo:\d{1,2}}`` would fail to match ``/1`` or ``/11``. One level of
  inner squiggly brackets is now recognized so that the prior two patterns
  given as examples now work. See also
  https://github.com/Pylons/pyramid/issues/#issue/123.

- Don't send port numbers along with domain information in cookies set by
  AuthTktCookieHelper (see https://github.com/Pylons/pyramid/issues/131).

- ``pyramid.url.route_path`` (and the shortcut
  ``pyramid.request.Request.route_url`` method) now include the WSGI
  SCRIPT_NAME at the front of the path if it is not empty (see
  https://github.com/Pylons/pyramid/issues/135).

- ``pyramid.testing.DummyRequest`` now has a ``script_name`` attribute (the
  empty string).

- Don't quote ``:@&+$,`` symbols in ``*elements`` passed to
  ``pyramid.url.route_url`` or ``pyramid.url.resource_url`` (see
  https://github.com/Pylons/pyramid/issues#issue/141).

- Include SCRIPT_NAME in redirects issued by
  ``pyramid.view.append_slash_notfound_view`` (see
  https://github.com/Pylons/pyramid/issues#issue/149).

- Static views registered with ``config.add_static_view`` which also included
  a ``permission`` keyword argument would not work as expected, because
  ``add_static_view`` also registered a route factory internally.  Because a
  route factory was registered internally, the context checked by the Pyramid
  permission machinery never had an ACL.  ``add_static_view`` no longer
  registers a route with a factory, so the default root factory will be used.

- ``config.add_static_view`` now passes extra keyword arguments it receives
  to ``config.add_route`` (calling add_static_view is mostly logically
  equivalent to adding a view of the type ``pyramid.static.static_view``
  hooked up to a route with a subpath).  This makes it possible to pass e.g.,
  ``factory=`` to ``add_static_view`` to protect a particular static view
  with a custom ACL.

- ``testing.DummyRequest`` used the wrong registry (the global registry) as
  ``self.registry`` if a dummy request was created *before* ``testing.setUp``
  was executed (``testing.setUp`` pushes a local registry onto the
  threadlocal stack). Fixed by implementing ``registry`` as a property for
  DummyRequest instead of eagerly assigning an attribute.
  See also https://github.com/Pylons/pyramid/issues/165

- When visiting a URL that represented a static view which resolved to a
  subdirectory, the ``index.html`` of that subdirectory would not be served
  properly.  Instead, a redirect to ``/subdir`` would be issued.  This has
  been fixed, and now visiting a subdirectory that contains an ``index.html``
  within a static view returns the index.html properly.  See also
  https://github.com/Pylons/pyramid/issues/67.

- Redirects issued by a static view did not take into account any existing
  ``SCRIPT_NAME`` (such as one set by a url mapping composite).  Now they do.

- The ``pyramid.wsgi.wsgiapp2`` decorator did not take into account the
  ``SCRIPT_NAME`` in the origin request.

- The ``pyramid.wsgi.wsgiapp2`` decorator effectively only worked when it
  decorated a view found via traversal; it ignored the ``PATH_INFO`` that was
  part of a url-dispatch-matched view.

Deprecations
------------

- Deprecated all assignments to ``request.response_*`` attributes (for
  example ``request.response_content_type = 'foo'`` is now deprecated).
  Assignments and mutations of assignable request attributes that were
  considered by the framework for response influence are now deprecated:
  ``response_content_type``, ``response_headerlist``, ``response_status``,
  ``response_charset``, and ``response_cache_for``.  Instead of assigning
  these to the request object for later detection by the rendering machinery,
  users should use the appropriate API of the Response object created by
  accessing ``request.response`` (e.g. code which does
  ``request.response_content_type = 'abc'`` should be changed to
  ``request.response.content_type = 'abc'``).

- Passing view-related parameters to
  ``pyramid.config.Configurator.add_route`` is now deprecated.  Previously, a
  view was permitted to be connected to a route using a set of ``view*``
  parameters passed to the ``add_route`` method of the Configurator.  This
  was a shorthand which replaced the need to perform a subsequent call to
  ``add_view``. For example, it was valid (and often recommended) to do::

     config.add_route('home', '/', view='mypackage.views.myview',
                       view_renderer='some/renderer.pt')

  Passing ``view*`` arguments to ``add_route`` is now deprecated in favor of
  connecting a view to a predefined route via ``Configurator.add_view`` using
  the route's ``route_name`` parameter.  As a result, the above example
  should now be spelled::

     config.add_route('home', '/')
     config.add_view('mypackage.views.myview', route_name='home')
                     renderer='some/renderer.pt')

  This deprecation was done to reduce confusion observed in IRC, as well as
  to (eventually) reduce documentation burden (see also
  https://github.com/Pylons/pyramid/issues/164).  A deprecation warning is
  now issued when any view-related parameter is passed to
  ``Configurator.add_route``.

- Passing an ``environ`` dictionary to the ``__call__`` method of a
  "traverser" (e.g. an object that implements
  ``pyramid.interfaces.ITraverser`` such as an instance of
  ``pyramid.traversal.ResourceTreeTraverser``) as its ``request`` argument
  now causes a deprecation warning to be emitted.  Consumer code should pass a
  ``request`` object instead.  The fact that passing an environ dict is
  permitted has been documentation-deprecated since ``repoze.bfg`` 1.1, and
  this capability will be removed entirely in a future version.

- The following (undocumented, dictionary-like) methods of the
  ``pyramid.request.Request`` object have been deprecated: ``__contains__``,
  ``__delitem__``, ``__getitem__``, ``__iter__``, ``__setitem__``, ``get``,
  ``has_key``, ``items``, ``iteritems``, ``itervalues``, ``keys``, ``pop``,
  ``popitem``, ``setdefault``, ``update``, and ``values``.  Usage of any of
  these methods will cause a deprecation warning to be emitted.  These
  methods were added for internal compatibility in ``repoze.bfg`` 1.1 (code
  that currently expects a request object expected an environ object in BFG
  1.0 and before).  In a future version, these methods will be removed
  entirely.

- Deprecated ``pyramid.view.is_response`` function in favor of (newly-added)
  ``pyramid.request.Request.is_response`` method.  Determining if an object
  is truly a valid response object now requires access to the registry, which
  is only easily available as a request attribute.  The
  ``pyramid.view.is_response`` function will still work until it is removed,
  but now may return an incorrect answer under some (very uncommon)
  circumstances.

Behavior Changes
----------------

- The default Mako renderer is now configured to escape all HTML in
  expression tags. This is intended to help prevent XSS attacks caused by
  rendering unsanitized input from users. To revert this behavior in user's
  templates, they need to filter the expression through the 'n' filter.
  For example, ${ myhtml | n }.
  See https://github.com/Pylons/pyramid/issues/193.

- A custom request factory is now required to return a request object that
  has a ``response`` attribute (or "reified"/lazy property) if they the
  request is meant to be used in a view that uses a renderer.  This
  ``response`` attribute should be an instance of the class
  ``pyramid.response.Response``.

- The JSON and string renderer factories now assign to
  ``request.response.content_type`` rather than
  ``request.response_content_type``.

- Each built-in renderer factory now determines whether it should change the
  content type of the response by comparing the response's content type
  against the response's default content type; if the content type is the
  default content type (usually ``text/html``), the renderer changes the
  content type (to ``application/json`` or ``text/plain`` for JSON and string
  renderers respectively).

- The ``pyramid.wsgi.wsgiapp2`` now uses a slightly different method of
  figuring out how to "fix" ``SCRIPT_NAME`` and ``PATH_INFO`` for the
  downstream application.  As a result, those values may differ slightly from
  the perspective of the downstream application (for example, ``SCRIPT_NAME``
  will now never possess a trailing slash).

- Previously, ``pyramid.request.Request`` inherited from
  ``webob.request.Request`` and implemented ``__getattr__``, ``__setattr__``
  and ``__delattr__`` itself in order to overidde "adhoc attr" WebOb behavior
  where attributes of the request are stored in the environ.  Now,
  ``pyramid.request.Request`` object inherits from (the more recent)
  ``webob.request.BaseRequest`` instead of ``webob.request.Request``, which
  provides the same behavior.  ``pyramid.request.Request`` no longer
  implements its own ``__getattr__``, ``__setattr__`` or ``__delattr__`` as a
  result.

- ``pyramid.response.Response`` is now a *subclass* of
  ``webob.response.Response`` (in order to directly implement the
  ``pyramid.interfaces.IResponse`` interface).

- The "exception response" objects importable from ``pyramid.httpexceptions``
  (e.g. ``HTTPNotFound``) are no longer just import aliases for classes that
  actually live in ``webob.exc``.  Instead, we've defined our own exception
  classes within the module that mirror and emulate the ``webob.exc``
  exception response objects almost entirely.  See the "Design Defense" doc
  section named "Pyramid Uses its Own HTTP Exception Classes" for more
  information.

Backwards Incompatibilities
---------------------------

- Pyramid no longer supports Python 2.4.  Python 2.5 or better is required to
  run Pyramid 1.1+.

- The Pyramid router now, by default, expects response objects returned from
  view callables to implement the ``pyramid.interfaces.IResponse`` interface.
  Unlike the Pyramid 1.0 version of this interface, objects which implement
  IResponse now must define a ``__call__`` method that accepts ``environ``
  and ``start_response``, and which returns an ``app_iter`` iterable, among
  other things.  Previously, it was possible to return any object which had
  the three WebOb ``app_iter``, ``headerlist``, and ``status`` attributes as
  a response, so this is a backwards incompatibility.  It is possible to get
  backwards compatibility back by registering an adapter to IResponse from
  the type of object you're now returning from view callables.  See the
  section in the Hooks chapter of the documentation entitled "Changing How
  Pyramid Treats View Responses".

- The ``pyramid.interfaces.IResponse`` interface is now much more extensive.
  Previously it defined only ``app_iter``, ``status`` and ``headerlist``; now
  it is basically intended to directly mirror the ``webob.Response`` API,
  which has many methods and attributes.

- The ``pyramid.httpexceptions`` classes named ``HTTPFound``,
  ``HTTPMultipleChoices``, ``HTTPMovedPermanently``, ``HTTPSeeOther``,
  ``HTTPUseProxy``, and ``HTTPTemporaryRedirect`` now accept ``location`` as
  their first positional argument rather than ``detail``.  This means that
  you can do, e.g. ``return pyramid.httpexceptions.HTTPFound('http://foo')``
  rather than ``return
  pyramid.httpexceptions.HTTPFound(location='http//foo')`` (the latter will
  of course continue to work).

Dependencies
------------

- Pyramid now depends on WebOb >= 1.0.2 as tests depend on the bugfix in that
  release: "Fix handling of WSGI environs with missing ``SCRIPT_NAME``".
  (Note that in reality, everyone should probably be using 1.0.4 or better
  though, as WebOb 1.0.2 and 1.0.3 were effectively brownbag releases.)

1.0 (2011-01-30)
================

Documentation
-------------

- Fixed bug in ZODB Wiki tutorial (missing dependency on ``docutils`` in
  "models" step within ``setup.py``).

- Removed API documentation for ``pyramid.testing`` APIs named
  ``registerDummySecurityPolicy``, ``registerResources``, ``registerModels``,
  ``registerEventListener``, ``registerTemplateRenderer``,
  ``registerDummyRenderer``, ``registerView``, ``registerUtility``,
  ``registerAdapter``, ``registerSubscriber``, ``registerRoute``,
  and ``registerSettings``.

- Moved "Using ZODB With ZEO" and "Using repoze.catalog Within Pyramid"
  tutorials out of core documentation and into the Pyramid Tutorials site
  (http://docs.pylonsproject.org/projects/pyramid_tutorials/en/latest/).

- Changed "Cleaning up After a Request" section in the URL Dispatch chapter
  to use ``request.add_finished_callback`` instead of jamming an object with
  a ``__del__`` into the WSGI environment.

- Remove duplication of ``add_route`` API documentation from URL Dispatch
  narrative chapter.

- Remove duplication of API and narrative documentation in
  ``pyramid.view.view_config`` API docs by pointing to
  ``pyramid.config.add_view`` documentation and narrative chapter
  documentation.

- Removed some API documentation duplicated in narrative portions of
  documentation 

- Removed "Overall Flow of Authentication" from SQLAlchemy + URL Dispatch
  wiki tutorial due to print space concerns (moved to Pyramid Tutorials
  site).

Bug Fixes
---------

- Deprecated-since-BFG-1.2 APIs from ``pyramid.testing`` now properly emit
  deprecation warnings.

- Added ``egg:repoze.retry#retry`` middleware to the WSGI pipeline in ZODB
  templates (retry ZODB conflict errors which occur in normal operations).

- Removed duplicate implementations of ``is_response``.  Two competing
  implementations existed: one in ``pyramid.config`` and one in
  ``pyramid.view``.  Now the one defined in ``pyramid.view`` is used
  internally by ``pyramid.config`` and continues to be advertised as an API.

1.0b3 (2011-01-28)
==================

Bug Fixes
---------

- Use &copy; instead of copyright symbol in paster templates / tutorial
  templates for the benefit of folks who cutnpaste and save to a non-UTF8
  format.

- ``pyramid.view.append_slash_notfound_view`` now preserves GET query
  parameters across redirects.

Documentation
-------------

- Beef up documentation related to ``set_default_permission``: explicitly
  mention that default permissions also protect exception views.

- Paster templates and tutorials now use spaces instead of tabs in their HTML
  templates.

1.0b2 (2011-01-24)
==================

Bug Fixes
---------

- The ``production.ini`` generated by all paster templates now have an
  effective logging level of WARN, which prevents e.g. SQLAlchemy statement
  logging and other inappropriate output.

- The ``production.ini`` of the ``pyramid_routesalchemy`` and
  ``pyramid_alchemy`` paster templates did not have a ``sqlalchemy`` logger
  section, preventing ``paster serve production.ini`` from working.

- The ``pyramid_routesalchemy`` and ``pyramid_alchemy`` paster templates used
  the ``{{package}}`` variable in a place where it should have used the
  ``{{project}}`` variable, causing applications created with uppercase
  letters e.g. ``paster create -t pyramid_routesalchemy Dibbus`` to fail to
  start when ``paster serve development.ini`` was used against the result.
  See https://github.com/Pylons/pyramid/issues/#issue/107

- The ``render_view`` method of ``pyramid.renderers.RendererHelper`` passed
  an incorrect value into the renderer for ``renderer_info``.  It now passes
  an instance of ``RendererHelper`` instead of a dictionary, which is
  consistent with other usages.  See
  https://github.com/Pylons/pyramid/issues#issue/106

- A bug existed in the ``pyramid.authentication.AuthTktCookieHelper`` which
  would break any usage of an AuthTktAuthenticationPolicy when one was
  configured to reissue its tokens (``reissue_time`` < ``timeout`` /
  ``max_age``). Symptom: ``ValueError: ('Invalid token %r', '')``.  See
  https://github.com/Pylons/pyramid/issues#issue/108.

1.0b1 (2011-01-21)
==================

Features
--------

- The AuthTktAuthenticationPolicy now accepts a ``tokens`` parameter via
  ``pyramid.security.remember``.  The value must be a sequence of strings.
  Tokens are placed into the auth_tkt "tokens" field and returned in the
  auth_tkt cookie.

- Add ``wild_domain`` argument to AuthTktAuthenticationPolicy, which defaults
  to ``True``.  If it is set to ``False``, the feature of the policy which
  sets a cookie with a wildcard domain will be turned off.

- Add a ``MANIFEST.in`` file to each paster template. See
  https://github.com/Pylons/pyramid/issues#issue/95

Bug Fixes
---------

- ``testing.setUp`` now adds a ``settings`` attribute to the registry (both
  when it's passed a registry without any settings and when it creates one).

- The ``testing.setUp`` function now takes a ``settings`` argument, which
  should be a dictionary.  Its values will subsequently be available on the
  returned ``config`` object as ``config.registry.settings``.

Documentation
-------------

- Added "What's New in Pyramid 1.0" chapter to HTML rendering of
  documentation.

- Merged caseman-master narrative editing branch, many wording fixes and
  extensions.

- Fix deprecated example showing ``chameleon_zpt`` API call in testing
  narrative chapter.

- Added "Adding Methods to the Configurator via ``add_directive``" section to
  Advanced Configuration narrative chapter.

- Add docs for ``add_finished_callback``, ``add_response_callback``,
  ``route_path``, ``route_url``, and ``static_url`` methods to
  ``pyramid.request.Request`` API docs.

- Add (minimal) documentation about using I18N within Mako templates to
  "Internationalization and Localization" narrative chapter.

- Move content of "Forms" chapter back to "Views" chapter; I can't think of a
  better place to put it.

- Slightly improved interface docs for ``IAuthorizationPolicy``.

- Minimally explain usage of custom regular expressions in URL dispatch
  replacement markers within URL Dispatch chapter.

Deprecations
-------------

- Using the ``pyramid.view.bfg_view`` alias for ``pyramid.view.view_config``
  (a backwards compatibility shim) now issues a deprecation warning.

Backwards Incompatibilities
---------------------------

- Using ``testing.setUp`` now registers an ISettings utility as a side
  effect.  Some test code which queries for this utility after
  ``testing.setUp`` via queryAdapter will expect a return value of ``None``.
  This code will need to be changed.

- When a ``pyramid.exceptions.Forbidden`` error is raised, its status code
  now ``403 Forbidden``.  It was previously ``401 Unauthorized``, for
  backwards compatibility purposes with ``repoze.bfg``.  This change will
  cause problems for users of Pyramid with ``repoze.who``, which intercepts
  ``401 Unauthorized`` by default, but allows ``403 Forbidden`` to pass
  through.  Those deployments will need to configure ``repoze.who`` to also
  react to ``403 Forbidden``.

- The default value for the ``cookie_on_exception`` parameter to
  ``pyramid.session.UnencryptedCookieSessionFactory`` is now ``True``.  This
  means that when view code causes an exception to be raised, and the session
  has been mutated, a cookie will be sent back in the response.  Previously
  its default value was ``False``.

Paster Templates
----------------

- The ``pyramid_zodb``, ``pyramid_routesalchemy`` and ``pyramid_alchemy``
  paster templates now use a default "commit veto" hook when configuring the
  ``repoze.tm2`` transaction manager in ``development.ini``.  This prevents a
  transaction from being committed when the response status code is within
  the 400 or 500 ranges.  See also
  http://docs.repoze.org/tm2/#using-a-commit-veto.

1.0a10 (2011-01-18)
===================

Bug Fixes
---------

- URL dispatch now properly handles a ``.*`` or ``*`` appearing in a regex
  match when used inside brackets.  Resolves issue #90.

Backwards Incompatibilities
---------------------------

- The ``add_handler`` method of a Configurator has been removed from the
  Pyramid core.  Handlers are now a feature of the ``pyramid_handlers``
  package, which can be downloaded from PyPI.  Documentation for the package
  should be available via
  http://docs.pylonsproject.org/projects/pyramid_handlers/en/latest/,
  which describes how
  to add a configuration statement to your ``main`` block to reobtain this
  method.  You will also need to add an ``install_requires`` dependency upon
  ``pyramid_handlers`` to your ``setup.py`` file.

- The ``load_zcml`` method of a Configurator has been removed from the
  Pyramid core.  Loading ZCML is now a feature of the ``pyramid_zcml``
  package, which can be downloaded from PyPI.  Documentation for the package
  should be available via
  http://docs.pylonsproject.org/projects/pyramid_zcml/en/latest/,
  which describes how
  to add a configuration statement to your ``main`` block to reobtain this
  method.  You will also need to add an ``install_requires`` dependency upon
  ``pyramid_zcml`` to your ``setup.py`` file.

- The ``pyramid.includes`` subpackage has been removed.  ZCML files which use
  include the package ``pyramid.includes`` (e.g. ``<include
  package="pyramid.includes"/>``) now must include the ``pyramid_zcml``
  package instead (e.g. ``<include package="pyramid_zcml"/>``).

- The ``pyramid.view.action`` decorator has been removed from the Pyramid
  core.  Handlers are now a feature of the ``pyramid_handlers`` package.  It
  should now be imported from ``pyramid_handlers`` e.g. ``from
  pyramid_handlers import action``.

- The ``handler`` ZCML directive has been removed.  It is now a feature of
  the ``pyramid_handlers`` package.

- The ``pylons_minimal``, ``pylons_basic`` and ``pylons_sqla`` paster
  templates were removed.  Use ``pyramid_sqla`` (available from PyPI) as a
  generic replacement for Pylons-esque development.

- The ``make_app`` function has been removed from the ``pyramid.router``
  module.  It continues life within the ``pyramid_zcml`` package.  This
  leaves the ``pyramid.router`` module without any API functions.

- The ``configure_zcml`` setting within the deployment settings (within
  ``**settings`` passed to a Pyramid ``main`` function) has ceased to have any
  meaning.

Features
--------

- ``pyramid.testing.setUp`` and ``pyramid.testing.tearDown`` have been
  undeprecated.  They are now the canonical setup and teardown APIs for test
  configuration, replacing "direct" creation of a Configurator.  This is a
  change designed to provide a facade that will protect against any future
  Configurator deprecations.

- Add ``charset`` attribute to ``pyramid.testing.DummyRequest``
  (unconditionally ``UTF-8``).

- Add ``add_directive`` method to configurator, which allows framework
  extenders to add methods to the configurator (ala ZCML directives).

- When ``Configurator.include`` is passed a *module* as an argument, it
  defaults to attempting to find and use a callable named ``includeme``
  within that module.  This makes it possible to use
  ``config.include('some.module')`` rather than
  ``config.include('some.module.somefunc')`` as long as the include function
  within ``some.module`` is named ``includeme``.

- The ``bfg2pyramid`` script now converts ZCML include tags that have
  ``repoze.bfg.includes`` as a package attribute to the value
  ``pyramid_zcml``.  For example, ``<include package="repoze.bfg.includes">``
  will be converted to ``<include package="pyramid_zcml">``.

Paster Templates
----------------

- All paster templates now use ``pyramid.testing.setUp`` and
  ``pyramid.testing.tearDown`` rather than creating a Configurator "by hand"
  within their ``tests.py`` module, as per decision in features above.

- The ``starter_zcml`` paster template has been moved to the ``pyramid_zcml``
  package.

Documentation
-------------

- The wiki and wiki2 tutorials now use ``pyramid.testing.setUp`` and
  ``pyramid.testing.tearDown`` rather than creating a Configurator "by hand",
  as per decision in features above.

- The "Testing" narrative chapter now explains ``pyramid.testing.setUp`` and
  ``pyramid.testing.tearDown`` instead of Configurator creation and
  ``Configurator.begin()`` and ``Configurator.end()``.

- Document the ``request.override_renderer`` attribute within the narrative
  "Renderers" chapter in a section named "Overriding A Renderer at Runtime".

- The "Declarative Configuration" narrative chapter has been removed (it was
  moved to the ``pyramid_zcml`` package).

- Most references to ZCML in narrative chapters have been removed or
  redirected to ``pyramid_zcml`` locations.

Deprecations
------------

- Deprecation warnings related to import of the following API functions were
  added: ``pyramid.traversal.find_model``, ``pyramid.traversal.model_path``,
  ``pyramid.traversal.model_path_tuple``, ``pyramid.url.model_url``.  The
  instructions emitted by the deprecation warnings instruct the developer to
  change these method spellings to their ``resource`` equivalents.  This is a
  consequence of the mass concept rename of "model" to "resource" performed
  in 1.0a7.

1.0a9 (2011-01-08)
==================

Bug Fixes
---------

- The ``proutes`` command tried too hard to resolve the view for printing,
  resulting in exceptions when an exceptional root factory was encountered.
  Instead of trying to resolve the view, if it cannot, it will now just print
  ``<unknown>``.

- The `self` argument was included in new methods of the ``ISession`` interface
  signature, causing ``pyramid_beaker`` tests to fail.

- Readd ``pyramid.traversal.model_path_tuple`` as an alias for
  ``pyramid.traversal.resource_path_tuple`` for backwards compatibility.

Features
--------

- Add a new API ``pyramid.url.current_route_url``, which computes a URL based
  on the "current" route (if any) and its matchdict values.

- ``config.add_view`` now accepts a ``decorator`` keyword argument, a callable
  which will decorate the view callable before it is added to the registry.

- If a handler class provides an ``__action_decorator__`` attribute (usually
  a classmethod or staticmethod), use that as the decorator for each view
  registration for that handler.

- The ``pyramid.interfaces.IAuthenticationPolicy`` interface now specifies an
  ``unauthenticated_userid`` method.  This method supports an important
  optimization required by people who are using persistent storages which do
  not support object caching and whom want to create a "user object" as a
  request attribute.

- A new API has been added to the ``pyramid.security`` module named
  ``unauthenticated_userid``.  This API function calls the
  ``unauthenticated_userid`` method of the effective security policy.

- An ``unauthenticated_userid`` method has been added to the dummy
  authentication policy returned by
  ``pyramid.config.Configurator.testing_securitypolicy``.  It returns the
  same thing as that the dummy authentication policy's
  ``authenticated_userid`` method.

- The class ``pyramid.authentication.AuthTktCookieHelper`` is now an API.
  This class can be used by third-party authentication policy developers to
  help in the mechanics of authentication cookie-setting.

- New constructor argument to Configurator: ``default_view_mapper``.  Useful
  to create systems that have alternate view calling conventions.  A view
  mapper allows objects that are meant to be used as view callables to have
  an arbitrary argument list and an arbitrary result.  The object passed as
  ``default_view_mapper`` should implement the
  ``pyramid.interfaces.IViewMapperFactory`` interface.

- add a ``set_view_mapper`` API to Configurator.  Has
  the same result as passing ``default_view_mapper`` to the Configurator
  constructor.

- ``config.add_view`` now accepts a ``mapper`` keyword argument, which should
  either be ``None``, a string representing a Python dotted name, or an
  object which is an ``IViewMapperFactory``.  This feature is not useful for
  "civilians", only for extension writers.

- Allow static renderer provided during view registration to be overridden at
  request time via a request attribute named ``override_renderer``, which
  should be the name of a previously registered renderer.  Useful to provide
  "omnipresent" RPC using existing rendered views.

- Instances of ``pyramid.testing.DummyRequest`` now have a ``session``
  object, which is mostly a dictionary, but also implements the other session
  API methods for flash and CSRF.

Backwards Incompatibilities
---------------------------

- Since the ``pyramid.interfaces.IAuthenticationPolicy`` interface now
  specifies that a policy implementation must implement an
  ``unauthenticated_userid`` method, all third-party custom authentication
  policies now must implement this method.  It, however, will only be called
  when the global function named ``pyramid.security.unauthenticated_userid``
  is invoked, so if you're not invoking that, you will not notice any issues.

- ``pyramid.interfaces.ISession.get_csrf_token`` now mandates that an
  implementation should return a *new* token if one doesn't already exist in
  the session (previously it would return None).  The internal sessioning
  implementation has been changed.

Documentation
-------------

- The (weak) "Converting a CMF Application to Pyramid" tutorial has been
  removed from the tutorials section.  It was moved to the
  ``pyramid_tutorials`` Github repository.

- The "Resource Location and View Lookup" chapter has been replaced with a
  variant of Rob Miller's "Much Ado About Traversal" (originally published at
  http://blog.nonsequitarian.org/2010/much-ado-about-traversal/).

- Many minor wording tweaks and refactorings (merged Casey Duncan's docs
  fork, in which he is working on general editing).

- Added (weak) description of new view mapper feature to Hooks narrative
  chapter.

- Split views chapter into 2: View Callables and View Configuration.

- Reorder Renderers and Templates chapters after View Callables but before
  View Configuration.

- Merge Session Objects, Cross-Site Request Forgery, and Flash Messaging
  chapter into a single Sessions chapter.

- The Wiki and Wiki2 tutorials now have much nicer CSS and graphics.

Internals
---------

- The "view derivation" code is now factored into a set of classes rather
  than a large number of standalone functions (a side effect of the
  view mapper refactoring).

- The ``pyramid.renderer.RendererHelper`` class has grown a ``render_view``
  method, which is used by the default view mapper (a side effect of the
  view mapper refactoring).

- The object passed as ``renderer`` to the "view deriver" is now an instance
  of ``pyramid.renderers.RendererHelper`` rather than a dictionary (a side
  effect of view mapper refactoring).

- The class used as the "page template" in ``pyramid.chameleon_text`` was
  removed, in preference to using a Chameleon-inbuilt version.

- A view callable wrapper registered in the registry now contains an
  ``__original_view__`` attribute which references the original view callable
  (or class).

- The (non-API) method of all internal authentication policy implementations
  previously named ``_get_userid`` is now named ``unauthenticated_userid``,
  promoted to an API method.  If you were overriding this method, you'll now
  need to override it as ``unauthenticated_userid`` instead.

- Remove (non-API) function of config.py named _map_view.

1.0a8 (2010-12-27)
==================

Bug Fixes
---------

- The name ``registry`` was not available in the ``paster pshell``
  environment under IPython.

Features
--------

- If a resource implements a ``__resource_url__`` method, it will be called
  as the result of invoking the ``pyramid.url.resource_url`` function to
  generate a URL, overriding the default logic.  See the new "Generating The
  URL Of A Resource" section within the Resources narrative chapter.

- Added flash messaging, as described in the "Flash Messaging" narrative
  documentation chapter.

- Added CSRF token generation, as described in the narrative chapter entitled
  "Preventing Cross-Site Request Forgery Attacks".

- Prevent misunderstanding of how the ``view`` and ``view_permission``
  arguments to add_route work by raising an exception during configuration if
  view-related arguments exist but no ``view`` argument is passed.

- Add ``paster proute`` command which displays a summary of the routing
  table.  See the narrative documentation section within the "URL Dispatch"
  chapter entitled "Displaying All Application Routes".

Paster Templates
----------------

- The ``pyramid_zodb`` Paster template no longer employs ZCML.  Instead, it
  is based on scanning.

Documentation
-------------

- Added "Generating The URL Of A Resource" section to the Resources narrative
  chapter (includes information about overriding URL generation using
  ``__resource_url__``).

- Added "Generating the Path To a Resource" section to the Resources
  narrative chapter.

- Added "Finding a Resource by Path" section to the Resources narrative
  chapter.

- Added "Obtaining the Lineage of a Resource" to the Resources narrative
  chapter.

- Added "Determining if a Resource is In The Lineage of Another Resource" to
  Resources narrative chapter.

- Added "Finding the Root Resource" to Resources narrative chapter.

- Added "Finding a Resource With a Class or Interface in Lineage" to
  Resources narrative chapter.

- Added a "Flash Messaging" narrative documentation chapter.

- Added a narrative chapter entitled "Preventing Cross-Site Request Forgery
  Attacks".

- Changed the "ZODB + Traversal Wiki Tutorial" based on changes to
  ``pyramid_zodb`` Paster template.

- Added "Advanced Configuration" narrative chapter which documents how to
  deal with configuration conflicts, two-phase configuration, ``include`` and
  ``commit``.

- Fix API documentation rendering for ``pyramid.view.static``

- Add "Pyramid Provides More Than One Way to Do It" to Design Defense
  documentation.

- Changed "Static Assets" narrative chapter: clarify that ``name`` represents
  a prefix unless it's a URL, added an example of a root-relative static view
  fallback for URL dispatch, added an example of creating a simple view that
  returns the body of a file.

- Move ZCML usage in Hooks chapter to Declarative Configuration chapter.

- Merge "Static Assets" chapter into the "Assets" chapter.

- Added narrative documentation section within the "URL Dispatch" chapter
  entitled "Displaying All Application Routes" (for ``paster proutes``
  command).

1.0a7 (2010-12-20)
==================

Terminology Changes
-------------------

- The Pyramid concept previously known as "model" is now known as "resource".
  As a result:

  - The following API changes have been made::

      pyramid.url.model_url -> 
                        pyramid.url.resource_url

      pyramid.traversal.find_model -> 
                        pyramid.url.find_resource

      pyramid.traversal.model_path ->
                        pyramid.traversal.resource_path

      pyramid.traversal.model_path_tuple ->
                        pyramid.traversal.resource_path_tuple

      pyramid.traversal.ModelGraphTraverser -> 
                        pyramid.traversal.ResourceTreeTraverser

      pyramid.config.Configurator.testing_models ->
                        pyramid.config.Configurator.testing_resources

      pyramid.testing.registerModels ->
                        pyramid.testing.registerResources

      pyramid.testing.DummyModel ->
                        pyramid.testing.DummyResource

   - All documentation which previously referred to "model" now refers to
     "resource".

   - The ``starter`` and ``starter_zcml`` paster templates now have a
     ``resources.py`` module instead of a ``models.py`` module.

  - Positional argument names of various APIs have been changed from
    ``model`` to ``resource``.

  Backwards compatibility shims have been left in place in all cases.  They
  will continue to work "forever".

- The Pyramid concept previously known as "resource" is now known as "asset".
  As a result:

  - The (non-API) module previously known as ``pyramid.resource`` is now
    known as ``pyramid.asset``.

  - All docs that previously referred to "resource specification" now refer
    to "asset specification".

  - The following API changes were made::

      pyramid.config.Configurator.absolute_resource_spec ->
                        pyramid.config.Configurator.absolute_asset_spec

      pyramid.config.Configurator.override_resource ->
                        pyramid.config.Configurator.override_asset

  - The ZCML directive previously known as ``resource`` is now known as
    ``asset``.

  - The setting previously known as ``BFG_RELOAD_RESOURCES`` (envvar) or
    ``reload_resources`` (config file) is now known, respectively, as
    ``PYRAMID_RELOAD_ASSETS`` and ``reload_assets``.

  Backwards compatibility shims have been left in place in all cases.  They
  will continue to work "forever".

Bug Fixes
---------

- Make it possible to successfully run all tests via ``nosetests`` command
  directly (rather than indirectly via ``python setup.py nosetests``).

- When a configuration conflict is encountered during scanning, the conflict
  exception now shows the decorator information that caused the conflict.

Features
--------

- Added ``debug_routematch`` configuration setting that logs matched routes
  (including the matchdict and predicates).

- The name ``registry`` is now available in a ``pshell`` environment by
  default.  It is the application registry object.

Environment
-----------

- All environment variables which used to be prefixed with ``BFG_`` are now
  prefixed with ``PYRAMID_`` (e.g. ``BFG_DEBUG_NOTFOUND`` is now
  ``PYRAMID_DEBUG_NOTFOUND``)

Documentation
-------------

- Added "Debugging Route Matching" section to the urldispatch narrative
  documentation chapter.

- Added reference to ``PYRAMID_DEBUG_ROUTEMATCH`` envvar and ``debug_routematch``
  config file setting to the Environment narrative docs chapter.

- Changed "Project" chapter slightly to expand on use of ``paster pshell``.

- Direct Jython users to Mako rather than Jinja2 in "Install" narrative
  chapter.

- Many changes to support terminological renaming of "model" to "resource"
  and "resource" to "asset".

- Added an example of ``WebTest`` functional testing to the testing narrative
  chapter.

- Rearranged chapter ordering by popular demand (URL dispatch first, then
  traversal).  Put hybrid chapter after views chapter.

- Split off "Renderers" as its own chapter from "Views" chapter in narrative
  documentation.

Paster Templates
----------------

- Added ``debug_routematch = false`` to all paster templates.

Dependencies
------------

- Depend on Venusian >= 0.5 (for scanning conflict exception decoration).

1.0a6 (2010-12-15)
==================

Bug Fixes
---------

- 1.0a5 introduced a bug when ``pyramid.config.Configurator.scan`` was used
  without a ``package`` argument (e.g. ``config.scan()`` as opposed to
  ``config.scan('packagename')``.  The symptoms were: lots of deprecation
  warnings printed to the console about imports of deprecated Pyramid
  functions and classes and non-detection of view callables decorated with
  ``view_config`` decorators.  This has been fixed.

- Tests now pass on Windows (no bugs found, but a few tests in the test suite
  assumed UNIX path segments in filenames).

Documentation
-------------

- If you followed it to-the-letter, the ZODB+Traversal Wiki tutorial would
  instruct you to run a test which would fail because the view callable
  generated by the ``pyramid_zodb`` tutorial used a one-arg view callable,
  but the test in the sample code used a two-arg call.

- Updated ZODB+Traversal tutorial setup.py of all steps to match what's
  generated by ``pyramid_zodb``.

- Fix reference to ``repoze.bfg.traversalwrapper`` in "Models" chapter (point
  at ``pyramid_traversalwrapper`` instead).

1.0a5 (2010-12-14)
==================

Features
--------

- Add a ``handler`` ZCML directive.  This directive does the same thing as
  ``pyramid.configuration.add_handler``.

- A new module named ``pyramid.config`` was added.  It subsumes the duties of
  the older ``pyramid.configuration`` module.

- The new ``pyramid.config.Configurator` class has API methods that the older
  ``pyramid.configuration.Configurator`` class did not: ``with_context`` (a
  classmethod), ``include``, ``action``, and ``commit``.  These methods exist
  for imperative application extensibility purposes.

- The ``pyramid.testing.setUp`` function now accepts an ``autocommit``
  keyword argument, which defaults to ``True``.  If it is passed ``False``,
  the Config object returned by ``setUp`` will be a non-autocommitting Config
  object.

- Add logging configuration to all paster templates.

- ``pyramid_alchemy``, ``pyramid_routesalchemy``, and ``pylons_sqla`` paster
  templates now use idiomatic SQLAlchemy configuration in their respective
  ``.ini`` files and Python code.

- ``pyramid.testing.DummyRequest`` now has a class variable,
  ``query_string``, which defaults to the empty string.

- Add support for json on GAE by catching NotImplementedError and importing
  simplejson from django.utils.

- The Mako renderer now accepts a resource specification for
  ``mako.module_directory``.

- New boolean Mako settings variable ``mako.strict_undefined``.  See `Mako
  Context Variables
  <http://www.makotemplates.org/docs/runtime.html#context-variables>`_ for
  its meaning.

Dependencies
------------

- Depend on Mako 0.3.6+ (we now require the ``strict_undefined`` feature).

Bug Fixes
---------

- When creating a Configurator from within a ``paster pshell`` session, you
  were required to pass a ``package`` argument although ``package`` is not
  actually required.  If you didn't pass ``package``, you would receive an
  error something like ``KeyError: '__name__'`` emanating from the
  ``pyramid.path.caller_module`` function.  This has now been fixed.

- The ``pyramid_routesalchemy`` paster template's unit tests failed
  (``AssertionError: 'SomeProject' != 'someproject'``).  This is fixed.

- Make default renderer work (renderer factory registered with no name, which
  is active for every view unless the view names a specific renderer).

- The Mako renderer did not properly turn the ``mako.imports``,
  ``mako.default_filters``, and ``mako.imports`` settings into lists.

- The Mako renderer did not properly convert the ``mako.error_handler``
  setting from a dotted name to a callable.

Documentation
-------------

- Merged many wording, readability, and correctness changes to narrative
  documentation chapters from https://github.com/caseman/pyramid (up to and
  including "Models" narrative chapter).

- "Sample Applications" section of docs changed to note existence of Cluegun,
  Shootout and Virginia sample applications, ported from their repoze.bfg
  origin packages.

- SQLAlchemy+URLDispatch tutorial updated to integrate changes to
  ``pyramid_routesalchemy`` template.

- Add ``pyramid.interfaces.ITemplateRenderer`` interface to Interfaces API
  chapter (has ``implementation()`` method, required to be used when getting
  at Chameleon macros).

- Add a "Modifying Package Structure" section to the project narrative
  documentation chapter (explain turning a module into a package).

- Documentation was added for the new ``handler`` ZCML directive in the ZCML
  section.

Deprecations
------------

- ``pyramid.configuration.Configurator`` is now deprecated.  Use
  ``pyramid.config.Configurator``, passing its constructor
  ``autocommit=True`` instead.  The ``pyramid.configuration.Configurator``
  alias will live for a long time, as every application uses it, but its
  import now issues a deprecation warning.  The
  ``pyramid.config.Configurator`` class has the same API as
  ``pyramid.configuration.Configurator`` class, which it means to replace,
  except by default it is a *non-autocommitting* configurator. The
  now-deprecated ``pyramid.configuration.Configurator`` will autocommit every
  time a configuration method is called.

  The ``pyramid.configuration`` module remains, but it is deprecated.  Use
  ``pyramid.config`` instead.

1.0a4 (2010-11-21)
==================

Features
--------

- URL Dispatch now allows for replacement markers to be located anywhere
  in the pattern, instead of immediately following a ``/``.

- URL Dispatch now uses the form ``{marker}`` to denote a replace marker in
  the route pattern instead of ``:marker``. The old colon-style marker syntax
  is still accepted for backwards compatibility. The new format allows a
  regular expression for that marker location to be used instead of the
  default ``[^/]+``, for example ``{marker:\d+}`` is now valid to require the
  marker to be digits.

- Add a ``pyramid.url.route_path`` API, allowing folks to generate relative
  URLs.  Calling ``route_path`` is the same as calling
  ``pyramid.url.route_url`` with the argument ``_app_url`` equal to the empty
  string.

- Add a ``pyramid.request.Request.route_path`` API.  This is a convenience
  method of the request which calls ``pyramid.url.route_url``.

- Make test suite pass on Jython (requires PasteScript trunk, presumably to
  be 1.7.4).

- Make test suite pass on PyPy (Chameleon doesn't work).

- Surrounding application configuration with ``config.begin()`` and
  ``config.end()`` is no longer necessary.  All paster templates have been
  changed to no longer call these functions.

- Fix configurator to not convert ``ImportError`` to ``ConfigurationError``
  if the import that failed was unrelated to the import requested via a
  dotted name when resolving dotted names (such as view dotted names).

Documentation
-------------

- SQLAlchemy+URLDispatch and ZODB+Traversal tutorials have been updated to
  not call ``config.begin()`` or ``config.end()``.

Bug Fixes
---------

- Add deprecation warnings to import of ``pyramid.chameleon_text`` and
  ``pyramid.chameleon_zpt`` of ``get_renderer``, ``get_template``,
  ``render_template``, and ``render_template_to_response``.

- Add deprecation warning for import of ``pyramid.zcml.zcml_configure`` and
  ``pyramid.zcml.file_configure``.

- The ``pyramid_alchemy`` paster template had a typo, preventing an import
  from working.

- Fix apparent failures when calling ``pyramid.traversal.find_model(root,
  path)`` or ``pyramid.traversal.traverse(path)`` when ``path`` is
  (erroneously) a Unicode object. The user is meant to pass these APIs a
  string object, never a Unicode object.  In practice, however, users indeed
  pass Unicode.  Because the string that is passed must be ASCII encodeable,
  now, if they pass a Unicode object, its data is eagerly converted to an
  ASCII string rather than being passed along to downstream code as a
  convenience to the user and to prevent puzzling second-order failures from
  cropping up (all failures will occur within ``pyramid.traversal.traverse``
  rather than later down the line as the result of calling e.g.
  ``traversal_path``).

Backwards Incompatibilities
---------------------------

- The ``pyramid.testing.zcml_configure`` API has been removed.  It had been
  advertised as removed since repoze.bfg 1.2a1, but hadn't actually been.

Deprecations
------------

- The ``pyramid.settings.get_settings`` API is now deprecated.  Use
  ``pyramid.threadlocals.get_current_registry().settings`` instead or use the
  ``settings`` attribute of the registry available from the request
  (``request.registry.settings``).

Documentation
-------------

- Removed ``zodbsessions`` tutorial chapter.  It's still useful, but we now
  have a SessionFactory abstraction which competes with it, and maintaining
  documentation on both ways to do it is a distraction.

Internal
--------

- Replace Twill with WebTest in internal integration tests (avoid deprecation
  warnings generated by Twill).

1.0a3 (2010-11-16)
==================

Features
--------

- Added Mako TemplateLookup settings for ``mako.error_handler``,
  ``mako.default_filters``, and ``mako.imports``.

- Normalized all paster templates: each now uses the name ``main`` to
  represent the function that returns a WSGI application, each now uses
  WebError, each now has roughly the same shape of development.ini style.

- Added class vars ``matchdict`` and ``matched_route`` to
  ``pyramid.request.Request``.  Each is set to ``None``.

- New API method: ``pyramid.settings.asbool``.

- New API methods for ``pyramid.request.Request``: ``model_url``,
  ``route_url``, and ``static_url``.  These are simple passthroughs for their
  respective functions in ``pyramid.url``.

- The ``settings`` object which used to be available only when
  ``request.settings.get_settings`` was called is now available as
  ``registry.settings`` (e.g. ``request.registry.settings`` in view code).

Bug Fixes
---------

- The pylons_* paster templates erroneously used the ``{squiggly}`` routing
  syntax as the pattern supplied to ``add_route``.  This style of routing is
  not supported.  They were replaced with ``:colon`` style route patterns.

- The pylons_* paster template used the same string
  (``your_app_secret_string``) for the ``session.secret`` setting in the
  generated ``development.ini``.  This was a security risk if left unchanged
  in a project that used one of the templates to produce production
  applications.  It now uses a randomly generated string.

Documentation
-------------

- ZODB+traversal wiki (``wiki``) tutorial updated due to changes to
  ``pyramid_zodb`` paster template.

- SQLAlchemy+urldispach wiki (``wiki2``) tutorial updated due to changes to
  ``pyramid_routesalchemy`` paster template.

- Documented the ``matchdict`` and ``matched_route`` attributes of the
  request object in the Request API documentation.

Deprecations
------------

- Obtaining the ``settings`` object via
  ``registry.{get|query}Utility(ISettings)`` is now deprecated.  Instead,
  obtain the ``settings`` object via the ``registry.settings`` attribute.  A
  backwards compatibility shim was added to the registry object to register
  the settings object as an ISettings utility when ``setattr(registry,
  'settings', foo)`` is called, but it will be removed in a later release.

- Obtaining the ``settings`` object via ``pyramid.settings.get_settings`` is
  now deprecated.  Obtain it as the ``settings`` attribute of the registry
  now (obtain the registry via ``pyramid.threadlocal.get_registry`` or as
  ``request.registry``).

Behavior Differences
--------------------

- Internal: ZCML directives no longer call get_current_registry() if there's
  a ``registry`` attribute on the ZCML context (kill off use of
  threadlocals).

- Internal: Chameleon template renderers now accept two arguments: ``path``
  and ``lookup``.  ``Lookup`` will be an instance of a lookup class which
  supplies (late-bound) arguments for debug, reload, and translate.  Any
  third-party renderers which use (the non-API) function
  ``pyramid.renderers.template_renderer_factory`` will need to adjust their
  implementations to obey the new callback argument list.  This change was to
  kill off inappropriate use of threadlocals.

1.0a2 (2010-11-09)
==================

Documentation
-------------

- All references to events by interface
  (e.g. ``pyramid.interfaces.INewRequest``) have been changed to reference
  their concrete classes (e.g. ``pyramid.events.NewRequest``) in
  documentation about making subscriptions.

- All references to Pyramid-the-application were changed from mod-`pyramid`
  to app-`Pyramid`.  A custom role setting was added to ``docs/conf.py`` to
  allow for this.  (internal)

1.0a1 (2010-11-05)
==================

Features (delta from BFG 1.3)
-------------------------------

- Mako templating renderer supports resource specification format for
  template lookups and within Mako templates. Absolute filenames must
  be used in Pyramid to avoid this lookup process.

- Add ``pyramid.httpexceptions`` module, which is a facade for the
  ``webob.exc`` module.

- Direct built-in support for the Mako templating language.

- A new configurator method exists: ``add_handler``.  This method adds
  a Pylons-style "view handler" (such a thing used to be called a
  "controller" in Pylons 1.0).

- New argument to configurator: ``session_factory``.

- New method on configurator: ``set_session_factory``

- Using ``request.session`` now returns a (dictionary-like) session
  object if a session factory has been configured.

- The request now has a new attribute: ``tmpl_context`` for benefit of
  Pylons users.

- The decorator previously known as ``pyramid.view.bfg_view`` is now
  known most formally as ``pyramid.view.view_config`` in docs and
  paster templates.  An import of ``pyramid.view.bfg_view``, however,
  will continue to work "forever".

- New API methods in ``pyramid.session``: ``signed_serialize`` and
  ``signed_deserialize``.

- New interface: ``pyramid.interfaces.IRendererInfo``.  An object of this type
  is passed to renderer factory constructors (see "Backwards
  Incompatibilities").

- New event type: ``pyramid.interfaces.IBeforeRender``.  An object of this type
  is sent as an event before a renderer is invoked (but after the
  application-level renderer globals factory added via
  ``pyramid.configurator.configuration.set_renderer_globals_factory``, if any,
  has injected its own keys).  Applications may now subscribe to the
  ``IBeforeRender`` event type in order to introspect the and modify the set of
  renderer globals before they are passed to a renderer.  The event object
  iself has a dictionary-like interface that can be used for this purpose.  For
  example::

    from repoze.events import subscriber
    from pyramid.interfaces import IRendererGlobalsEvent

    @subscriber(IRendererGlobalsEvent)
    def add_global(event):
        event['mykey'] = 'foo'

  If a subscriber attempts to add a key that already exist in the renderer
  globals dictionary, a ``KeyError`` is raised.  This limitation is due to the
  fact that subscribers cannot be ordered relative to each other.  The set of
  keys added to the renderer globals dictionary by all subscribers and
  app-level globals factories must be unique.

- New class: ``pyramid.response.Response``.  This is a pure facade for
  ``webob.Response`` (old code need not change to use this facade, it's
  existence is mostly for vanity and documentation-generation purposes).

- All preexisting paster templates (except ``zodb``) now use "imperative"
  configuration (``starter``, ``routesalchemy``, ``alchemy``).

- A new paster template named ``pyramid_starter_zcml`` exists, which uses
  declarative configuration.

Documentation (delta from BFG 1.3)
-----------------------------------

- Added a ``pyramid.httpexceptions`` API documentation chapter.

- Added a ``pyramid.session`` API documentation chapter.

- Added a ``Session Objects`` narrative documentation chapter.

- Added an API chapter for the ``pyramid.personality`` module.

- Added an API chapter for the ``pyramid.response`` module.

- All documentation which previously referred to ``webob.Response`` now uses
  ``pyramid.response.Response`` instead.

- The documentation has been overhauled to use imperative configuration,
  moving declarative configuration (ZCML) explanations to a separate
  narrative chapter ``declarative.rst``.

- The ZODB Wiki tutorial was updated to take into account changes to the
  ``pyramid_zodb`` paster template.

- The SQL Wiki tutorial was updated to take into account changes to the
  ``pyramid_routesalchemy`` paster template.

Backwards Incompatibilities (with BFG 1.3)
------------------------------------------

- There is no longer an ``IDebugLogger`` registered as a named utility
  with the name ``repoze.bfg.debug``.

- The logger which used to have the name of ``repoze.bfg.debug`` now
  has the name ``pyramid.debug``.

- The deprecated API ``pyramid.testing.registerViewPermission``
  has been removed.

- The deprecated API named ``pyramid.testing.registerRoutesMapper``
  has been removed.

- The deprecated API named ``pyramid.request.get_request`` was removed.

- The deprecated API named ``pyramid.security.Unauthorized`` was
  removed.

- The deprecated API named ``pyramid.view.view_execution_permitted``
  was removed.

- The deprecated API named ``pyramid.view.NotFound`` was removed.

- The ``bfgshell`` paster command is now named ``pshell``.

- The Venusian "category" for all built-in Venusian decorators
  (e.g. ``subscriber`` and ``view_config``/``bfg_view``) is now
  ``pyramid`` instead of ``bfg``.

- ``pyramid.renderers.rendered_response`` function removed; use
  ``render_pyramid.renderers.render_to_response`` instead.

- Renderer factories now accept a *renderer info object* rather than an
  absolute resource specification or an absolute path.  The object has the
  following attributes: ``name`` (the ``renderer=`` value), ``package`` (the
  'current package' when the renderer configuration statement was found),
  ``type``: the renderer type, ``registry``: the current registry, and
  ``settings``: the deployment settings dictionary.

  Third-party ``repoze.bfg`` renderer implementations that must be ported to
  Pyramid will need to account for this.

  This change was made primarily to support more flexible Mako template
  rendering.

- The presence of the key ``repoze.bfg.message`` in the WSGI environment when
  an exception occurs is now deprecated.  Instead, code which relies on this
  environ value should use the ``exception`` attribute of the request
  (e.g. ``request.exception[0]``) to retrieve the message.

- The values ``bfg_localizer`` and ``bfg_locale_name`` kept on the request
  during internationalization for caching purposes were never APIs.  These
  however have changed to ``localizer`` and ``locale_name``, respectively.

- The default ``cookie_name`` value of the ``authtktauthenticationpolicy`` ZCML
  now defaults to ``auth_tkt`` (it used to default to ``repoze.bfg.auth_tkt``).

- The default ``cookie_name`` value of the
  ``pyramid.authentication.AuthTktAuthenticationPolicy`` constructor now
  defaults to ``auth_tkt`` (it used to default to ``repoze.bfg.auth_tkt``).

- The ``request_type`` argument to the ``view`` ZCML directive, the
  ``pyramid.configuration.Configurator.add_view`` method, or the
  ``pyramid.view.view_config`` decorator (nee ``bfg_view``) is no longer
  permitted to be one of the strings ``GET``, ``HEAD``, ``PUT``, ``POST`` or
  ``DELETE``, and now must always be an interface.  Accepting the
  method-strings as ``request_type`` was a backwards compatibility strategy
  servicing repoze.bfg 1.0 applications.  Use the ``request_method``
  parameter instead to specify that a view a string request-method predicate.

