.. _qtut_debugtoolbar:

============================================
04: Easier Development with ``debugtoolbar``
============================================

Error handling and introspection using the ``pyramid_debugtoolbar`` add-on.


Background
==========

As we introduce the basics, we also want to show how to be productive in
development and debugging. For example, we just discussed template reloading,
and earlier we showed ``--reload`` for application reloading.

``pyramid_debugtoolbar`` is a popular Pyramid add-on which makes several tools
available in your browser. Adding it to your project illustrates several points
about configuration.


Objectives
==========

- Install and enable the toolbar to help during development.

- Explain Pyramid add-ons.

- Show how an add-on gets configured into your application.


Steps
=====

#.  First we copy the results of the previous step.

    .. code-block:: bash

        cd ..; cp -r ini debugtoolbar; cd debugtoolbar

#.  Add ``pyramid_debugtoolbar`` to our project's dependencies in ``setup.py`` as a :term:`Setuptools` "extra" for development:

    .. literalinclude:: debugtoolbar/setup.py
        :language: python
        :linenos:
        :emphasize-lines: 10-16, 20-22

#.  Install our project and its newly added dependency.
    Note that we use the extra specifier ``[dev]`` to install development requirements and surround it and the period with double quote marks.

    .. code-block:: bash

        $VENV/bin/pip install -e ".[dev]"

#.  Our ``debugtoolbar/development.ini`` gets a configuration entry for ``pyramid.includes``:

    .. literalinclude:: debugtoolbar/development.ini
        :language: ini
        :linenos:

#.  Run the WSGI application with:

    .. code-block:: bash

        $VENV/bin/pserve development.ini --reload

#.  Open http://localhost:6543/ in your browser.
    See the handy toolbar on the right. ``note: the Response object should contain <body> html or it won't be shown unless an error is introduced.``
    


Analysis
========

``pyramid_debugtoolbar`` is a full-fledged Python package, available on PyPI
just like thousands of other Python packages. Thus we start by installing the
``pyramid_debugtoolbar`` package into our virtual environment using normal
Python package installation commands.

The ``pyramid_debugtoolbar`` Python package is also a Pyramid add-on, which
means we need to include its add-on configuration into our web application. We
could do this with imperative configuration in ``tutorial/__init__.py`` by
using ``config.include``. Pyramid also supports wiring in add-on configuration
via our ``development.ini`` using ``pyramid.includes``. We use this to load the
configuration for the debugtoolbar.

You'll now see an attractive button on the right side of your browser, which
you may click to provide introspective access to debugging information in a new
browser tab. Even better, if your web application generates an error, you will
see a nice traceback on the screen. When you want to disable this toolbar,
there's no need to change code: you can remove it from ``pyramid.includes`` in
the relevant ``.ini`` configuration file (thus showing why configuration files
are handy).

Note that the toolbar injects a small amount of HTML/CSS into your app just
before the closing ``</body>`` tag in order to display itself. If you start to
experience otherwise inexplicable client-side weirdness, you can shut it off
by commenting out the ``pyramid_debugtoolbar`` line in ``pyramid.includes``
temporarily.

Finally we've introduced the concept of :term:`Setuptools` extras.
These are optional or recommended features that may be installed with an "extras" specifier, in this case, ``dev``.
The specifier is the name of a key in a Python dictionary, and is surrounded by square brackets when invoked on the command line, for example, .
The value for the key is a Python list of dependencies.

.. seealso:: See also :ref:`pyramid_debugtoolbar <toolbar:overview>`.


Extra credit
============

#.  We added ``pyramid_debugtoolbar`` to the list of ``dev_requires`` dependencies in ``debugtoolbar/setup.py``.
    We then installed the dependencies via ``pip install -e ".[dev]"`` by virtue of the Setuptools ``extras_require`` value in the Python dictionary.
    Why did we add them there instead of in the ``requires`` list?

#.  Introduce a bug into your application. Change:

    .. code-block:: python

        def hello_world(request):
            return Response('<body><h1>Hello World!</h1></body>')

    to:

    .. code-block:: python

        def hello_world(request):
            return xResponse('<body><h1>Hello World!</h1></body>')

    Save, and visit http://localhost:6543/ again.
    Notice the nice traceback display.
    On the lowest line, click the "screen" icon to the right, and try typing the variable names ``request`` and ``Response``.
    What else can you discover?
