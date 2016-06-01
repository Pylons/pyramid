.. _qtut_requirements:

============
Requirements
============

Let's get our tutorial environment set up. Most of the set up work is in
standard Python development practices (install Python and make an isolated
virtual environment.)

.. note::

  Pyramid encourages standard Python development practices with packaging
  tools, virtual environments, logging, and so on. There are many variations,
  implementations, and opinions across the Python community.  For consistency,
  ease of documentation maintenance, and to minimize confusion, the Pyramid
  *documentation* has adopted specific conventions that are consistent with the
  :term:`Python Packaging Authority`.

This *Quick Tutorial* is based on:

* **Python 3.5**. Pyramid fully supports Python 3.3+ and Python 2.7+. This
  tutorial uses **Python 3.5** but runs fine under Python 2.7.

* **venv**. We believe in virtual environments. For this tutorial, we use
  Python 3.5's built-in solution :term:`venv`. For Python 2.7, you can install
  :term:`virtualenv`.

* **pip**. We use :term:`pip` for package management.

* **Workspaces, projects, and packages.** Our home directory will contain a
  *tutorial workspace* with our Python virtual environment and *Python
  projects* (a directory with packaging information and *Python packages* of
  working code.)

* **Unix commands**. Commands in this tutorial use UNIX syntax and paths.
  Windows users should adjust commands accordingly.

.. note::
    Pyramid was one of the first web frameworks to fully support Python 3 in
    October 2011.

.. note::
    Windows commands use the plain old MSDOS shell. For PowerShell command
    syntax, see its documentation.

Steps
=====

#. :ref:`install-python-3`
#. :ref:`create-a-project-directory-structure`
#. :ref:`set-an-environment-variable`
#. :ref:`create-a-virtual-environment`
#. :ref:`install-pyramid`


.. _install-python-3:

Install Python 3
----------------

See the detailed recommendation for your operating system described under
:ref:`installing_chapter`.

- :ref:`for-mac-os-x-users`
- :ref:`if-you-don-t-yet-have-a-python-interpreter-unix`
- :ref:`if-you-don-t-yet-have-a-python-interpreter-windows`


.. _create-a-project-directory-structure:

Create a project directory structure
------------------------------------

We will arrive at a directory structure of ``workspace -> project -> package``,
where our workspace is named ``quick_tutorial``. The following tree diagram
shows how this will be structured, and where our :term:`virtual environment`
will reside as we proceed through the tutorial:

.. code-block:: text

    `── ~
        `── projects
            `── quick_tutorial
                │── env
                `── step_one
                    │── intro
                    │   │── __init__.py
                    │   `── app.py
                    `── setup.py

For Linux, the commands to do so are as follows:

.. code-block:: bash

    # Mac and Linux
    $ cd ~
    $ mkdir -p projects/quick_tutorial
    $ cd projects/quick_tutorial

For Windows:

.. code-block:: doscon

    # Windows
    c:\> cd \
    c:\> mkdir projects\quick_tutorial
    c:\> cd projects\quick_tutorial

In the above figure, your user home directory is represented by ``~``. In your
home directory, all of your projects are in the ``projects`` directory. This is
a general convention not specific to Pyramid that many developers use. Windows
users will do well to use ``c:\`` as the location for ``projects`` in order to
avoid spaces in any of the path names.

Next within ``projects`` is your workspace directory, here named
``quick_tutorial``. A workspace is a common term used by integrated
development environments (IDE), like PyCharm and PyDev, where virtual
environments, specific project files, and repositories are stored.


.. _set-an-environment-variable:

Set an environment variable
---------------------------

This tutorial will refer frequently to the location of the :term:`virtual
environment`. We set an environment variable to save typing later.

.. code-block:: bash

    # Mac and Linux
    $ export VENV=~/projects/quick_tutorial/env

.. code-block:: doscon

    # Windows
    c:\> set VENV=c:\projects\quick_tutorial\env


.. _create-a-virtual-environment:

Create a virtual environment
----------------------------

``venv`` is a tool to create isolated Python 3 environments, each with its own
Python binary and independent set of installed Python packages in its site
directories. Let's create one, using the location we just specified in the
environment variable.

.. code-block:: bash

    # Mac and Linux
    $ python3 -m venv $VENV

.. code-block:: doscon

    # Windows
    c:\> c:\Python35\python3 -m venv %VENV%

.. seealso:: See also Python 3's :mod:`venv module <python:venv>` and Python
   2's `virtualenv <https://virtualenv.pypa.io/en/latest/>`_ package.


Update packaging tools in the virtual environment
-------------------------------------------------

It's always a good idea to update to the very latest version of packaging tools
because the installed Python bundles only the version that was available at the
time of its release.

.. code-block:: bash

    # Mac and Linux
    $VENV/bin/pip install --upgrade pip setuptools

.. code-block:: doscon

    # Windows
    c:\> %VENV%\Scripts\pip install --upgrade pip setuptools


.. _install-pyramid:

Install Pyramid
---------------

We have our Python standard prerequisites out of the way. The Pyramid
part is pretty easy.

.. parsed-literal::

    # Mac and Linux
    $ $VENV/bin/pip install "pyramid==\ |release|\ "

    # Windows
    c:\\> %VENV%\\Scripts\\pip install "pyramid==\ |release|\ "

Our Python virtual environment now has the Pyramid software available.

You can optionally install some of the extra Python packages used in this
tutorial.

.. code-block:: bash

    # Mac and Linux
    $ $VENV/bin/pip install webtest pytest pytest-cov deform sqlalchemy \
      pyramid_chameleon pyramid_debugtoolbar pyramid_jinja2 waitress \
      pyramid_tm zope.sqlalchemy

.. code-block:: doscon

    # Windows
    c:\> %VENV%\Scripts\pip install webtest deform sqlalchemy pyramid_chameleon pyramid_debugtoolbar pyramid_jinja2 waitress pyramid_tm zope.sqlalchemy
