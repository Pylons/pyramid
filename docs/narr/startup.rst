.. _startup_chapter:

Startup
=======

When you cause :mod:`repoze.bfg` to start up in a console window,
you'll see something much like this show up on the console:

.. code-block:: text

  $ paster serve myproject/MyProject.ini
  Starting server in PID 16601.
  serving on 0.0.0.0:6543 view at http://127.0.0.1:6543

This chapter explains what happens between the time you press the
"Return" key on your keyboard after typing ``paster serve
myproject/MyProject.ini`` and the time the line ``serving on
0.0.0.0:6543 ...`` is output to your console.

.. index::
   single: startup process

The Startup Process
-------------------

The easiest and best-documented way to start and serve a
:mod:`repoze.bfg` application is to use the ``paster serve`` command
against a :term:`PasteDeploy` ``.ini`` file.  This uses the ``.ini``
file to infer settings and starts a server listening on a port.  For
the purposes of this discussion, we'll assume that you are using this
command to run your :mod:`repoze.bfg` application.

Here's a high-level time-ordered overview of what happens when you
press ``return`` after running ``paster serve MyProject.ini``.

#. The :term:`PasteDeploy` ``paster`` command is invoked under your
   shell with the arguments ``serve`` and ``MyProject.ini``.  As a
   result, the :term:`PasteDeploy` framework recognizes that it is
   meant to begin to run and serve an application using the
   information contained within the ``MyProject.ini`` file.

#. The PasteDeploy framework finds a section named either
   ``[app:main]``, ``[pipeline:main]``, or ``[composite::main]`` in
   the ``.ini`` file.  This section represents the configuration of a
   :term:`WSGI` application that will be served.  If you're using a
   simple application (e.g. an ``[app:main]`` section of a
   default-generated :mod:`repoze.bfg` project), the application
   :term:`entry point` or :term:`dotted Python name` will be named on
   the ``use=`` line within the section's configuration.  If, instead
   of a simple application, you're using a WSGI :term:`pipeline`
   (e.g. a ``[pipeline:main]`` section), the application named on the
   "last" element will refer to your :mod:`repoze.bfg` application.
   If instead of a simple application or a pipeline, you're using a
   Paste "composite" (e.g. ``[composite:main]``), refer to the
   documentation for that particular composite to understand how to
   make it refer to your :mod:`repoze.bfg` application.

#. The application's *constructor* (named by the entry point reference
   or dotted Python name on the ``use=`` line) is passed the key/value
   parameters mentioned within the section in which it's defined.  The
   constructor is meant to return a :term:`router` instance, which is
   a :term:`WSGI` application.

   For :mod:`repoze.bfg` applications, the constructor will be a
   function named ``app`` in the ``run.py`` file within the
   :term:`package` in which your application lives.  If this function
   succeeds, it will return a :mod:`repoze.bfg` :term:`router`
   instance.  Here's the contents of an example ``run.py`` module:

   .. literalinclude:: MyProject/myproject/run.py
      :linenos:

   Note that the constructor function accepts a ``global_config``
   argument (which is a dictionary of key/value pairs mentioned in the
   ``[DEFAULT]`` section of the configuration file).  It also accepts
   a ``**settings`` argument, which collects another set of arbitrary
   key/value pairs.  The arbitrary key/value pairs received by this
   function in ``**settings`` will be composed of all the key/value
   pairs that are present in the ``[app:main]`` section (except for
   the ``use=`` setting) when this function is called by the
   :term:`PasteDeploy` framework when you run ``paster serve``.

   Our generated ``MyProject.ini`` file looks like so:

   .. literalinclude:: MyProject/MyProject.ini
      :linenos:

   In this case, the ``myproject.run:app`` function referred to by the
   entry point URI ``egg:MyProject#app`` (see :ref:`MyProject_ini` for
   more information about entry point URIs, and how they relate to
   callables), will receive the key/value pairs
   ``{'reload_templates':'true', 'debug_authorization':'false',
   'debug_notfound':'false'}``.

#. The ``app`` function first constructs a
   :class:`repoze.bfg.configuration.Configurator` instance, passing
   ``get_root`` to it as its ``root_factory`` argument, and
   ``settings`` dictionary captured via the ``**settings`` kwarg as
   its ``settings`` argument.

   ``get_root`` is a root factory callable that is invoked on every
   request to retrieve the application root.  It is not called during
   startup, only when a request is handled.

   ``settings`` dictionary contains all the options in the
   ``[app:main]`` section of our .ini file except the "use" option
   (which is internal to paste).  In this case, ``**settings`` will be
   something like ``{'reload_templates':'true',
   'debug_authorization':'false', 'debug_notfound':'false'}``.

#. The ``app`` function then calls the
   :meth:`repoze.bfg.configuration.Configurator.load_zcml` method,
   passing in a ``zcml_file`` value.  ``zcml_file`` is the value of
   the ``configure_zcml`` setting or a default of ``configure.zcml``.
   This filename is relative to the run.py file that the ``app``
   function lives in.  The ``load_zcml`` function processes each
   :term:`ZCML declaration` in the ZCML file implied by the
   ``zcml_file`` argument.  If ``load_zcml`` fails to parse the ZCML
   file (or any file which is included by the ZCML file), a
   ``XMLConfigurationError`` is raised and processing ends.  If it
   succeeds, an :term:`application registry` is populated using all
   the :term:`ZCML declaration` statements present in the file.

#. The :meth:`repoze.bfg.configuration.Configurator.make_wsgi_app`
   method is called.  The result is a :term:`router` instance.  The
   router is associated with the :term:`application registry` implied
   by the configurator previously populated by ZCML.  The router is a
   WSGI application.

#. A :class:`repoze.bfg.interfaces.WSGIApplicationCreatedEvent` event
   is emitted (see :ref:`events_chapter` for more information about
   events).

#. Assuming there were no errors, the ``app`` function in
   ``myproject`` returns the router instance created by
   ``make_wsgi_app`` back to PasteDeploy.  As far as PasteDeploy is
   concerned, it is "just another WSGI application".

#. PasteDeploy starts the WSGI *server* defined within the
   ``[server:main]`` section.  In our case, this is the ``Paste#http``
   server (``use = egg:Paste#http``), and it will listen on all
   interfaces (``host = 0.0.0.0``), on port number 6543 (``port =
   6543``).  The server code itself is what prints ``serving on
   0.0.0.0:6543 view at http://127.0.0.1:6543``.  The server serves
   the application, and the application is running, waiting to receive
   requests.




   

