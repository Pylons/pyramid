============
Installation
============

This tutorial assumes that Python and virtualenv are already installed
and working in your system. If you need help setting this up, you should
refer to the chapters on :ref:`installing_chapter`.

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

#. Use your Python's virtualenv to make a workspace:

   .. code-block:: text

      $ path/to/my/Python-2.6/bin/virtualenv --no-site-packages pyramidtut

#. Switch to the ``pyramidtut`` directory:

   .. code-block:: text

      $ cd pyramidtut

#. Use ``easy_install`` to get :app:`Pyramid` and its direct
   dependencies installed:

   .. code-block:: text

      $ bin/easy_install pyramid

#. Use ``easy_install`` to install various packages from PyPI.

   .. code-block:: text

      $ bin/easy_install docutils nose coverage zope.sqlalchemy \
                SQLAlchemy pyramid_tm

Preparation, Windows
--------------------

#. Use your Python's virtualenv to make a workspace:

   .. code-block:: text

      c:\> c:\Python26\Scripts\virtualenv --no-site-packages pyramidtut

#. Switch to the ``pyramidtut`` directory:

   .. code-block:: text

      c:\> cd pyramidtut

#. Use ``easy_install`` to get :app:`Pyramid` and its direct
   dependencies installed:

   .. code-block:: text

      c:\pyramidtut> Scripts\easy_install pyramid

#. Use ``easy_install`` to install various packages from PyPI.

   .. code-block:: text

      c:\pyramidtut> Scripts\easy_install docutils \
               nose coverage zope.sqlalchemy SQLAlchemy pyramid_tm


.. _sql_making_a_project:

Making a Project
================

Your next step is to create a project.  :app:`Pyramid` supplies a
variety of scaffolds to generate sample projects.  We will use the
``pyramid_routesalchemy`` scaffold, which generates an application
that uses :term:`SQLAlchemy` and :term:`URL dispatch`.

The below instructions assume your current working directory is the
"virtualenv" named "pyramidtut".

On UNIX:

.. code-block:: text

   $ bin/paster create -t pyramid_routesalchemy tutorial

On Windows:

.. code-block:: text

   c:\pyramidtut> Scripts\paster create -t pyramid_routesalchemy tutorial

.. note:: If you are using Windows, the ``pyramid_routesalchemy``
   scaffold may not deal gracefully with installation into a
   location that contains spaces in the path.  If you experience
   startup problems, try putting both the virtualenv and the project
   into directories that do not contain spaces in their paths.

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

   c:\pyramidtut> cd tutorial
   c:\pyramidtut\tutorial> ..\Scripts\python setup.py develop

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

   c:\pyramidtut\tutorial> ..\Scripts\python setup.py test -q

Starting the Application
========================

Start the application.

On UNIX:

.. code-block:: text

   $ ../bin/paster serve development.ini --reload

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> ..\Scripts\paster serve development.ini --reload

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

   c:\pyramidtut\tutorial> ..\Scripts\easy_install nose coverage

Once ``nose`` and ``coverage`` are installed, we can actually run the
coverage tests.

On UNIX:

.. code-block:: text

   $ ../bin/nosetests --cover-package=tutorial --cover-erase --with-coverage

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> ..\Scripts\nosetests --cover-package=tutorial ^
         --cover-erase --with-coverage

Looks like our package's ``models`` module doesn't quite have 100%
test coverage.

Visit the Application in a Browser
==================================

In a browser, visit ``http://localhost:6543/``.  You will see the
generated application's default page.

One thing you'll notice is the "debug toolbar" icon on right hand side of the
page.  You can read more about the purpose of the icon at
:ref:`debug_toolbar`.  It allows you to get information about your
application while you develop.

Decisions the ``pyramid_routesalchemy`` Scaffold Has Made For You
=================================================================

Creating a project using the ``pyramid_routesalchemy`` scaffold makes
the following assumptions:

- you are willing to use :term:`SQLAlchemy` as a database access tool

- you are willing to use :term:`url dispatch` to map URLs to code.

.. note::

   :app:`Pyramid` supports any persistent storage mechanism (e.g. object
   database or filesystem files, etc).  It also supports an additional
   mechanism to map URLs to code (:term:`traversal`).  However, for the
   purposes of this tutorial, we'll only be using url dispatch and
   SQLAlchemy.

