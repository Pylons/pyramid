============================================
02: Python Packages for Pyramid Applications
============================================

Most modern Python development is done using Python packages, an approach
Pyramid puts to good use. In this step we redo "Hello World" as a minimal
Python package inside a minimal Python project.


Background
==========

Python developers can organize a collection of modules and files into a
namespaced unit called a :ref:`package <python:tut-packages>`. If a directory
is on ``sys.path`` and has a special file named ``__init__.py``, it is treated
as a Python package.

Packages can be bundled up, made available for installation, and installed
through a toolchain oriented around a ``setup.py`` file. For this tutorial,
this is all you need to know:

- We will have a directory for each tutorial step as a *project*.

- This project will contain a ``setup.py`` which injects the features of the
  project machinery into the directory.

- In this project we will make a ``tutorial`` subdirectory into a Python
  *package* using an ``__init__.py`` Python module file.

- We will run ``pip install -e .`` to install our project in development mode.

In summary:

- You'll do your development in a Python *package*.

- That package will be part of a *project*.


Objectives
==========

- Make a Python "package" directory with an ``__init__.py``.

- Get a minimum Python "project" in place by making a ``setup.py``.

- Install our ``tutorial`` project in development mode.


Steps
=====

#. Make an area for this tutorial step:

   .. code-block:: bash

    $ cd ..; mkdir package; cd package

#. In ``package/setup.py``, enter the following:

   .. literalinclude:: package/setup.py

#. Make the new project installed for development then make a directory for the
   actual code:

   .. code-block:: bash

    $ $VENV/bin/pip install -e .
    $ mkdir tutorial

#. Enter the following into ``package/tutorial/__init__.py``:

   .. literalinclude:: package/tutorial/__init__.py

#. Enter the following into ``package/tutorial/app.py``:

   .. literalinclude:: package/tutorial/app.py

#. Run the WSGI application with:

   .. code-block:: bash

    $ $VENV/bin/python tutorial/app.py

#. Open http://localhost:6543/ in your browser.


Analysis
========

Python packages give us an organized unit of project development. Python
projects, via ``setup.py``, give us special features when our package is
installed (in this case, in local development mode, also called local editable
mode as indicated by ``-e .``).

In this step we have a Python package called ``tutorial``. We use the same name
in each step of the tutorial, to avoid unnecessary retyping.

Above this ``tutorial`` directory we have the files that handle the packaging
of this project. At the moment, all we need is a bare-bones ``setup.py``.

Everything else is the same about our application. We simply made a Python
package with a ``setup.py`` and installed it in development mode.

Note that the way we're running the app (``python tutorial/app.py``) is a bit
of an odd duck.  We would never do this unless we were writing a tutorial that
tries to capture how this stuff works one step at a time. It's generally a bad
idea to run a Python module inside a package directly as a script.

.. seealso:: :ref:`Python Packages <python:tut-packages>` and `Working in
   "Development Mode"
   <https://packaging.python.org/en/latest/distributing/#working-in-development-mode>`_.
