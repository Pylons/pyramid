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


Install SQLite3 and its development packages
--------------------------------------------

If you used a package manager to install your Python or if you compiled your Python from source, then you must install SQLite3 and its development packages.  If you downloaded your Python as an installer from https://www.python.org, then you already have it installed and can skip this step.

If you need to install the SQLite3 packages, then, for example, using the Debian system and ``apt-get``, the command would be the following:

.. code-block:: bash

    sudo apt-get install libsqlite3-dev


Install cookiecutter
--------------------
We will use a :term:`cookiecutter` to create a Python package project from a Python package project template.  See `Cookiecutter Installation <https://cookiecutter.readthedocs.io/en/latest/installation.html>`_ for instructions.


Generate a Pyramid project from a cookiecutter
----------------------------------------------

We will create a Pyramid project in your home directory for Unix or at the root for Windows. It is assumed you know the path to where you installed ``cookiecutter``. Issue the following commands and override the defaults in the prompts as follows.

On Unix
^^^^^^^

.. code-block:: bash

    cd ~
    cookiecutter gh:Pylons/pyramid-cookiecutter-starter --checkout 2.1-branch

On Windows
^^^^^^^^^^

.. code-block:: doscon

    cd \
    cookiecutter gh:Pylons/pyramid-cookiecutter-starter --checkout 2.1-branch

On all operating systems
^^^^^^^^^^^^^^^^^^^^^^^^
If prompted for the first item, accept the default ``yes`` by hitting return.

.. code-block:: text

    You've cloned ~/.cookiecutters/pyramid-cookiecutter-starter before.
    Is it okay to delete and re-clone it? [yes]: yes
    project_name [Pyramid Scaffold]: myproj
    repo_name [myproj]: tutorial
    Select template_language:
    1 - jinja2
    2 - chameleon
    3 - mako
    Choose from 1, 2, 3 [1]: 1
    Select backend:
    1 - none
    2 - sqlalchemy
    3 - zodb
    Choose from 1, 2, 3 [1]: 2


Change directory into your newly created project
------------------------------------------------

On Unix
^^^^^^^

.. code-block:: bash

    cd tutorial

On Windows
^^^^^^^^^^

.. code-block:: doscon

    cd tutorial


Set and use a ``VENV`` environment variable
-------------------------------------------

We will set the ``VENV`` environment variable to the absolute path of the virtual environment, and use it going forward.

On Unix
^^^^^^^

.. code-block:: bash

    export VENV=~/tutorial

On Windows
^^^^^^^^^^

.. code-block:: doscon

    set VENV=c:\tutorial


Create a virtual environment
----------------------------

On Unix
^^^^^^^

.. code-block:: bash

    python3 -m venv $VENV

On Windows
^^^^^^^^^^

.. code-block:: doscon

    python -m venv %VENV%


Upgrade packaging tools in the virtual environment
--------------------------------------------------

On Unix
^^^^^^^

.. code-block:: bash

    $VENV/bin/pip install --upgrade pip setuptools

On Windows
^^^^^^^^^^

.. code-block:: doscon

    %VENV%\Scripts\pip install --upgrade pip setuptools


.. _installing_project_in_dev_mode:

Installing the project in development mode
------------------------------------------

In order to do development on the project easily, you must "register" the project as a development egg in your workspace. We will install testing requirements at the same time. We do so with the following command.

On Unix
^^^^^^^

.. code-block:: bash

    $VENV/bin/pip install -e ".[testing]"

On Windows
^^^^^^^^^^

.. code-block:: doscon

    %VENV%\Scripts\pip install -e ".[testing]"

On all operating systems
^^^^^^^^^^^^^^^^^^^^^^^^

The console will show ``pip`` checking for packages and installing missing packages. Success executing this command will show a line like the following:

.. code-block:: bash

    Successfully installed Mako-1.3.2 PasteDeploy-3.1.0 Pygments-2.17.2 SQLAlchemy-2.0.25 WebTest-3.0.0 alembic-1.13.1 beautifulsoup4-4.12.3 coverage-7.4.1 greenlet-3.0.3 hupper-1.12.1 iniconfig-2.0.0 jinja2-3.1.3 markupsafe-2.1.5 packaging-23.2 plaster-1.1.2 plaster-pastedeploy-1.0.1 pluggy-1.4.0 pyramid-2.0.2 pyramid-debugtoolbar-4.12 pyramid-jinja2-2.10 pyramid-mako-1.1.0 pyramid-retry-2.1.1 pyramid-tm-2.5 pytest-8.0.0 pytest-cov-4.1.0 soupsieve-2.5 transaction-4.0 translationstring-1.4 tutorial-0.0 typing-extensions-4.9.0 venusian-3.1.0 waitress-2.1.2 webob-1.8.7 zope.deprecation-5.0 zope.interface-6.1 zope.sqlalchemy-3.1

