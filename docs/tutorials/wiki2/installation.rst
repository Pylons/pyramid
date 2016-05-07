.. _wiki2_installation:

============
Installation
============

Before you begin
----------------

This tutorial assumes that you have already followed the steps in
:ref:`installing_chapter`, except **do not create a virtual environment or
install Pyramid**.  Thereby you will satisfy the following requirements.

* A Python interpreter is installed on your operating system.
* You've satisfied the :ref:`requirements-for-installing-packages`.


Create directory to contain the project
---------------------------------------

We need a workspace for our project files.

On UNIX
^^^^^^^

.. code-block:: bash

    $ mkdir ~/pyramidtut

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\> mkdir pyramidtut


Create and use a virtual Python environment
-------------------------------------------

Next let's create a virtual environment workspace for our project.  We will use
the ``VENV`` environment variable instead of the absolute path of the virtual
environment.

On UNIX
^^^^^^^

.. code-block:: bash

   $ export VENV=~/pyramidtut
   $ python3 -m venv $VENV

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\> set VENV=c:\pyramidtut

Each version of Python uses different paths, so you will need to adjust the
path to the command for your Python version.

Python 2.7:

.. code-block:: doscon

   c:\> c:\Python27\Scripts\virtualenv %VENV%

Python 3.5:

.. code-block:: doscon

   c:\> c:\Python35\Scripts\python -m venv %VENV%


Upgrade ``pip`` and ``setuptools`` in the virtual environment
-------------------------------------------------------------

On UNIX
^^^^^^^

.. code-block:: bash

    $ $VENV/bin/pip install --upgrade pip setuptools

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\> %VENV%\Scripts\pip install --upgrade pip setuptools


Install Pyramid into the virtual Python environment
---------------------------------------------------

On UNIX
^^^^^^^

.. parsed-literal::

   $ $VENV/bin/pip install "pyramid==\ |release|\ "

On Windows
^^^^^^^^^^

.. parsed-literal::

   c:\\> %VENV%\\Scripts\\pip install "pyramid==\ |release|\ "


Install SQLite3 and its development packages
--------------------------------------------

If you used a package manager to install your Python or if you compiled
your Python from source, then you must install SQLite3 and its
development packages.  If you downloaded your Python as an installer
from https://www.python.org, then you already have it installed and can skip
this step.

If you need to install the SQLite3 packages, then, for example, using
the Debian system and ``apt-get``, the command would be the following:

.. code-block:: bash

   $ sudo apt-get install libsqlite3-dev


Change directory to your virtual Python environment
---------------------------------------------------

Change directory to the ``pyramidtut`` directory, which is both your workspace
and your virtual environment.

On UNIX
^^^^^^^

.. code-block:: bash

   $ cd pyramidtut

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\> cd pyramidtut


.. _sql_making_a_project:

Making a project
----------------

Your next step is to create a project.  For this tutorial we will use
the :term:`scaffold` named ``alchemy`` which generates an application
that uses :term:`SQLAlchemy` and :term:`URL dispatch`.

:app:`Pyramid` supplies a variety of scaffolds to generate sample projects. We
will use ``pcreate``, a script that comes with Pyramid, to create our project
using a scaffold.

By passing ``alchemy`` into the ``pcreate`` command, the script creates the
files needed to use SQLAlchemy. By passing in our application name
``tutorial``, the script inserts that application name into all the required
files. For example, ``pcreate`` creates the ``initialize_tutorial_db`` in the
``pyramidtut/bin`` directory.

The below instructions assume your current working directory is "pyramidtut".

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/pcreate -s alchemy tutorial

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut> %VENV%\Scripts\pcreate -s alchemy tutorial

.. note:: If you are using Windows, the ``alchemy`` scaffold may not deal
   gracefully with installation into a location that contains spaces in the
   path. If you experience startup problems, try putting both the virtual
   environment and the project into directories that do not contain spaces in
   their paths.


.. _installing_project_in_dev_mode:

Installing the project in development mode
------------------------------------------

In order to do development on the project easily, you must "register" the
project as a development egg in your workspace using the ``pip install -e .``
command. In order to do so, change directory to the ``tutorial`` directory that
you created in :ref:`sql_making_a_project`, and run the ``pip install -e .``
command using the virtual environment Python interpreter.

On UNIX
^^^^^^^

.. code-block:: bash

   $ cd tutorial
   $ $VENV/bin/pip install -e .

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut> cd tutorial
   c:\pyramidtut\tutorial> %VENV%\Scripts\pip install -e .

