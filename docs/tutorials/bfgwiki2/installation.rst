============
Installation
============

For the most part, the installation process for this tutorial
duplicates the steps described in :ref:`installing_chapter` and
:ref:`project_narr`, however it also explains how to install
additional libraries for tutorial purposes.

Preparation
===========

Please take the following steps to prepare for the tutorial.  The
steps are slightly different depending on whether you're using UNIX or
Windows.

Preparation, UNIX
-----------------

#. Install SQLite3 and its development packages if you don't already
   have them installed.  Usually this is via your system's package
   manager.  For example, on a Debian Linux system, do ``sudo apt-get
   install libsqlite3-dev``.

#. If you don't already have a Python 2.5 interpreter installed on
   your system, obtain, install, or find `Python 2.5
   <http://python.org/download/releases/2.5.4/>`_ for your system.

#. Install the latest `setuptools` into the Python you
   obtained/installed/found in the step above: download `ez_setup.py
   <http://peak.telecommunity.com/dist/ez_setup.py>`_ and run it using
   the ``python`` interpreter of your Python 2.5 installation:

   .. code-block:: text

      $ /path/to/my/Python-2.5/bin/python ez_setup.py

#. Use that Python's `bin/easy_install` to install `virtualenv`:

   .. code-block:: text

      $ /path/to/my/Python-2.5/bin/easy_install virtualenv

#. Use that Python's virtualenv to make a workspace:

   .. code-block:: text

      $ path/to/my/Python-25/bin/virtualenv --no-site-packages bigfntut

#. Switch to the ``bigfntut`` directory:

   .. code-block:: text

      $ cd bigfntut

#. (Optional) Consider using ``source bin/activate`` to make your
   shell environment wired to use the virtualenv.

#. Use ``easy_install`` and point to the BFG "current" index to get
   :mod:`repoze.bfg` and its direct dependencies installed:

   .. code-block:: text

      $ bin/easy_install -i http://dist.repoze.org/bfg/current/simple \
              repoze.bfg

#. Use ``easy_install`` to install various packages from PyPI.

   .. code-block:: text

      $ bin/easy_install docutils nose coverage zope.sqlalchemy SQLAlchemy \
                repoze.tm2

Preparation, Windows
--------------------

#. Install, or find `Python 2.5
   <http://python.org/download/releases/2.5.4/>`_ for your system.

#. Install the latest `setuptools` into the Python you
   obtained/installed/found in the step above: download `ez_setup.py
   <http://peak.telecommunity.com/dist/ez_setup.py>`_ and run it using
   the ``python`` interpreter of your Python 2.5 installation using a
   command prompt:

   .. code-block:: text

      c:\> c:\Python25\python ez_setup.py

#. Use that Python's `bin/easy_install` to install `virtualenv`:

   .. code-block:: text

      c:\> c:\Python25\Scripts\easy_install virtualenv

#. Use that Python's virtualenv to make a workspace:

   .. code-block:: text

      c:\> c:\Python25\Scripts\virtualenv --no-site-packages bigfntut

#. Switch to the ``bigfntut`` directory:

   .. code-block:: text

      c:\> cd bigfntut

#. (Optional) Consider using ``bin\activate.bat`` to make your shell
   environment wired to use the virtualenv.

#. Use ``easy_install`` and point to the BFG "current" index to get
   :mod:`repoze.bfg` and its direct dependencies installed:

   .. code-block:: text

      c:\bigfntut> Scripts\easy_install -i \
                http://dist.repoze.org/bfg/current/simple repoze.bfg

#. Use ``easy_install`` to install various packages from PyPI.

   .. code-block:: text

      c:\bigfntut> Scripts\easy_install -i \
               http://dist.repoze.org/bfg/current/simple docutils \
               nose coverage zope.sqlalchemy SQLAlchemy repoze.tm2


.. _sql_making_a_project:

Making a Project
================

Your next step is to create a project.  :mod:`repoze.bfg` supplies a
variety of templates to generate sample projects.  We will use the
``bfg_routesalchemy`` template, which generates an application that
uses :term:`SQLAlchemy` and :term:`URL dispatch`.

The below instructions assume your current working directory is the
"virtualenv" named "bigfntut".

On UNIX:

.. code-block:: text

   $ bin/paster create -t bfg_routesalchemy tutorial

On Windows:

.. code-block:: text

   c:\bigfntut> Scripts\paster create -t bfg_routesalchemy tutorial

.. note:: If you are using Windows, the ``bfg_routesalchemy`` Paster
   template may not deal gracefully with installation into a location
   that contains spaces in the path.  If you experience startup
   problems, try putting both the virtualenv and the project into
   directories that do not contain spaces in their paths.

Installing the Project in "Development Mode"
============================================

In order to do development on the project easily, you must "register"
the project as a development egg in your workspace using the
``setup.py develop`` command.  In order to do so, cd to the "tutorial"
directory you created in :ref:`sql_making_a_project`, and run the
"setup.py develop" command using virtualenv Python interpreter.

On UNIX:

.. code-block:: text

   $ cd tutorial
   $ ../bin/python setup.py develop

On Windows:

.. code-block:: text

   c:\bigfntut> cd tutorial
   c:\bigfntut\tutorial> ..\Scripts\python setup.py develop

.. _sql_running_tests:

Running the Tests
=================

After you've installed the project in development mode, you may run
the tests for the project.

On UNIX:

.. code-block:: text

   $ ../bin/python setup.py test -q

On Windows:

.. code-block:: text

   c:\bigfntut\tutorial> ..\Scripts\python setup.py test -q

Starting the Application
========================

Start the application.

On UNIX:

.. code-block:: text

   $ ../bin/paster serve tutorial.ini --reload

On Windows:

.. code-block:: text

   c:\bifgfntut\tutorial> ..\Scripts\paster serve tutorial.ini --reload

Exposing Test Coverage Information
==================================

You can run the ``nosetests`` command to see test coverage
information.  This runs the tests in the same way that ``setup.py
test`` does but provides additional "coverage" information, exposing
which lines of your project are "covered" (or not covered) by the
tests.

To get this functionality working, we'll need to install a couple of
other packages into our ``virtualenv``: ``nose`` and ``coverage``:

On UNIX:

.. code-block:: text

   $ ../bin/easy_install nose coverage

On Windows:

.. code-block:: text

   c:\bfgfntut\tutorial> ..\Scripts\easy_install nose coverage

Once ``nose`` and ``coverage`` are installed, we can actually run the
coverage tests.

On UNIX:

.. code-block:: text

   $ ../bin/nosetests --cover-package=tutorial --cover-erase --with-coverage

On Windows:

.. code-block:: text

   c:\bigfntut\tutorial> ..\Scripts\nosetests --cover-package=tutorial \
         --cover-erase --with-coverage

Looks like our package's ``models`` module doesn't quite have 100%
test coverage.

Visit the Application in a Browser
==================================

In a browser, visit ``http://localhost:6543/``.  You will see the
generated application's default page.

Decisions the ``bfg_routesalchemy`` Template Has Made For You
=============================================================

Creating a project using the ``bfg_routesalchemy`` template makes the
assumption that you are willing to use :term:`SQLAlchemy` as a
database access tool and :term:`url dispatch` to map URLs to code.
:mod:`repoze.bfg` supports any persistent storage mechanism
(e.g. object database or filesystem files, etc).  It also supports an
additional mechanism to map URLs to code (:term:`traversal`).
However, for the purposes of this tutorial, we'll only be using url
dispatch and SQLAlchemy.

