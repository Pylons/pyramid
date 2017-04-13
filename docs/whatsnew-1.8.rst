What's New in Pyramid 1.8
=========================

This article explains the new features in :app:`Pyramid` version 1.8 as
compared to its predecessor, :app:`Pyramid` 1.7. It also documents backwards
incompatibilities between the two versions and deprecations added to
:app:`Pyramid` 1.8, as well as software dependency changes and notable
documentation additions.

Major Feature Additions
-----------------------

- Added :meth:`pyramid.config.Configurator.add_exception_view` and the
  :func:`pyramid.view.exception_view_config` decorator. It is now possible
  using these methods or via the new ``exception_only=True`` option to
  :meth:`pyramid.config.Configurator.add_view` to add a view which will only
  be matched when handling an exception. Previously, any exception views were
  also registered for a traversal context that inherited from the exception
  class which prevented any exception-only optimizations.
  See https://github.com/Pylons/pyramid/pull/2660

- ``pserve --reload`` now uses the
  `hupper <http://docs.pylonsproject.org/projects/hupper/en/latest/>`_
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

Minor Feature Additions
-----------------------

- Python 3.6 compatibility.
  https://github.com/Pylons/pyramid/issues/2835

- The ``_get_credentials`` private method of
  :class:`pyramid.authentication.BasicAuthAuthenticationPolicy`
  has been extracted into standalone function
  :func:`pyramid.authentication.extract_http_basic_credentials`, this function
  extracts HTTP Basic credentials from a ``request`` object, and returns them
  as a named tuple. See https://github.com/Pylons/pyramid/pull/2662

- Pyramid 1.4 silently dropped a feature of the configurator that has been
  restored. It's again possible for action discriminators to conflict across
  different action orders.
  See https://github.com/Pylons/pyramid/pull/2757

- :func:`pyramid.paster.bootstrap` and its sibling
  :func:`pyramid.scripting.prepare` can now be used as context managers to
  automatically invoke the ``closer`` and pop threadlocals off of the stack
  to prevent memory leaks. See https://github.com/Pylons/pyramid/pull/2760

- Added the ``exception_only`` boolean to
  :class:`pyramid.interfaces.IViewDeriverInfo` which can be used by view
  derivers to determine if they are wrapping a view which only handles
  exceptions. This means that it is no longer necessary to perform request-time
  checks for ``request.exception`` to determine if the view is handling an
  exception - the pipeline can be optimized at config-time.
  See https://github.com/Pylons/pyramid/pull/2660

- ``pcreate`` learned about ``--package-name`` to allow you to create a new
  project in an existing folder with a different package name than the project
  name. See https://github.com/Pylons/pyramid/pull/2783

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

- A new ``[pserve]`` section is supported in your config files with a
  ``watch_files`` key that can configure ``pserve --reload`` to monitor custom
  file paths. See https://github.com/Pylons/pyramid/pull/2827

- Allow streaming responses to be made from subclasses of
  :class:`pyramid.httpexceptions.HTTPException`. Previously the response would
  be unrolled while testing for a body, making it impossible to stream
  a response.
  See https://github.com/Pylons/pyramid/pull/2863

- Update starter, alchemy and zodb scaffolds to support IPv6 by using the
  new ``listen`` directives in waitress.
  See https://github.com/Pylons/pyramid/pull/2853

- All p* scripts now use argparse instead of optparse. This improves their
  ``--help`` output as well as enabling nicer documentation of their options.
  See https://github.com/Pylons/pyramid/pull/2864

- Added an ``override`` option to
  :meth:`pyramid.config.Configurator.add_translation_dirs` to allow
  later calls to place translation directories at a higher priority then
  earlier calls. See https://github.com/Pylons/pyramid/pull/2902