The console will show ``pip`` checking for packages and installing missing
packages. Success executing this command will show a line like the following:

.. code-block:: bash

   Successfully installed Chameleon-2.24 Mako-1.0.4 MarkupSafe-0.23 \
   Pygments-2.1.3 SQLAlchemy-1.0.12 pyramid-chameleon-0.3 \
   pyramid-debugtoolbar-2.4.2 pyramid-mako-1.0.2 pyramid-tm-0.12.1 \
   transaction-1.4.4 tutorial waitress-0.8.10 zope.sqlalchemy-0.7.6


.. _install-testing-requirements:

Install testing requirements
----------------------------

In order to run tests, we need to install the testing requirements. This is
done through our project's ``setup.py`` file, in the ``tests_require`` and
``extras_require`` stanzas, and by issuing the command below for your
operating system.

.. literalinclude:: src/installation/setup.py
   :language: python
   :linenos:
   :lineno-start: 22
   :lines: 22-26

.. literalinclude:: src/installation/setup.py
   :language: python
   :linenos:
   :lineno-start: 45
   :lines: 45-47

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/pip install -e ".[testing]"

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\pip install -e ".[testing]"


.. _sql_running_tests:

Run the tests
-------------

After you've installed the project in development mode as well as the testing
requirements, you may run the tests for the project. The following commands
provide options to py.test that specify the module for which its tests shall be
run, and to run py.test in quiet mode.

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/py.test -q

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\py.test -q

For a successful test run, you should see output that ends like this:

.. code-block:: bash

   ..
   2 passed in 0.44 seconds


Expose test coverage information
--------------------------------

You can run the ``py.test`` command to see test coverage information. This
runs the tests in the same way that ``py.test`` does, but provides additional
"coverage" information, exposing which lines of your project are covered by the
tests.

We've already installed the ``pytest-cov`` package into our virtual
environment, so we can run the tests with coverage.

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/py.test --cov --cov-report=term-missing

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\py.test --cov \
       --cov-report=term-missing

If successful, you will see output something like this:

.. code-block:: bash

   ======================== test session starts ========================
   platform Python 3.5.1, pytest-2.9.1, py-1.4.31, pluggy-0.3.1
   rootdir: /Users/stevepiercy/projects/pyramidtut/tutorial, inifile:
   plugins: cov-2.2.1
   collected 2 items

   tutorial/tests.py ..
   ------------------ coverage: platform Python 3.5.1 ------------------
   Name                               Stmts   Miss  Cover   Missing
   ----------------------------------------------------------------
   tutorial/__init__.py                   8      6    25%   7-12
   tutorial/models/__init__.py           22      0   100%
   tutorial/models/meta.py                5      0   100%
   tutorial/models/mymodel.py             8      0   100%
   tutorial/routes.py                     3      3     0%   1-3
   tutorial/scripts/__init__.py           0      0   100%
   tutorial/scripts/initializedb.py      26     26     0%   1-45
   tutorial/tests.py                     39      0   100%
   tutorial/views/__init__.py             0      0   100%
   tutorial/views/default.py             12      0   100%
   tutorial/views/notfound.py             4      4     0%   1-7
   ----------------------------------------------------------------
   TOTAL                                127     39    69%

   ===================== 2 passed in 0.57 seconds ======================

Our package doesn't quite have 100% test coverage.


.. _test_and_coverage_scaffold_defaults_sql:

Test and coverage scaffold defaults
-----------------------------------

Scaffolds include configuration defaults for ``py.test`` and test coverage.
These configuration files are ``pytest.ini`` and ``.coveragerc``, located at
the root of your package. Without these defaults, we would need to specify the
path to the module on which we want to run tests and coverage.

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/py.test --cov=tutorial tutorial/tests.py -q

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\py.test --cov=tutorial \
       --cov-report=term-missing tutorial\tests.py -q

py.test follows :ref:`conventions for Python test discovery
<pytest:test discovery>`, and the configuration defaults from the scaffold
tell ``py.test`` where to find the module on which we want to run tests and
coverage.

.. seealso:: See py.test's documentation for :ref:`pytest:usage` or invoke
   ``py.test -h`` to see its full set of options.


.. _initialize_db_wiki2:

Initializing the database
-------------------------

We need to use the ``initialize_tutorial_db`` :term:`console script` to
initialize our database.

.. note::

   The ``initialize_tutorial_db`` command does not perform a migration, but
   rather it simply creates missing tables and adds some dummy data. If you
   already have a database, you should delete it before running
   ``initialize_tutorial_db`` again.

