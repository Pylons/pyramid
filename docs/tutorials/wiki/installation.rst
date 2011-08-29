============
Installation
============

For the most part, the installation process for this tutorial
duplicates the steps described in :ref:`installing_chapter` and
:ref:`project_narr`, however it also explains how to install
additional libraries for tutorial purposes.

Preparation
========================

Please take the following steps to prepare for the tutorial.  The
steps to prepare for the tutorial are slightly different depending on
whether you're using UNIX or Windows.

Preparation, UNIX
-----------------

#. If you don't already have a Python 2.6 interpreter installed on
   your system, obtain, install, or find `Python 2.6
   <http://python.org/download/releases/2.6.6/>`_ for your system.

#. Make sure the Python development headers are installed on your system.  If
   you've installed Python from source, these will already be installed.  If
   you're using a system Python, you may have to install a ``python-dev``
   package (e.g. ``apt-get python-dev``).  The headers are not required for
   Pyramid itself, just for dependencies of the tutorial.

#. Install the latest `setuptools` into the Python you
   obtained/installed/found in the step above: download `ez_setup.py
   <http://peak.telecommunity.com/dist/ez_setup.py>`_ and run it using
   the ``python`` interpreter of your Python 2.6 installation:

   .. code-block:: text

    $ /path/to/my/Python-2.6/bin/python ez_setup.py

#. Use that Python's `bin/easy_install` to install `virtualenv`:

   .. code-block:: text

    $ /path/to/my/Python-2.6/bin/easy_install virtualenv

#. Use that Python's virtualenv to make a workspace:

   .. code-block:: text

     $ path/to/my/Python-2.6/bin/virtualenv --no-site-packages \
               pyramidtut

#. Switch to the ``pyramidtut`` directory:

   .. code-block:: text

     $ cd pyramidtut

#. (Optional) Consider using ``source bin/activate`` to make your
   shell environment wired to use the virtualenv.

#. Use ``easy_install`` to get :app:`Pyramid` and its direct
   dependencies installed:

   .. code-block:: text

     $ bin/easy_install pyramid

#. Use ``easy_install`` to install ``docutils``, ``pyramid_tm``,
   ``pyramid_zodbconn``, ``pyramid_debugtoolbar``, ``nose`` and ``coverage``:

   .. code-block:: text

     $ bin/easy_install docutils pyramid_tm pyramid_zodbconn \
               pyramid_debugtoolbar nose coverage

Preparation, Windows
--------------------

#. Install, or find `Python 2.6
   <http://python.org/download/releases/2.6.6/>`_ for your system.

#. Install the latest `setuptools` into the Python you
   obtained/installed/found in the step above: download `ez_setup.py
   <http://peak.telecommunity.com/dist/ez_setup.py>`_ and run it using
   the ``python`` interpreter of your Python 2.6 installation using a
   command prompt:

   .. code-block:: text

    c:\> c:\Python26\python ez_setup.py

#. Use that Python's `bin/easy_install` to install `virtualenv`:

   .. code-block:: text

    c:\> c:\Python26\Scripts\easy_install virtualenv

#. Use that Python's virtualenv to make a workspace:

   .. code-block:: text

     c:\> c:\Python26\Scripts\virtualenv --no-site-packages pyramidtut

#. Switch to the ``pyramidtut`` directory:

   .. code-block:: text

     c:\> cd pyramidtut

#. (Optional) Consider using ``bin\activate.bat`` to make your shell
   environment wired to use the virtualenv.

#. Use ``easy_install`` to get :app:`Pyramid` and its direct
   dependencies installed:

   .. code-block:: text

     c:\pyramidtut> Scripts\easy_install pyramid

#. Use ``easy_install`` to install ``docutils``, ``pyramid_tm``,
   ``pyramid_zodbconn``, ``pyramid_debugtoolbar``, ``nose`` and ``coverage``:

   .. code-block:: text

     c:\pyramidtut> Scripts\easy_install docutils pyramid_tm \
           pyramid_zodbconn pyramid_debugtoolbar nose coverage

.. _making_a_project:

Making a Project
================

Your next step is to create a project.  :app:`Pyramid` supplies a
variety of scaffolds to generate sample projects.  For this tutorial,
we will use the :term:`ZODB` -oriented scaffold named ``pyramid_zodb``.

The below instructions assume your current working directory is the
"virtualenv" named "pyramidtut".

On UNIX:

.. code-block:: text

  $ bin/paster create -t pyramid_zodb tutorial

On Windows:

.. code-block:: text

   c:\pyramidtut> Scripts\paster create -t pyramid_zodb tutorial

.. note:: If you are using Windows, the ``pyramid_zodb`` Paster scaffold
   doesn't currently deal gracefully with installation into a location
   that contains spaces in the path.  If you experience startup
   problems, try putting both the virtualenv and the project into
   directories that do not contain spaces in their paths.

Installing the Project in "Development Mode"
============================================

In order to do development on the project easily, you must "register"
the project as a development egg in your workspace using the
``setup.py develop`` command.  In order to do so, cd to the "tutorial"
directory you created in :ref:`making_a_project`, and run the
"setup.py develop" command using virtualenv Python interpreter.

On UNIX:

.. code-block:: text

  $ cd tutorial
  $ ../bin/python setup.py develop

On Windows:

.. code-block:: text

  C:\pyramidtut> cd tutorial
  C:\pyramidtut\tutorial> ..\Scripts\python setup.py develop

.. _running_tests:

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

On UNIX:

.. code-block:: text

  $ ../bin/nosetests --cover-package=tutorial --cover-erase --with-coverage

On Windows:

.. code-block:: text

  c:\pyramidtut\tutorial> ..\Scripts\nosetests --cover-package=tutorial ^
       --cover-erase --with-coverage

Looks like the code in the ``pyramid_zodb`` scaffold for ZODB projects is
missing some test coverage, particularly in the file named
``models.py``.

Visit the Application in a Browser
==================================

In a browser, visit `http://localhost:6543/ <http://localhost:6543>`_.  You
will see the generated application's default page.

One thing you'll notice is the "debug toolbar" icon on right hand side of the
page.  You can read more about the purpose of the icon at
:ref:`debug_toolbar`.  It allows you to get information about your
application while you develop.

Decisions the ``pyramid_zodb`` Scaffold Has Made For You
========================================================

Creating a project using the ``pyramid_zodb`` scaffold makes the following
assumptions:

- you are willing to use :term:`ZODB` as persistent storage

- you are willing to use :term:`traversal` to map URLs to code.

.. note::

   :app:`Pyramid` supports any persistent storage mechanism (e.g. a SQL
   database or filesystem files, etc).  :app:`Pyramid` also supports an
   additional mechanism to map URLs to code (:term:`URL dispatch`).  However,
   for the purposes of this tutorial, we'll only be using traversal and ZODB.