- Added a new ``callback`` option to
  :meth:`pyramid.config.Configurator.set_default_csrf_options`` which
  can be used to determine per-request whether CSRF checking should be enabled
  to allow for a mix authentication methods. Only cookie-based methods
  generally require CSRF checking.
  See https://github.com/Pylons/pyramid/pull/2778

Backwards Incompatibilities
---------------------------

- Following the Pyramid deprecation period (1.6 -> 1.8),
  daemon support for pserve has been removed. This includes removing the
  daemon commands (start, stop, restart, status) as well as the following
  arguments: ``--daemon``, ``--pid-file``, ``--log-file``,
  ``--monitor-restart``, ``--status``, ``--user``, ``--group``,
  ``--stop-daemon``

  To run your server as a daemon you should use a process manager instead of
  pserve.

  See https://github.com/Pylons/pyramid/pull/2615

- Change static view to avoid setting the ``Content-Encoding`` response header
  to an encoding guessed using Python's ``mimetypes`` module. This was causing
  clients to decode the content of gzipped files when downloading them. The
  client would end up with a ``foo.txt.gz`` file on disk that was already
  decoded, thus should really be ``foo.txt``. Also, the ``Content-Encoding``
  should only have been used if the client itself broadcast support for the
  encoding via ``Accept-Encoding`` request headers.
  See https://github.com/Pylons/pyramid/pull/2810

- ``pcreate`` is now interactive by default. You will be prompted if a file
  already exists with different content. Previously if there were similar
  files it would silently skip them unless you specified ``--interactive``
  or ``--overwrite``.
  See https://github.com/Pylons/pyramid/pull/2775

- Support for the ``IContextURL`` interface that was deprecated in Pyramid 1.3
  has been removed.  See https://github.com/Pylons/pyramid/pull/2822

- Settings are no longer accessible as attributes on the settings object
  (e.g. ``request.registry.settings.foo``). This was deprecated in Pyramid 1.2.
  See https://github.com/Pylons/pyramid/pull/2823

- Removed undocumented argument ``cachebust_match`` from
  ``pyramid.static.static_view``. This argument was shipped accidentally
  in Pyramid 1.6. See https://github.com/Pylons/pyramid/pull/2681

Deprecations
------------

- The ``pcreate`` script and the core scaffolds (``starter``, ``alchemy`` and
  ``zodb``) have been deprecated.

  They have been replaced with the decision to embrace the popular
  `cookiecutter <https://cookiecutter.readthedocs.io/en/latest/>`_ project
  as a best-of-breed project templating solution.

  ``pcreate`` was originally introduced when very few alternatives existed
  that supported Python 3. Fortunately the situation has improved and
  with possible tooling support for cookiecutters being discussed by major
  IDEs, and the simplicity of the jinja2 syntax, it is exciting to embrace
  the project moving forward!

  All of Pyramid's official scaffolds as well as the tutorials have been
  ported to cookiecutters:

  - `pyramid-cookiecutter-starter
    <https://github.com/Pylons/pyramid-cookiecutter-starter>`_

  - `pyramid-cookiecutter-alchemy
    <https://github.com/Pylons/pyramid-cookiecutter-alchemy>`_

  - `pyramid-cookiecutter-zodb
    <https://github.com/Pylons/pyramid-cookiecutter-zodb>`_

  See https://github.com/Pylons/pyramid/pull/2780

Documentation Enhancements
--------------------------

- Update Typographical Conventions.
  https://github.com/Pylons/pyramid/pull/2838

- Add `pyramid_nacl_session
  <http://docs.pylonsproject.org/projects/pyramid-nacl-session/en/latest/>`_
  to session factories. See https://github.com/Pylons/pyramid/issues/2791

- Update HACKING.txt from stale branch that was never merged to master.
  See https://github.com/Pylons/pyramid/pull/2782

- Updated Windows installation instructions and related bits.
  See https://github.com/Pylons/pyramid/issues/2661

- Fix an inconsistency in the documentation between view predicates and
  route predicates and highlight the differences in their APIs.
  See https://github.com/Pylons/pyramid/pull/2764

- Clarify a possible misuse of the ``headers`` kwarg to subclasses of
  :class:`pyramid.httpexceptions.HTTPException` in which more appropriate
  kwargs from the parent class :class:`pyramid.response.Response` should be
  used instead. See https://github.com/Pylons/pyramid/pull/2750

- The SQLAlchemy + URL Dispatch + Jinja2 (``wiki2``) and
  ZODB + Traversal + Chameleon (``wiki``) tutorials have been updated to
  utilize the new cookiecutters and drop support for the ``pcreate``
  scaffolds.

  See https://github.com/Pylons/pyramid/pull/2881 and
  https://github.com/Pylons/pyramid/pull/2883.

- Quick Tour, Quick Tutorial, and most files throughout the documentation have
  been updated to use cookiecutters instead of pcreate and scaffolds.
  See https://github.com/Pylons/pyramid/pull/2888 and
  https://github.com/Pylons/pyramid/pull/2889

- Updated the ``mod_wsgi`` tutorial to use cookiecutters and Apache 2.4+.
  See https://github.com/Pylons/pyramid/pull/2901
