What's New In Pyramid 1.6
=========================

This article explains the new features in :app:`Pyramid` version 1.6 as
compared to its predecessor, :app:`Pyramid` 1.5.  It also documents backwards
incompatibilities between the two versions and deprecations added to
:app:`Pyramid` 1.6, as well as software dependency changes and notable
documentation additions.

Backwards Incompatibilities
---------------------------

- ``request.response`` will no longer be mutated when using the
  :func:`~pyramid.renderers.render_to_response` API.  It is now necessary 
  to pass in
  a ``response=`` argument to :func:`~pyramid.renderers.render_to_response` if
  you wish to supply the renderer with a custom response object for it to
  use. If you do not pass one then a response object will be created using the
  current response factory. Almost all renderers mutate the
  ``request.response`` response object (for example, the JSON renderer sets
  ``request.response.content_type`` to ``application/json``).  However, when
  invoking ``render_to_response`` it is not expected that the response object
  being returned would be the same one used later in the request. The response
  object returned from ``render_to_response`` is now explicitly different from
  ``request.response``. This does not change the API of a renderer. See
  https://github.com/Pylons/pyramid/pull/1563


Feature Additions
-----------------

- Cache busting for static assets has been added and is available via a new
  argument to :meth:`pyramid.config.Configurator.add_static_view`:
  ``cachebust``.  Core APIs are shipped for both cache busting via query
  strings and path segments and may be extended to fit into custom asset
  pipelines.  See https://github.com/Pylons/pyramid/pull/1380 and
  https://github.com/Pylons/pyramid/pull/1583

- Assets can now be overidden by an absolute path on the filesystem when using
  the :meth:`~pyramid.config.Configurator.override_asset` API. This makes it
  possible to fully support serving up static content from a mutable directory
  while still being able to use the :meth:`~pyramid.request.Request.static_url`
  API and :meth:`~pyramid.config.Configurator.add_static_view`.  Previously it
  was not possible to use :meth:`~pyramid.config.Configurator.add_static_view`
  with an absolute path **and** generate urls to the content. This change
  replaces the call, ``config.add_static_view('/abs/path', 'static')``, with
  ``config.add_static_view('myapp:static', 'static')`` and
  ``config.override_asset(to_override='myapp:static/',
  override_with='/abs/path/')``. The ``myapp:static`` asset spec is completely
  made up and does not need to exist - it is used for generating urls via
  ``request.static_url('myapp:static/foo.png')``.  See
  https://github.com/Pylons/pyramid/issues/1252

- Added :meth:`~pyramid.config.Configurator.set_response_factory` and the
  ``response_factory`` keyword argument to the constructor of
  :class:`~pyramid.config.Configurator` for defining a factory that will return
  a custom ``Response`` class.  See https://github.com/Pylons/pyramid/pull/1499

- Add :attr:`pyramid.config.Configurator.root_package` attribute and init
  parameter to assist with includeable packages that wish to resolve
  resources relative to the package in which the configurator was created.
  This is especially useful for addons that need to load asset specs from
  settings, in which case it is may be natural for a developer to define
  imports or assets relative to the top-level package.
  See https://github.com/Pylons/pyramid/pull/1337

- Overall improvments for the ``proutes`` command. Added ``--format`` and
  ``--glob`` arguments to the command, introduced the ``method``
  column for displaying available request methods, and improved the ``view``
  output by showing the module instead of just ``__repr__``.
  See https://github.com/Pylons/pyramid/pull/1488

- ``pserve`` can now take a ``-b`` or ``--browser`` option to open the server
  URL in a web browser. See https://github.com/Pylons/pyramid/pull/1533

- Support keyword-only arguments and function annotations in views in
  Python 3. See https://github.com/Pylons/pyramid/pull/1556

