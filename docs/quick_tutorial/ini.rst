.. _qtut_ini:

=================================================
03: Application Configuration with ``.ini`` Files
=================================================

Use Pyramid's ``pserve`` command with a ``.ini`` configuration file for
simpler, better application running.


Background
==========

Pyramid has a first-class concept of :ref:`configuration <configuration_narr>`
distinct from code. This approach is optional, but its presence makes it
distinct from other Python web frameworks. It taps into Python's ``setuptools``
library, which establishes conventions for installing and providing "entry
points" for Python projects. Pyramid uses an entry point to let a Pyramid
application know where to find the WSGI app.


Objectives
==========

- Modify our ``setup.py`` to have an entry point telling Pyramid the location
  of the WSGI app.

- Create an application driven by an ``.ini`` file.

- Start the application with Pyramid's ``pserve`` command.

- Move code into the package's ``__init__.py``.


Steps
=====

#. First we copy the results of the previous step:

   .. code-block:: bash

    $ cd ..; cp -r package ini; cd ini

#. Our ``ini/setup.py`` needs a setuptools "entry point" in the ``setup()``
   function:

   .. literalinclude:: ini/setup.py
    :linenos:

#. We can now install our project, thus generating (or re-generating) an "egg"
   at ``ini/tutorial.egg-info``:

   .. code-block:: bash

    $ $VENV/bin/pip install -e .

#. Let's make a file ``ini/development.ini`` for our configuration:

   .. literalinclude:: ini/development.ini
    :language: ini
    :linenos:

#. We can refactor our startup code from the previous step's ``app.py`` into
   ``ini/tutorial/__init__.py``:

   .. literalinclude:: ini/tutorial/__init__.py
    :linenos:

#. Now that ``ini/tutorial/app.py`` isn't used, let's remove it:

   .. code-block:: bash

    $ rm tutorial/app.py

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/.

Analysis
========

Our ``development.ini`` file is read by ``pserve`` and serves to bootstrap our
application. Processing then proceeds as described in the Pyramid chapter on
:ref:`application startup <startup_chapter>`:

- ``pserve`` looks for ``[app:main]`` and finds ``use = egg:tutorial``.

- The projects's ``setup.py`` has defined an "entry point" (lines 9-12) for the
  project's "main" entry point of ``tutorial:main``.

- The ``tutorial`` package's ``__init__`` has a ``main`` function.

- This function is invoked, with the values from certain ``.ini`` sections
  passed in.

The ``.ini`` file is also used for two other functions:

- *Configuring the WSGI server*. ``[server:main]`` wires up the choice of which
  WSGI *server* for your WSGI *application*. In this case, we are using
  ``wsgiref`` bundled in the Python library. It also wires up the *port
  number*: ``port = 6543`` tells ``wsgiref`` to listen on port 6543.

- *Configuring Python logging*. Pyramid uses Python standard logging, which
  needs a number of configuration values. The ``.ini`` serves this function.
  This provides the console log output that you see on startup and each
  request.

We moved our startup code from ``app.py`` to the package's
``tutorial/__init__.py``. This isn't necessary, but it is a common style in
Pyramid to take the WSGI app bootstrapping out of your module's code and put it
in the package's ``__init__.py``.

The ``pserve`` application runner has a number of command-line arguments and
options. We are using ``--reload`` which tells ``pserve`` to watch the
filesystem for changes to relevant code (Python files, the INI file, etc.) and,
when something changes, restart the application. Very handy during development.


Extra credit
============

#. If you don't like configuration and/or ``.ini`` files, could you do this
   yourself in Python code?

#. Can we have multiple ``.ini`` configuration files for a project? Why might
   you want to do that?

#. The entry point in ``setup.py`` didn't mention ``__init__.py`` when it
   declared ``tutorial:main`` function. Why not?

#. What is the purpose of ``**settings``? What does the ``**`` signify?

.. seealso::
   :ref:`project_narr`,
   :ref:`cookiecutters`,
   :ref:`what_is_this_pserve_thing`,
   :ref:`environment_chapter`,
   :ref:`paste_chapter`