.. note::

   The ``initialize_tutorial_db`` command is not performing a migration but
   rather simply creating missing tables and adding some dummy data. If you
   already have a database, you should delete it before running
   ``initialize_tutorial_db`` again.

Type the following command, making sure you are still in the ``tutorial``
directory (the directory with a ``development.ini`` in it):

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/initialize_tutorial_db development.ini

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\initialize_tutorial_db development.ini

The output to your console should be something like this:

.. code-block:: bash

   2016-04-09 00:53:37,801 INFO  [sqlalchemy.engine.base.Engine:1192][MainThread] SELECT CAST('test plain returns' AS VARCHAR(60)) AS anon_1
   2016-04-09 00:53:37,801 INFO  [sqlalchemy.engine.base.Engine:1193][MainThread] ()
   2016-04-09 00:53:37,802 INFO  [sqlalchemy.engine.base.Engine:1192][MainThread] SELECT CAST('test unicode returns' AS VARCHAR(60)) AS anon_1
   2016-04-09 00:53:37,802 INFO  [sqlalchemy.engine.base.Engine:1193][MainThread] ()
   2016-04-09 00:53:37,802 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] PRAGMA table_info("models")
   2016-04-09 00:53:37,803 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
   2016-04-09 00:53:37,803 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread]
   CREATE TABLE models (
           id INTEGER NOT NULL,
           name TEXT,
           value INTEGER,
           CONSTRAINT pk_models PRIMARY KEY (id)
   )


   2016-04-09 00:53:37,803 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
   2016-04-09 00:53:37,804 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT
   2016-04-09 00:53:37,805 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] CREATE UNIQUE INDEX my_index ON models (name)
   2016-04-09 00:53:37,805 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ()
   2016-04-09 00:53:37,806 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT
   2016-04-09 00:53:37,807 INFO  [sqlalchemy.engine.base.Engine:646][MainThread] BEGIN (implicit)
   2016-04-09 00:53:37,808 INFO  [sqlalchemy.engine.base.Engine:1097][MainThread] INSERT INTO models (name, value) VALUES (?, ?)
   2016-04-09 00:53:37,808 INFO  [sqlalchemy.engine.base.Engine:1100][MainThread] ('one', 1)
   2016-04-09 00:53:37,809 INFO  [sqlalchemy.engine.base.Engine:686][MainThread] COMMIT

Success!  You should now have a ``tutorial.sqlite`` file in your current
working directory. This is an SQLite database with a single table defined in it
(``models``).

.. _wiki2-start-the-application:

Start the application
---------------------

Start the application.

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/pserve development.ini --reload

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\pserve development.ini --reload

.. note::

   Your OS firewall, if any, may pop up a dialog asking for authorization
   to allow python to accept incoming network connections.

If successful, you will see something like this on your console:

.. code-block:: text

   Starting subprocess with file monitor
   Starting server in PID 82349.
   serving on http://127.0.0.1:6543

This means the server is ready to accept requests.


Visit the application in a browser
----------------------------------

In a browser, visit http://localhost:6543/. You will see the generated
application's default page.

One thing you'll notice is the "debug toolbar" icon on right hand side of the
page.  You can read more about the purpose of the icon at
:ref:`debug_toolbar`.  It allows you to get information about your
application while you develop.


Decisions the ``alchemy`` scaffold has made for you
---------------------------------------------------

Creating a project using the ``alchemy`` scaffold makes the following
assumptions:

- You are willing to use :term:`SQLAlchemy` as a database access tool.

- You are willing to use :term:`URL dispatch` to map URLs to code.

- You want to use zope.sqlalchemy_, pyramid_tm_, and the transaction_ packages
  to scope sessions to requests.

- You want to use pyramid_jinja2_ to render your templates. Different
  templating engines can be used, but we had to choose one to make this
  tutorial. See :ref:`available_template_system_bindings` for some options.

.. note::

   :app:`Pyramid` supports any persistent storage mechanism (e.g., object
   database or filesystem files). It also supports an additional mechanism to
   map URLs to code (:term:`traversal`). However, for the purposes of this
   tutorial, we'll only be using :term:`URL dispatch` and :term:`SQLAlchemy`.

.. _pyramid_jinja2:
   http://docs.pylonsproject.org/projects/pyramid-jinja2/en/latest/

.. _pyramid_tm:
   http://docs.pylonsproject.org/projects/pyramid-tm/en/latest/

.. _zope.sqlalchemy:
   https://pypi.python.org/pypi/zope.sqlalchemy

.. _transaction:
   http://zodb.readthedocs.org/en/latest/transactions.html
