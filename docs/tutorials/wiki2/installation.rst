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

.. _sql_making_a_project:

Making a Project
================

Your next step is to create a project.  :app:`Pyramid` supplies a
variety of scaffolds to generate sample projects.  We will use the
``alchemy`` scaffold, which generates an application
that uses :term:`SQLAlchemy` and :term:`URL dispatch`.

The below instructions assume your current working directory is the
"virtualenv" named "pyramidtut".

On UNIX:

.. code-block:: text

   $ bin/pcreate -s alchemy tutorial

On Windows:

.. code-block:: text

   c:\pyramidtut> Scripts\pcreate -s alchemy tutorial

.. note:: If you are using Windows, the ``alchemy``
   scaffold may not deal gracefully with installation into a
   location that contains spaces in the path.  If you experience
   startup problems, try putting both the virtualenv and the project
   into directories that do not contain spaces in their paths.

Success executing this command will end with a line to the console something
like::

   Please run the "populate_tutorial" script to set up the SQL 
   database before starting the application (e.g. 
   "$myvirtualenv/bin/populate_tutorial development.ini".)

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

Success executing this command will end with a line to the console something
like::

   Finished processing dependencies for tutorial==0.0

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

For a successful test run, you should see output like this::

  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.094s
 
  OK

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

If successful, you will see output something like this::

  .
  Name               Stmts   Miss  Cover   Missing
  ------------------------------------------------
  tutorial              11      7    36%   9-15
  tutorial.models       17      0   100%   
  tutorial.scripts       0      0   100%   
  tutorial.tests        24      0   100%   
  tutorial.views         6      0   100%   
  ------------------------------------------------
  TOTAL                 58      7    88%   
  ----------------------------------------------------------------------
  Ran 1 test in 0.459s

  OK

Looks like our package doesn't quite have 100% test coverage.

Starting the Application
========================

Start the application.

On UNIX:

.. code-block:: text

   $ ../bin/pserve development.ini --reload

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> ..\Scripts\pserve development.ini --reload

If successful, you will see something like this on your console::

  Starting subprocess with file monitor
  Starting server in PID 8966.
  Starting HTTP server on http://0.0.0.0:6543

This means the server is ready to accept requests.

Populating the Database
=======================

In a web browser, visit ``http://localhost:6543/``. 

You will see an error page with a title something like this::

  sqlalchemy.exc.OperationalError

  OperationalError: (OperationalError) no such table: models ...

Oh no!  Something isn't working!

This happens because we haven't populated the SQL database with any table
information yet.  We need to use the ``populate_tutorial`` :term:`console
script` to populate our database before we can see the page render correctly.

Stop the running Pyramid application by pressing ``ctrl-C`` in the console.
Make sure you're still in the ``tutorial`` directory (the directory with a
``development.ini`` in it) and type the following command:

On UNIX:

.. code-block:: text

   $ ../bin/populate_tutorial development.ini

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> ..\Scripts\populate_tutorial development.ini

The output to your console should be something like this::

  2011-11-26 14:42:25,012 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                PRAGMA table_info("models")
  2011-11-26 14:42:25,013 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
  2011-11-26 14:42:25,013 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
  CREATE TABLE models (
  	id INTEGER NOT NULL, 
  	name VARCHAR(255), 
  	value INTEGER, 
  	PRIMARY KEY (id), 
  	UNIQUE (name)
  )
  2011-11-26 14:42:25,013 INFO  [sqlalchemy.engine.base.Engine][MainThread] ()
  2011-11-26 14:42:25,135 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                COMMIT
  2011-11-26 14:42:25,137 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                BEGIN (implicit)
  2011-11-26 14:42:25,138 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                INSERT INTO models (name, value) VALUES (?, ?)
  2011-11-26 14:42:25,139 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                (u'one', 1)
  2011-11-26 14:42:25,140 INFO  [sqlalchemy.engine.base.Engine][MainThread] 
                                COMMIT

Success!  You should now have a ``tutorial.db`` file in your current working
directory.  This will be a SQLite database with a single table defined in it
(``models``).

Starting the Application (Again)
================================

Start the application again.

On UNIX:

.. code-block:: text

   $ ../bin/pserve development.ini --reload

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> ..\Scripts\pserve development.ini --reload

At this point, when you visit ``http://localhost:6543/`` in your web browser,
you will no longer see an error; instead you will see the generated
application's default page.

One thing you'll notice is the "debug toolbar" icon on right hand side of the
page.  You can read more about the purpose of the icon at
:ref:`debug_toolbar`.  It allows you to get information about your
application while you develop.

Decisions the ``alchemy`` Scaffold Has Made For You
=================================================================

Creating a project using the ``alchemy`` scaffold makes
the following assumptions:

- you are willing to use :term:`SQLAlchemy` as a database access tool

- you are willing to use :term:`url dispatch` to map URLs to code.

.. note::

   :app:`Pyramid` supports any persistent storage mechanism (e.g. object
   database or filesystem files, etc).  It also supports an additional
   mechanism to map URLs to code (:term:`traversal`).  However, for the
   purposes of this tutorial, we'll only be using url dispatch and
   SQLAlchemy.

