============
Installation
============

Before you begin
================

This tutorial assumes that you have already followed the steps in
:ref:`installing_chapter`, except **do not create a virtualenv or install
Pyramid**.  Thereby you will satisfy the following requirements.

* Python interpreter is installed on your operating system
* :term:`setuptools` or :term:`distribute` is installed
* :term:`virtualenv` is installed

Create directory to contain the project
---------------------------------------

We need a workspace for our project files.

On UNIX
^^^^^^^

.. code-block:: text

    $ mkdir ~/pyramidtut

On Windows
^^^^^^^^^^

.. code-block:: text

   c:\> mkdir pyramidtut

Create and use a virtual Python environment
-------------------------------------------

Next let's create a `virtualenv` workspace for our project.  We will
use the `VENV` environment variable instead of the absolute path of the
virtual environment.

On UNIX
^^^^^^^

.. code-block:: text

   $ export VENV=~/pyramidtut
   $ virtualenv $VENV
   New python executable in /home/foo/env/bin/python
   Installing setuptools.............done.

On Windows
^^^^^^^^^^

.. code-block:: text

   c:\> set VENV=c:\pyramidtut

Versions of Python use different paths, so you will need to adjust the
path to the command for your Python version.

Python 2.7:

.. code-block:: text

   c:\> c:\Python27\Scripts\virtualenv %VENV%

Python 3.2:

.. code-block:: text

   c:\> c:\Python32\Scripts\virtualenv %VENV%

Install Pyramid into the virtual Python environment
---------------------------------------------------

On UNIX
^^^^^^^

.. code-block:: text

   $ $VENV/bin/easy_install pyramid

On Windows
^^^^^^^^^^

.. code-block:: text

   c:\> %VENV%\Scripts\easy_install pyramid

Install SQLite3 and its development packages
--------------------------------------------

If you used a package manager to install your Python or if you compiled
your Python from source, then you must install SQLite3 and its
development packages.  If you downloaded your Python as an installer
from python.org, then you already have it installed and can proceed to
the next section :ref:`sql_making_a_project`..

If you need to install the SQLite3 packages, then, for example, using
the Debian system and apt-get, the command would be the following:

.. code-block:: text

   $ sudo apt-get install libsqlite3-dev

Change directory to your virtual Python environment
---------------------------------------------------

Change directory to the ``pyramidtut`` directory.

On UNIX
^^^^^^^

.. code-block:: text

   $ cd pyramidtut

On Windows
^^^^^^^^^^

.. code-block:: text

   c:\> cd pyramidtut

.. _sql_making_a_project:

Making a project
================

Your next step is to create a project.  For this tutorial we will use
the :term:`scaffold` named ``alchemy`` which generates an application
that uses :term:`SQLAlchemy` and :term:`URL dispatch`.

:app:`Pyramid` supplies a variety of scaffolds to generate sample
projects. We will use `pcreate`—a script that comes with Pyramid to
quickly and easily generate scaffolds, usually with a single command—to
create the scaffold for our project.

By passing `alchemy` into the `pcreate` command, the script creates
the files needed to use SQLAlchemy. By passing in our application name
`tutorial`, the script inserts that application name into all the
required files. For example, `pcreate` creates the
``initialize_tutorial_db`` in the ``pyramidtut/bin`` directory.

The below instructions assume your current working directory is "pyramidtut".

On UNIX
-------

.. code-block:: text

   $ $VENV/bin/pcreate -s alchemy tutorial

On Windows
----------

.. code-block:: text

   c:\pyramidtut> %VENV%\Scripts\pcreate -s alchemy tutorial

.. note:: If you are using Windows, the ``alchemy``
   scaffold may not deal gracefully with installation into a
   location that contains spaces in the path.  If you experience
   startup problems, try putting both the virtualenv and the project
   into directories that do not contain spaces in their paths.

.. _installing_project_in_dev_mode:

Installing the project in development mode
==========================================

In order to do development on the project easily, you must "register"
the project as a development egg in your workspace using the
``setup.py develop`` command.  In order to do so, cd to the `tutorial`
directory you created in :ref:`sql_making_a_project`, and run the
``setup.py develop`` command using the virtualenv Python interpreter.

On UNIX
-------

.. code-block:: text

   $ cd tutorial
   $ $VENV/bin/python setup.py develop

On Windows
----------

.. code-block:: text

   c:\pyramidtut> cd tutorial
   c:\pyramidtut\tutorial> %VENV%\Scripts\python setup.py develop

The console will show `setup.py` checking for packages and installing
missing packages. Success executing this command will show a line like
the following::

   Finished processing dependencies for tutorial==0.0

.. _sql_running_tests:

Run the tests
=============

After you've installed the project in development mode, you may run
the tests for the project.

On UNIX
-------

.. code-block:: text

   $ $VENV/bin/python setup.py test -q

On Windows
----------

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\python setup.py test -q

For a successful test run, you should see output that ends like this::

  .
  ----------------------------------------------------------------------
  Ran 1 test in 0.094s
 
  OK