Testing requirements are defined in our project's ``pyproject.toml`` file in a ``testing`` optional dependency.

.. literalinclude:: src/installation/pyproject.toml
    :language: python
    :lineno-match:
    :lines: 34-39


.. _initialize_db_wiki2:

Initialize and upgrade the database using Alembic
-------------------------------------------------

We use :term:`Alembic` to manage our database initialization and migrations.

Generate your first revision.

On Unix
^^^^^^^

.. code-block:: bash

    $VENV/bin/alembic -c development.ini revision --autogenerate -m "init"

On Windows
^^^^^^^^^^

.. code-block:: doscon

    %VENV%\Scripts\alembic -c development.ini revision --autogenerate -m "init"

The output to your console should be something like this:

.. code-block:: text

    2024-02-04 12:02:28,828 INFO  [alembic.runtime.migration:216][MainThread] Context impl SQLiteImpl.
    2024-02-04 12:02:28,828 INFO  [alembic.runtime.migration:219][MainThread] Will assume non-transactional DDL.
    2024-02-04 12:02:28,832 INFO  [alembic.autogenerate.compare:189][MainThread] Detected added table 'models'
    2024-02-04 12:02:28,832 INFO  [alembic.autogenerate.compare:633][MainThread] Detected added index ''my_index'' on '('name',)'
      Generating <somepath>/tutorial/tutorial/alembic/versions/20240204_4b6614165904.py ...  done

Upgrade to that revision.

On Unix
^^^^^^^

.. code-block:: bash

    $VENV/bin/alembic -c development.ini upgrade head

On Windows
^^^^^^^^^^

.. code-block:: doscon

    %VENV%\Scripts\alembic -c development.ini upgrade head

The output to your console should be something like this:

.. code-block:: text

    2024-02-04 12:03:04,738 INFO  [alembic.runtime.migration:216][MainThread] Context impl SQLiteImpl.
    2024-02-04 12:03:04,738 INFO  [alembic.runtime.migration:219][MainThread] Will assume non-transactional DDL.
    2024-02-04 12:03:04,739 INFO  [alembic.runtime.migration:622][MainThread] Running upgrade  -> 4b6614165904, init


.. _load_data_wiki2:

Load default data
-----------------

Load default data into the database using a :term:`console script`. Type the following command, making sure you are still in the ``tutorial`` directory (the directory with a ``development.ini`` in it):

On Unix
^^^^^^^

.. code-block:: bash

   $VENV/bin/initialize_tutorial_db development.ini

On Windows
^^^^^^^^^^

.. code-block:: doscon

   %VENV%\Scripts\initialize_tutorial_db development.ini

There should be no output to your console.
You should now have a ``tutorial.sqlite`` file in your current working directory.
This is an SQLite database with two tables defined in it, ``alembic_version`` and ``models``, where each table has a single record.


.. _sql_running_tests:

Run the tests
-------------

After you've installed the project in development mode as well as the testing
requirements, you may run the tests for the project. The following commands
provide options to ``pytest`` that specify the module for which its tests shall be
run, and to run ``pytest`` in quiet mode.

On Unix
^^^^^^^

.. code-block:: bash

    $VENV/bin/pytest -q

On Windows
^^^^^^^^^^

.. code-block:: doscon

    %VENV%\Scripts\pytest -q

For a successful test run, you should see output that ends like this:

.. code-block:: bash

    .....
    5 passed in 0.44 seconds


Expose test coverage information
--------------------------------

You can run the ``pytest`` command to see test coverage information. This
runs the tests in the same way that ``pytest`` does, but provides additional
:term:`coverage` information, exposing which lines of your project are covered by the
tests.

We've already installed the ``pytest-cov`` package into our virtual
environment, so we can run the tests with coverage.

On Unix
^^^^^^^

.. code-block:: bash

    $VENV/bin/pytest --cov --cov-report=term-missing

On Windows
^^^^^^^^^^

.. code-block:: doscon

    %VENV%\Scripts\pytest --cov --cov-report=term-missing

If successful, you will see output something like this:

.. code-block:: bash

    ====================================== test session starts ======================================
    platform darwin -- Python 3.11.7, pytest-8.0.0, pluggy-1.4.0
    rootdir: <somepath>/tutorial
    configfile: pyproject.toml
    testpaths: tutorial, tests
    plugins: cov-4.1.0
    collected 5 items

    tests/test_functional.py ..                                                               [ 40%]
    tests/test_views.py ...                                                                   [100%]

    ---------- coverage: platform darwin, python 3.11.7-final-0 ----------
    Name                                                 Stmts   Miss  Cover   Missing
    ----------------------------------------------------------------------------------
    tutorial/__init__.py                                     8      0   100%
    tutorial/alembic/env.py                                 23      4    83%   28-30, 56
    tutorial/alembic/versions/20240204_4b6614165904.py      12      2    83%   31-32
    tutorial/models/__init__.py                             32      2    94%   111, 122
    tutorial/models/meta.py                                  4      0   100%
    tutorial/models/mymodel.py                              10      0   100%
    tutorial/pshell.py                                       7      5    29%   5-13
    tutorial/routes.py                                       3      0   100%
    tutorial/scripts/__init__.py                             0      0   100%
    tutorial/scripts/initialize_db.py                       22     14    36%   15-16, 20-25, 29-38
    tutorial/views/__init__.py                               0      0   100%
    tutorial/views/default.py                               13      0   100%
    tutorial/views/notfound.py                               5      0   100%
    ----------------------------------------------------------------------------------
    TOTAL                                                  139     27    81%

    ================================= 5 passed, 6 warnings in 0.54s =================================

Our package doesn't quite have 100% test coverage.

.. _test_and_coverage_cookiecutter_defaults_sql:

Test and coverage cookiecutter defaults
---------------------------------------

The Pyramid cookiecutter includes configuration defaults for ``pytest`` and test coverage.
The configuration for ``pytest`` is in the ``pyproject.toml`` file in the ``[tool.pytest.ini_options]`` section.
Coverage is checked using the ``pytest-cov`` plugin, a wrapper around the `Coverage <https://coverage.readthedocs.io/en/latest/index.html>`_ tool.
Options affecting coverage are defined in ``[tool.coverage.run]``.

``pytest`` follows :ref:`conventions for Python test discovery <pytest:test discovery>`.
The configuration defaults from the cookiecutter tell ``pytest`` where to find the module on which we want to run tests and coverage.

.. seealso:: See ``pytest``'s documentation for :ref:`pytest:usage` or invoke ``pytest -h`` to see its full set of options.


.. _wiki2-start-the-application:

Start the application
---------------------

Start the application. See :ref:`what_is_this_pserve_thing` for more
information on ``pserve``.

On Unix
^^^^^^^

.. code-block:: bash

    $VENV/bin/pserve development.ini --reload

On Windows
^^^^^^^^^^

.. code-block:: doscon

    %VENV%\Scripts\pserve development.ini --reload

.. note::

   Your OS firewall, if any, may pop up a dialog asking for authorization
   to allow python to accept incoming network connections.

If successful, you will see something like this on your console:

.. code-block:: text

    Starting monitor for PID 68932.
    Starting server in PID 68932.
    Serving on http://localhost:6543
    Serving on http://localhost:6543

This means the server is ready to accept requests.


Visit the application in a browser
----------------------------------

In a browser, visit http://localhost:6543/. You will see the generated
application's default page.

One thing you'll notice is the "debug toolbar" icon on right hand side of the
page.  You can read more about the purpose of the icon at
:ref:`debug_toolbar`.  It allows you to get information about your
application while you develop.


Decisions the cookiecutter backend option ``sqlalchemy`` has made for you
-------------------------------------------------------------------------

When creating a project and selecting the backend option of ``sqlalchemy``, the
cookiecutter makes the following assumptions:

- You are willing to use SQLite for persistent storage, although almost any SQL database could be used with SQLAlchemy.

- You are willing to use :term:`SQLAlchemy` for a database access tool.

- You are willing to use :term:`Alembic` for a database migrations tool.

- You are willing to use a :term:`console script` for a data loading tool.

- You are willing to use :term:`URL dispatch` to map URLs to code.

- You want to use zope.sqlalchemy_, pyramid_tm_, and the transaction_ packages
  to scope sessions to requests.

.. note::

   :app:`Pyramid` supports any persistent storage mechanism (e.g., object
   database or filesystem files). It also supports an additional mechanism to
   map URLs to code (:term:`traversal`). However, for the purposes of this
   tutorial, we'll only be using :term:`URL dispatch` and :term:`SQLAlchemy`.

.. _pyramid_jinja2:
   https://docs.pylonsproject.org/projects/pyramid-jinja2/en/latest/

.. _pyramid_tm:
   https://docs.pylonsproject.org/projects/pyramid-tm/en/latest/

.. _zope.sqlalchemy:
   https://pypi.org/project/zope.sqlalchemy/

.. _transaction:
   https://zodb.readthedocs.io/en/latest/transactions.html