- The ``append_slash`` argument of
  :meth:`~pyramid.config.Configurator.add_notfound_view()` will now accept
  anything that implements the :class:`~pyramid.interfaces.IResponse` interface
  and will use that as the response class instead of the default
  :class:`~pyramid.httpexceptions.HTTPFound`.  See
  https://github.com/Pylons/pyramid/pull/1610

- The :class:`~pyramid.config.Configurator` has grown the ability to allow
  actions to call other actions during a commit-cycle. This enables much more
  logic to be placed into actions, such as the ability to invoke other actions
  or group them for improved conflict detection. We have also exposed and
  documented the config phases that Pyramid uses in order to further assist in
  building conforming addons.  See https://github.com/Pylons/pyramid/pull/1513

- Allow an iterator to be returned from a renderer. Previously it was only
  possible to return bytes or unicode.
  See https://github.com/Pylons/pyramid/pull/1417

- Improve robustness to timing attacks in the
  :class:`~pyramid.authentication.AuthTktCookieHelper` and the
  :class:`~pyramid.session.SignedCookieSessionFactory` classes by using the
  stdlib's ``hmac.compare_digest`` if it is available (such as Python 2.7.7+ and
  3.3+).  See https://github.com/Pylons/pyramid/pull/1457

- Improve the readability of the ``pcreate`` shell script output.
  See https://github.com/Pylons/pyramid/pull/1453

- Make it simple to define notfound and forbidden views that wish to use the
  default exception-response view but with altered predicates and other
  configuration options. The ``view`` argument is now optional in
  :meth:`~pyramid.config.Configurator.add_notfound_view` and
  :meth:`~pyramid.config.Configurator.add_forbidden_view` See
  https://github.com/Pylons/pyramid/issues/494

- The ``pshell`` script will now load a ``PYTHONSTARTUP`` file if one is
  defined in the environment prior to launching the interpreter.
  See https://github.com/Pylons/pyramid/pull/1448

- Add new HTTP exception objects for status codes
  ``428 Precondition Required``, ``429 Too Many Requests`` and
  ``431 Request Header Fields Too Large`` in ``pyramid.httpexceptions``.
  See https://github.com/Pylons/pyramid/pull/1372/files

- ``pcreate`` when run without a scaffold argument will now print information
  on the missing flag, as well as a list of available scaffolds.  See
  https://github.com/Pylons/pyramid/pull/1566 and
  https://github.com/Pylons/pyramid/issues/1297

- Add :func:`pyramid.request.apply_request_extensions` function which can be
  used in testing to apply any request extensions configured via
  ``config.add_request_method``. Previously it was only possible to test the
  extensions by going through Pyramid's router.  See
  https://github.com/Pylons/pyramid/pull/1581


- Make it possible to subclass ``pyramid.request.Request`` and also use
  ``pyramid.request.Request.add_request.method``.  See
  https://github.com/Pylons/pyramid/issues/1529

Deprecations
------------

- The ``principal`` argument to :func:`pyramid.security.remember` was renamed
  to ``userid``.  Using ``principal`` as the argument name still works and will
  continue to work for the next few releases, but a deprecation warning is
  printed.


Scaffolding Enhancements
------------------------

- Added line numbers to the log formatters in the scaffolds to assist with
  debugging. See https://github.com/Pylons/pyramid/pull/1326

- Update scaffold generating machinery to return the version of pyramid and
  pyramid docs for use in scaffolds. Updated ``starter``, ``alchemy`` and
  ``zodb`` templates to have links to correctly versioned documentation and
  reflect which pyramid was used to generate the scaffold.

- Removed non-ascii copyright symbol from templates, as this was
  causing the scaffolds to fail for project generation.

Documentation Enhancements
--------------------------

- Removed logging configuration from Quick Tutorial ini files except for
  scaffolding- and logging-related chapters to avoid needing to explain it too
  early.

- Improve and clarify the documentation on what Pyramid defines as a
  ``principal`` and a ``userid`` in its security APIs.
  See https://github.com/Pylons/pyramid/pull/1399