Expose test coverage information
================================

You can run the ``nosetests`` command to see test coverage
information.  This runs the tests in the same way that ``setup.py
test`` does but provides additional "coverage" information, exposing
which lines of your project are "covered" (or not covered) by the
tests.

To get this functionality working, we'll need to install the ``nose`` and
``coverage`` packages into our ``virtualenv``:

On UNIX
-------

.. code-block:: text

   $ $VENV/bin/easy_install nose coverage

On Windows
----------

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\easy_install nose coverage

Once ``nose`` and ``coverage`` are installed, we can actually run the
coverage tests.

On UNIX
-------

.. code-block:: text

   $ $VENV/bin/nosetests --cover-package=tutorial --cover-erase --with-coverage

On Windows
----------

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\nosetests --cover-package=tutorial \
         --cover-erase --with-coverage

If successful, you will see output something like this::

    .
    Name                  Stmts   Miss  Cover   Missing
    ---------------------------------------------------
    tutorial.py              13      9    31%   13-21
    tutorial/models.py       12      0   100%   
    tutorial/scripts.py       0      0   100%   
    tutorial/views.py        11      0   100%   
    ---------------------------------------------------
    TOTAL                    36      9    75%   
    ----------------------------------------------------------------------
    Ran 2 tests in 0.643s

    OK

Looks like our package doesn't quite have 100% test coverage.

.. _initialize_db_wiki2:

Initializing the database
=========================

We need to use the ``initialize_tutorial_db`` :term:`console
script` to initialize our database.

Type the following command, making sure you are still in the ``tutorial``
directory (the directory with a ``development.ini`` in it):

On UNIX
-------

.. code-block:: text

   $ $VENV/bin/initialize_tutorial_db development.ini

On Windows
----------

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\initialize_tutorial_db development.ini

The output to your console should be something like this::

    2015-05-23 16:49:49,609 INFO  [sqlalchemy.engine.base.Engine:1192][MainThread] SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
    2015-05-23 16:49:49,609 INFO  [sqlalchemy.engine.base.Engine:1193][MainThread] ()
    2015-05-23 16:49:49,610 INFO  [sqlalchemy.engine.base.Engine:1192][MainThread] SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
    2015-05-23 16:49:49,610 INFO  [sqlalchemy.engine.base.Engine:1193][MainThread] ()
    2015-05-23 16:49:49,610 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] PRAGMA table_info("models")
    2015-05-23 16:49:49,610 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
    2015-05-23 16:49:49,612 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] 
    CREATE TABLE models (
            id INTEGER NOT NULL, 
            name TEXT, 
            value INTEGER, 
            PRIMARY KEY (id)
    )


    2015-05-23 16:49:49,612 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
    2015-05-23 16:49:49,613 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT
    2015-05-23 16:49:49,613 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] CREATE UNIQUE INDEX my_index ON models (name)
    2015-05-23 16:49:49,613 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
    2015-05-23 16:49:49,614 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT
    2015-05-23 16:49:49,616 INFO  [sqlalchemy.engine.base.Engine:646][MainThread] BEGIN (implicit)
    2015-05-23 16:49:49,617 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] INSERT INTO models (name, value) VALUES (?, ?)
    2015-05-23 16:49:49,617 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ('one', 1)
    2015-05-23 16:49:49,618 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT

Success!  You should now have a ``tutorial.sqlite`` file in your current working
directory.  This will be a SQLite database with a single table defined in it
(``models``).

.. _wiki2-start-the-application:

Start the application
=====================

Start the application.

On UNIX
-------

.. code-block:: text

   $ $VENV/bin/pserve development.ini --reload

On Windows
----------

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\pserve development.ini --reload

.. note::

   Your OS firewall, if any, may pop up a dialog asking for authorization
   to allow python to accept incoming network connections.

If successful, you will see something like this on your console::

  Starting subprocess with file monitor
  Starting server in PID 8966.
  Starting HTTP server on http://0.0.0.0:6543

This means the server is ready to accept requests.

Visit the application in a browser
==================================

In a browser, visit `http://localhost:6543/ <http://localhost:6543>`_.  You
will see the generated application's default page.

One thing you'll notice is the "debug toolbar" icon on right hand side of the
page.  You can read more about the purpose of the icon at
:ref:`debug_toolbar`.  It allows you to get information about your
application while you develop.

Decisions the ``alchemy`` scaffold has made for you
===================================================

Creating a project using the ``alchemy`` scaffold makes the following
assumptions:

- you are willing to use :term:`SQLAlchemy` as a database access tool

- you are willing to use :term:`URL dispatch` to map URLs to code

- you want to use ``ZopeTransactionExtension`` and ``pyramid_tm`` to scope
  sessions to requests

.. note::

   :app:`Pyramid` supports any persistent storage mechanism (e.g., object
   database or filesystem files). It also supports an additional
   mechanism to map URLs to code (:term:`traversal`).  However, for the
   purposes of this tutorial, we'll only be using URL dispatch and
   SQLAlchemy.
