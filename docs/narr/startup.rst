.. _startup_chapter:

Startup
=======

When you cause a :app:`Pyramid` application to start up in a console window,
you'll see something much like this show up on the console:

.. code-block:: bash

    $ $VENV/bin/pserve development.ini
    Starting server in PID 16305.
    Serving on http://localhost:6543
    Serving on http://localhost:6543

This chapter explains what happens between the time you press the "Return" key
on your keyboard after typing ``pserve development.ini`` and the time the lines
``Serving on http://localhost:6543`` are output to your console.

.. index::
   single: startup process
   pair: settings; .ini

The Startup Process
-------------------

The easiest and best-documented way to start and serve a :app:`Pyramid`
application is to use the ``pserve`` command against a :term:`PasteDeploy`
``.ini`` file.  This uses the ``.ini`` file to infer settings and starts a
server listening on a port.  For the purposes of this discussion, we'll assume
that you are using this command to run your :app:`Pyramid` application.

Here's a high-level time-ordered overview of what happens when you press
``return`` after running ``pserve development.ini``.

#. The ``pserve`` command is invoked under your shell with the argument
   ``development.ini``.  As a result, Pyramid recognizes that it is meant to
   begin to run and serve an application using the information contained
   within the ``development.ini`` file.

#. ``pserve`` passes the ``development.ini`` path to :term:`plaster` which
   finds an available configuration loader that recognizes the ``ini`` format.

#. :term:`plaster` finds the ``plaster_pastedeploy`` library which binds
   the :term:`PasteDeploy` library and returns a parser that can understand
   the format.

#. The :term:`PasteDeploy` finds a section named either ``[app:main]``,
   ``[pipeline:main]``, or ``[composite:main]`` in the ``.ini`` file.  This
   section represents the configuration of a :term:`WSGI` application that will
   be served.  If you're using a simple application (e.g., ``[app:main]``), the
   application's ``paste.app_factory`` :term:`entry point` will be named on the
   ``use=`` line within the section's configuration.  If instead of a simple
   application, you're using a WSGI :term:`pipeline` (e.g., a
   ``[pipeline:main]`` section), the application named on the "last" element
   will refer to your :app:`Pyramid` application.  If instead of a simple
   application or a pipeline, you're using a "composite" (e.g.,
   ``[composite:main]``), refer to the documentation for that particular
   composite to understand how to make it refer to your :app:`Pyramid`
   application.  In most cases, a Pyramid application built from a cookiecutter
   will have a single ``[app:main]`` section in it, and this will be the
   application served.

#. The framework finds all :mod:`logging` related configuration in the ``.ini``
   file and uses it to configure the Python standard library logging system for
   this application.  See :ref:`logging_config` for more information.

#. The application's *constructor* named by the entry point referenced on the
   ``use=`` line of the section representing your :app:`Pyramid` application is
   passed the key/value parameters mentioned within the section in which it's
   defined.  The constructor is meant to return a :term:`router` instance,
   which is a :term:`WSGI` application.

   For :app:`Pyramid` applications, the constructor will be a function named
   ``main`` in the ``__init__.py`` file within the :term:`package` in which
   your application lives.  If this function succeeds, it will return a
   :app:`Pyramid` :term:`router` instance.  Here's the contents of an example
   ``__init__.py`` module:

   .. literalinclude:: myproject/myproject/__init__.py
      :language: python
      :linenos:

   Note that the constructor function accepts a ``global_config`` argument,
   which is a dictionary of key/value pairs mentioned in the ``[DEFAULT]``
   section of an ``.ini`` file (if :ref:`[DEFAULT]
   <defaults_section_of_pastedeploy_file>` is present).  It also accepts a
   ``**settings`` argument, which collects another set of arbitrary key/value
   pairs.  The arbitrary key/value pairs received by this function in
   ``**settings`` will be composed of all the key/value pairs that are present
   in the ``[app:main]`` section (except for the ``use=`` setting) when this
   function is called when you run ``pserve``.

   Our generated ``development.ini`` file looks like so:

   .. literalinclude:: myproject/development.ini
      :language: ini
      :linenos:

   In this case, the ``myproject.__init__:main`` function referred to by the
   entry point URI ``egg:myproject`` (see :ref:`myproject_ini` for more
   information about entry point URIs, and how they relate to callables) will
   receive the key/value pairs ``{pyramid.reload_templates = true,
   pyramid.debug_authorization = false, pyramid.debug_notfound = false,
   pyramid.debug_routematch = false, pyramid.default_locale_name = en, and
   pyramid.includes = pyramid_debugtoolbar}``.  See :ref:`environment_chapter`
   for the meanings of these keys.

#. The ``main`` function first constructs a
   :class:`~pyramid.config.Configurator` instance, passing the ``settings``
   dictionary captured via the ``**settings`` kwarg as its ``settings``
   argument.

   The ``settings`` dictionary contains all the options in the ``[app:main]``
   section of our .ini file except the ``use`` option (which is internal to
   PasteDeploy) such as ``pyramid.reload_templates``,
   ``pyramid.debug_authorization``, etc.

#. The ``main`` function then calls various methods on the instance of the
   class :class:`~pyramid.config.Configurator` created in the previous step.
   The intent of calling these methods is to populate an :term:`application
   registry`, which represents the :app:`Pyramid` configuration related to the
   application.

#. The :meth:`~pyramid.config.Configurator.make_wsgi_app` method is called. The
   result is a :term:`router` instance.  The router is associated with the
   :term:`application registry` implied by the configurator previously
   populated by other methods run against the Configurator.  The router is a
   WSGI application.

#. An :class:`~pyramid.events.ApplicationCreated` event is emitted (see
   :ref:`events_chapter` for more information about events).

#. Assuming there were no errors, the ``main`` function in ``myproject``
   returns the router instance created by
   :meth:`pyramid.config.Configurator.make_wsgi_app` back to ``pserve``.  As
   far as ``pserve`` is concerned, it is "just another WSGI application".

#. ``pserve`` starts the WSGI *server* defined within the ``[server:main]``
   section.  In our case, this is the Waitress server (``use =
   egg:waitress#main``), and it will listen on all interfaces on port 6543
   for both IPv4 and IPv6 (``listen = localhost:6543``). The server
   code itself is what prints ``Serving on http://localhost:6543``. The server
   serves the application, and the application is running, waiting to receive requests.

.. seealso::
   Logging configuration is described in the :ref:`logging_chapter` chapter.
   There, in :ref:`request_logging_with_pastes_translogger`, you will also find
   an example of how to configure :term:`middleware` to add pre-packaged
   functionality to your application.

.. index::
   pair: settings; deployment
   single: custom settings

.. _deployment_settings:

Deployment Settings
-------------------

Note that an augmented version of the values passed as ``**settings`` to the
:class:`~pyramid.config.Configurator` constructor will be available in
:app:`Pyramid` :term:`view callable` code as ``request.registry.settings``. You
can create objects you wish to access later from view code, and put them into
the dictionary you pass to the configurator as ``settings``.  They will then be
present in the ``request.registry.settings`` dictionary at application runtime.
