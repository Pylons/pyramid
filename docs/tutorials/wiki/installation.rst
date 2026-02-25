.. _wiki_installation:

============
Installation
============


Before you begin
----------------

This tutorial assumes that you have already followed the steps in :ref:`installing_chapter`, except **do not create a virtual environment or
install Pyramid**.
Thereby you will satisfy the following requirements.

* A Python interpreter is installed on your operating system.
* You've satisfied the :ref:`requirements-for-installing-packages`.


Install cookiecutter
--------------------
We will use a :term:`cookiecutter` to create a Python package project from a Python package project template.
See `Cookiecutter Installation <https://cookiecutter.readthedocs.io/en/latest/installation.html>`_ for instructions.


Generate a Pyramid project from a cookiecutter
----------------------------------------------

We will create a Pyramid project in your home directory for Unix or at the root for Windows.
It is assumed you know the path to where you installed ``cookiecutter``.
Issue the following commands and override the defaults in the prompts as follows.


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

    You've downloaded ~/.cookiecutters/pyramid-cookiecutter-starter before.
    Is it okay to delete and re-download it? [yes]: yes
    project_name [Pyramid Scaffold]: myproj
    repo_name [myproj]: tutorial
    Select template_language:
    1 - jinja2
    2 - chameleon
    3 - mako
    Choose from 1, 2, 3 [1]: 2
    Select backend:
    1 - none
    2 - sqlalchemy
    3 - zodb
    Choose from 1, 2, 3 [1]: 3


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


.. _installing_project_in_dev_mode_zodb:

Installing the project in development mode
------------------------------------------

In order to work on the project, you must "register" the project as a development egg in your workspace.
We will install testing requirements at the same time.
We do so with the following command.


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

    Successfully installed BTrees-4.7.2 Chameleon-3.8.1 Mako-1.1.3 MarkupSafe-1.1.1 PasteDeploy-2.1.1 Pygments-2.7.3 WebTest-2.0.35 ZConfig-3.5.0 ZEO-5.2.2 ZODB-5.6.0 attrs-20.3.0 beautifulsoup4-4.9.3 cffi-1.14.4 coverage-5.3.1 hupper-1.10.2 iniconfig-1.1.1 packaging-20.8 persistent-4.6.4 plaster-1.0 plaster-pastedeploy-0.7 pluggy-0.13.1 py-1.10.0 pycparser-2.20 pyparsing-2.4.7 pyramid-1.10.5 pyramid-chameleon-0.3 pyramid-debugtoolbar-4.9 pyramid-mako-1.1.0 pyramid-retry-2.1.1 pyramid-tm-2.4 pyramid-zodbconn-0.8.1 pytest-6.2.1 pytest-cov-2.10.1 repoze.lru-0.7 six-1.15.0 soupsieve-2.1 toml-0.10.2 transaction-3.0.1 translationstring-1.4 tutorial venusian-3.0.0 waitress-1.4.4 webob-1.8.6 zc.lockfile-2.0 zdaemon-4.3 zodbpickle-2.0.0 zodburi-2.4.0 zope.deprecation-4.4.0 zope.interface-5.2.0

Testing requirements are defined in our project's ``pyproject.toml`` file, in the ``project:optional-dependencies`` stanza:

.. literalinclude:: src/installation/pyproject.toml
    :language: python
    :lineno-match:
    :lines: 33-38


.. _running_tests:

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

    ....
    4 passed in 0.49 seconds


Expose test coverage information
--------------------------------

You can run the ``pytest`` command to see test coverage information.
This runs the tests in the same way that ``pytest`` does, but provides additional :term:`coverage` information, exposing which lines of your project are covered by the tests.

