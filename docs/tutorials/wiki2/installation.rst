============
Installation
============

Preparation
===========

Follow the steps in :ref:`installing_chapter`, but name the virtualenv
directory ``pyramidtut``.

Preparation, UNIX
-----------------

#. Install SQLite3 and its development packages if you don't already
   have them installed.  Usually this is via your system's package
   manager.  On a Debian system, this would be:

   .. code-block:: text

      $ sudo apt-get install libsqlite3-dev

#. Switch to the ``pyramidtut`` directory:

   .. code-block:: text

      $ cd pyramidtut


Preparation, Windows
--------------------

#. Switch to the ``pyramidtut`` directory:

   .. code-block:: text

      c:\> cd pyramidtut

.. _sql_making_a_project:

Making a Project
================

Your next step is to create a project.  For this tutorial, we will use the
:term:`scaffold` named ``alchemy``, which generates an application
that uses :term:`SQLAlchemy` and :term:`URL dispatch`.  :app:`Pyramid`
supplies a variety of scaffolds to generate sample projects.

The below instructions assume your current working directory is the
"virtualenv" named "pyramidtut".

On UNIX:

.. code-block:: text

   $ $VENV/bin/pcreate -s alchemy tutorial

On Windows:

.. code-block:: text

   c:\pyramidtut> %VENV%\pcreate -s alchemy tutorial

.. note:: If you are using Windows, the ``alchemy``
   scaffold may not deal gracefully with installation into a
   location that contains spaces in the path.  If you experience
   startup problems, try putting both the virtualenv and the project
   into directories that do not contain spaces in their paths.

Pcreate is a script that comes with Pyramid that helps by creating and organizing files 
needed as part of a Pyramid project. By passing in `alchemy` was are asking the script to 
create the files needed to use SQLAlchemy. By passing in our app name `tutorial` it goes through and 
places that application name in all the different files required. For example, the ``initialize_tutorial_db``
that is in the ``pyramidtut/bin`` directory that we use later in this tutorial was created by `pcreate`



.. _installing_project_in_dev_mode:

Installing the Project in "Development Mode"
============================================

In order to do development on the project easily, you must "register"
the project as a development egg in your workspace using the
``setup.py develop`` command.  In order to do so, cd to the `tutorial`
directory you created in :ref:`sql_making_a_project`, and run the
``setup.py develop`` command using the virtualenv Python interpreter.

On UNIX:

.. code-block:: text

   $ cd tutorial
   $ $VENV/bin/python setup.py develop

On Windows:

.. code-block:: text

   c:\pyramidtut> cd tutorial
   c:\pyramidtut\tutorial> %VENV%\Scripts\python setup.py develop

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

   $ $VENV/bin/python setup.py test -q

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\python setup.py test -q

For a successful test run, you should see output that ends like this::

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

To get this functionality working, we'll need to install the ``nose`` and
``coverage`` packages into our ``virtualenv``:

On UNIX:

.. code-block:: text

   $ $VENV/bin/easy_install nose coverage

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\easy_install nose coverage

Once ``nose`` and ``coverage`` are installed, we can actually run the
coverage tests.

On UNIX:

.. code-block:: text

   $ $VENV/bin/nosetests --cover-package=tutorial --cover-erase --with-coverage

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\nosetests --cover-package=tutorial \
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


.. _initialize_db_wiki2:

Initializing the Database
=========================

We need to use the ``initialize_tutorial_db`` :term:`console
script` to initialize our database.

Type the following command, make sure you are still in the ``tutorial``
directory (the directory with a ``development.ini`` in it):

On UNIX:

.. code-block:: text

   $ $VENV/bin/initialize_tutorial_db development.ini

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\initialize_tutorial_db development.ini

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

Success!  You should now have a ``tutorial.sqlite`` file in your current working
directory.  This will be a SQLite database with a single table defined in it
(``models``).

.. _wiki2-start-the-application:

Starting the Application
========================

Start the application.

On UNIX:

.. code-block:: text

   $ $VENV/bin/pserve development.ini --reload

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\pserve development.ini --reload

If successful, you will see something like this on your console::

  Starting subprocess with file monitor
  Starting server in PID 8966.
  Starting HTTP server on http://0.0.0.0:6543

This means the server is ready to accept requests.

At this point, when you visit ``http://localhost:6543/`` in your web browser,
you will see the generated application's default page.

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

- you want to use ``ZopeTransactionExtension`` and ``pyramid_tm`` to scope
  sessions to requests

.. note::

   :app:`Pyramid` supports any persistent storage mechanism (e.g. object
   database or filesystem files, etc).  It also supports an additional
   mechanism to map URLs to code (:term:`traversal`).  However, for the
   purposes of this tutorial, we'll only be using url dispatch and
   SQLAlchemy.

