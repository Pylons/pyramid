============
Installation
============

Preparation
===========

Follow the steps in :ref:`installing_chapter`, but name the virtualenv
directory ``pyramidtut``.

Preparation, UNIX
-----------------


#. Switch to the ``pyramidtut`` directory:

   .. code-block:: text

     $ cd pyramidtut

#. Install tutorial dependencies:

   .. code-block:: text

     $ $VENV/bin/easy_install docutils pyramid_tm pyramid_zodbconn \
               pyramid_debugtoolbar nose coverage

Preparation, Windows
--------------------


#. Switch to the ``pyramidtut`` directory:

   .. code-block:: text

     c:\> cd pyramidtut

#. Install tutorial dependencies:

   .. code-block:: text

     c:\pyramidtut> %VENV%\Scripts\easy_install docutils pyramid_tm \
           pyramid_zodbconn pyramid_debugtoolbar nose coverage

.. _making_a_project:

Make a Project
==============

Your next step is to create a project.  For this tutorial, we will use the
:term:`scaffold` named ``zodb``, which generates an application
that uses :term:`ZODB` and :term:`traversal`.  :app:`Pyramid`
supplies a variety of scaffolds to generate sample projects.

The below instructions assume your current working directory is the
"virtualenv" named "pyramidtut".

On UNIX:

.. code-block:: text

  $ $VENV/bin/pcreate -s zodb tutorial

On Windows:

.. code-block:: text

   c:\pyramidtut> %VENV%\Scripts\pcreate -s zodb tutorial

.. note:: You don't have to call it `tutorial` -- the code uses
   relative paths for imports and finding templates and static
   resources.

.. note:: If you are using Windows, the ``zodb`` scaffold
   doesn't currently deal gracefully with installation into a location
   that contains spaces in the path.  If you experience startup
   problems, try putting both the virtualenv and the project into
   directories that do not contain spaces in their paths.

Install the Project in "Development Mode"
=========================================

In order to do development on the project easily, you must "register"
the project as a development egg in your workspace using the
``setup.py develop`` command.  In order to do so, cd to the "tutorial"
directory you created in :ref:`making_a_project`, and run the
"setup.py develop" command using virtualenv Python interpreter.

On UNIX:

.. code-block:: text

  $ cd tutorial
  $ $VENV/bin/python setup.py develop

On Windows:

.. code-block:: text

  C:\pyramidtut> cd tutorial
  C:\pyramidtut\tutorial> %VENV%\Scripts\python setup.py develop

.. _running_tests:

Run the Tests
=============

After you've installed the project in development mode, you may run
the tests for the project.

On UNIX:

.. code-block:: text

  $ $VENV/bin/python setup.py test -q

On Windows:

.. code-block:: text

  c:\pyramidtut\tutorial> %VENV%\Scripts\python setup.py test -q

Expose Test Coverage Information
================================

You can run the ``nosetests`` command to see test coverage
information.  This runs the tests in the same way that ``setup.py
test`` does but provides additional "coverage" information, exposing
which lines of your project are "covered" (or not covered) by the
tests.

On UNIX:

.. code-block:: text

  $ $VENV/bin/nosetests --cover-package=tutorial --cover-erase --with-coverage

On Windows:

.. code-block:: text

  c:\pyramidtut\tutorial> %VENV%\Scripts\nosetests --cover-package=tutorial ^
       --cover-erase --with-coverage

Looks like the code in the ``zodb`` scaffold for ZODB projects is
missing some test coverage, particularly in the file named
``models.py``.

.. _wiki-start-the-application:

Start the Application
=====================

Start the application.

On UNIX:

.. code-block:: text

  $ $VENV/bin/pserve development.ini --reload

On Windows:

.. code-block:: text

  c:\pyramidtut\tutorial> %VENV%\Scripts\pserve development.ini --reload

.. note::

   Your OS firewall, if any, may pop up a dialog asking for authorization
   to allow python to accept incoming network connections.

Visit the Application in a Browser
==================================

In a browser, visit `http://localhost:6543/ <http://localhost:6543>`_.  You
will see the generated application's default page.

One thing you'll notice is the "debug toolbar" icon on right hand side of the
page.  You can read more about the purpose of the icon at
:ref:`debug_toolbar`.  It allows you to get information about your
application while you develop.

Decisions the ``zodb`` Scaffold Has Made For You
================================================

Creating a project using the ``zodb`` scaffold makes the following
assumptions:

- you are willing to use :term:`ZODB` as persistent storage

- you are willing to use :term:`traversal` to map URLs to code.

.. note::

   :app:`Pyramid` supports any persistent storage mechanism (e.g., a SQL
   database or filesystem files).  :app:`Pyramid` also supports an additional
   mechanism to map URLs to code (:term:`URL dispatch`).  However, for the
   purposes of this tutorial, we'll only be using traversal and ZODB.