We've already installed the ``pytest-cov`` package into our virtual environment, so we can run the tests with coverage.


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

    ======================== test session starts =========================
    platform darwin -- Python 3.9.0, pytest-6.2.1, py-1.10.0, pluggy-0.13.1
    rootdir: /filepath/tutorial, inifile: pytest.ini, testpaths: tutorial
    plugins: cov-2.10.1
    collected 4 items

    tests/test_functional.py ..                                     [ 50%]
    tests/test_views.py ..                                          [100%]

    ---------- coverage: platform darwin, python 3.7.3-final-0 -----------
    Name                          Stmts   Miss  Cover   Missing
    -----------------------------------------------------------
    tutorial/__init__.py             16      0   100%
    tutorial/models/__init__.py       8      0   100%
    tutorial/pshell.py                6      4    33%   5-12
    tutorial/routes.py                2      0   100%
    tutorial/views/__init__.py        0      0   100%
    tutorial/views/default.py         4      0   100%
    tutorial/views/notfound.py        4      0   100%
    -----------------------------------------------------------
    TOTAL                            40      4    90%

    ===================== 4 passed in 0.85 seconds =======================

Our package doesn't quite have 100% test coverage.


.. _test_and_coverage_cookiecutter_defaults_zodb:

Test and coverage cookiecutter defaults
---------------------------------------

The Pyramid cookiecutter includes configuration defaults for ``pytest`` and test coverage.
The configuration for ``pytest`` is in the ``pyroject.toml`` file in the ``tool.pytest.ini_options`` stanza.
Coverage is checked using the ``pytest--cov`` plugin, a wrapper around the `Coverage <https://coverage.readthedocs.io/en/latest/index.html>`_ tool.
Options affecting coverage are defined in the ``[tool.coverage.run]`` stanza of ``pyproject.toml``.

``pytest`` follows :ref:`conventions for Python test discovery <pytest:test discovery>`.
The configuration defaults from the cookiecutter tell ``pytest`` where to find the module on which we want to run tests:

.. literalinclude:: src/installation/pyproject.toml
    :language: python
    :lineno-match:
    :lines: 51-56

The ``tool.coverage.run`` stanza defines the code for which we want to collect and report coverage:

.. literalinclude:: src/installation/pyproject.toml
    :language: python
    :lineno-match:
    :lines: 46-49

.. seealso:: See ``pytest``'s documentation for :ref:`pytest:usage` or invoke ``pytest -h`` to see its full set of options.


.. _wiki-start-the-application:

Start the application
---------------------

Start the application.
See :ref:`what_is_this_pserve_thing` for more information on ``pserve``.


On Unix
^^^^^^^

.. code-block:: bash

    $VENV/bin/pserve development.ini --reload


On Windows
^^^^^^^^^^

.. code-block:: doscon

    %VENV%\Scripts\pserve development.ini --reload


.. note::

   Your OS firewall, if any, may pop up a dialog asking for authorization to allow python to accept incoming network connections.

If successful, you will see something like this on your console:

.. code-block:: text

    Starting monitor for PID 65233.
    Starting server in PID 65233.
    Serving on http://localhost:6543
    Serving on http://localhost:6543

This means the server is ready to accept requests.


Visit the application in a browser
----------------------------------

In a browser, visit http://localhost:6543/.
You will see the generated application's default page.

One thing you'll notice is the "debug toolbar" icon on right hand side of the page.
You can read more about the purpose of the icon at :ref:`debug_toolbar`.
It allows you to get information about your application while you develop.


Decisions the cookiecutter backend option ``zodb`` has made for you
-------------------------------------------------------------------

When creating a project and selecting the backend option of ``zodb``, the cookiecutter makes the following assumptions:

- You are willing to use :term:`ZODB` for persistent storage.
- You are willing to use :term:`traversal` to map URLs to code.
- You want to use `pyramid_zodbconn <https://docs.pylonsproject.org/projects/pyramid-zodbconn/en/latest/>`_, `pyramid_tm <https://docs.pylonsproject.org/projects/pyramid-tm/en/latest/>`_, and the `transaction <https://zodb.readthedocs.io/en/latest/transactions.html>`_ packages to manage connections and transactions with :term:`ZODB`.

.. note::

    :app:`Pyramid` supports any persistent storage mechanism (e.g., an SQL database or filesystem files).
    It also supports an additional mechanism to map URLs to code (:term:`URL dispatch`).
    However, for the purposes of this tutorial, we will only use :term:`traversal` and :term:`ZODB`.
