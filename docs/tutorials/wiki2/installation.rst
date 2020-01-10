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
    cookiecutter gh:Pylons/pyramid-cookiecutter-starter --checkout master

On Windows
^^^^^^^^^^

.. code-block:: doscon

    cd \
    cookiecutter gh:Pylons/pyramid-cookiecutter-starter --checkout master

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

    Successfully installed Jinja2-2.10.3 Mako-1.1.0 MarkupSafe-1.1.1 \
    PasteDeploy-2.0.1 Pygments-2.5.2 SQLAlchemy-1.3.12 WebTest-2.0.33 \
    alembic-1.3.2 attrs-19.3.0 beautifulsoup4-4.8.2 coverage-5.0.1 \
    hupper-1.9.1 importlib-metadata-1.3.0 more-itertools-8.0.2 packaging-19.2 \
    plaster-1.0 plaster-pastedeploy-0.7 pluggy-0.13.1 py-1.8.1 \
    pyparsing-2.4.6 pyramid-1.10.4 pyramid-debugtoolbar-4.5.2 \
    pyramid-jinja2-2.8 pyramid-mako-1.1.0 pyramid-retry-2.1 pyramid-tm-2.4 \
    pytest-5.3.2 pytest-cov-2.8.1 python-dateutil-2.8.1 python-editor-1.0.4 \
    repoze.lru-0.7 six-1.13.0 soupsieve-1.9.5 transaction-3.0.0 \
    translationstring-1.3 tutorial venusian-3.0.0 waitress-1.4.1 \
    wcwidth-0.1.7 webob-1.8.5 zipp-0.6.0 zope.deprecation-4.4.0 \
    zope.interface-4.7.1 zope.sqlalchemy-1.2

Testing requirements are defined in our project's ``setup.py`` file, in the ``tests_require`` and ``extras_require`` stanzas.

.. literalinclude:: src/installation/setup.py
    :language: python
    :lineno-match:
    :lines: 25-29

.. literalinclude:: src/installation/setup.py
    :language: python
    :lineno-match:
    :lines: 49-51


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

    2019-12-28 00:46:03,850 INFO  [alembic.runtime.migration:154][MainThread] Context impl SQLiteImpl.
    2019-12-28 00:46:03,850 INFO  [alembic.runtime.migration:161][MainThread] Will assume non-transactional DDL.
    2019-12-28 00:46:03,853 INFO  [alembic.autogenerate.compare:134][MainThread] Detected added table 'models'
    2019-12-28 00:46:03,853 INFO  [alembic.autogenerate.compare:586][MainThread] Detected added index 'my_index' on '['name']'
      Generating <somepath>/tutorial/tutorial/alembic/versions/20191228_a8e203c3ce9c.py ...  done

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

    2019-12-28 00:52:12,158 INFO  [alembic.runtime.migration:154][MainThread] Context impl SQLiteImpl.
    2019-12-28 00:52:12,158 INFO  [alembic.runtime.migration:161][MainThread] Will assume non-transactional DDL.
    2019-12-28 00:52:12,160 INFO  [alembic.runtime.migration:513][MainThread] Running upgrade  -> a8e203c3ce9c, init


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
This is an SQLite database with three tables defined in it, ``alembic_version``, ``models``, and ``master``, where the first two tables each have single record inside of them.


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

    c:\tutorial> %VENV%\Scripts\pytest --cov --cov-report=term-missing

If successful, you will see output something like this:

.. code-block:: bash

    ======================== test session starts ========================
    platform -- Python 3.7.3, pytest-5.3.2, py-1.8.1, pluggy-0.13.1
    rootdir: <somepath>/tutorial, inifile: pytest.ini, testpaths: tutorial, tests
    plugins: cov-2.8.1
    collected 5 items

    tests/test_functional.py ..
    tests/test_views.py ...
    
    ---------- coverage: platform darwin, python 3.7.4-final-0 -----------
    Name                                                 Stmts   Miss  Cover   Missing
    ----------------------------------------------------------------------------------
    tutorial/__init__.py                                     8      0   100%
    tutorial/alembic/env.py                                 23      4    83%   28-30, 56
    tutorial/alembic/versions/20200106_8c274fe5f3c4.py      12      2    83%   31-32
    tutorial/models/__init__.py                             32      2    94%   71, 82
    tutorial/models/meta.py                                  5      0   100%
    tutorial/models/mymodel.py                               8      0   100%
    tutorial/pshell.py                                       7      5    29%   5-13
    tutorial/routes.py                                       3      0   100%
    tutorial/scripts/__init__.py                             0      0   100%
    tutorial/scripts/initialize_db.py                       22     14    36%   15-16, 20-25, 29-38
    tutorial/views/__init__.py                               0      0   100%
    tutorial/views/default.py                               12      0   100%
    tutorial/views/notfound.py                               4      0   100%
    ----------------------------------------------------------------------------------
    TOTAL                                                  136     27    80%

    ===================== 5 passed in 0.77 seconds ======================

Our package doesn't quite have 100% test coverage.


.. _test_and_coverage_cookiecutter_defaults_sql:

Test and coverage cookiecutter defaults
---------------------------------------

Cookiecutters include configuration defaults for ``pytest`` and test coverage.
These configuration files are ``pytest.ini`` and ``.coveragerc``, located at
the root of your package. Without these defaults, we would need to specify the
path to the module on which we want to run tests and coverage.

On Unix
^^^^^^^

.. code-block:: bash

    $VENV/bin/pytest --cov=tutorial tests -q

On Windows
^^^^^^^^^^

.. code-block:: doscon

    %VENV%\Scripts\pytest --cov=tutorial tutorial\tests.py -q

pytest follows :ref:`conventions for Python test discovery
<pytest:test discovery>`, and the configuration defaults from the cookiecutter
tell ``pytest`` where to find the module on which we want to run tests and
coverage.

.. seealso:: See ``pytest``'s documentation for :ref:`pytest:usage` or invoke
   ``pytest -h`` to see its full set of options.


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
