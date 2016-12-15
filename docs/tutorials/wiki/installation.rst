.. _wiki_installation:

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


Install cookiecutter
--------------------
We will use a :term:`cookiecutter` to create a Python package project from a Python package project template.  See `Cookiecutter Installation <https://cookiecutter.readthedocs.io/en/latest/installation.html>`_ for instructions.


Generate a Pyramid project from a cookiecutter
----------------------------------------------

Issue the command, following the default prompts from the command. It is assumed you know the path to ``cookiecutter``.

.. note::

   At the time of writing, the installation instructions for Cookiecutter suggest the optional use of ``sudo``, implying to install it in the system Python. We suggest that you install it in a virtual environment instead.

On UNIX
^^^^^^^

.. code-block:: bash

    $ cookiecutter https://github.com/Pylons/pyramid-cookiecutter-zodb

On Windows
^^^^^^^^^^

.. code-block:: doscon

    c:\> cookiecutter https://github.com/Pylons/pyramid-cookiecutter-zodb


Configure the project
---------------------

Change directory into your newly created project.

On UNIX
^^^^^^^

.. code-block:: bash

    $ cd myproj

On Windows
^^^^^^^^^^

.. code-block:: doscon

    c:\> cd myproj


Set and use a ``VENV`` environment variable
-------------------------------------------

We will set the ``VENV`` environment variable to the absolute path of the virtual environment, and use it going forward.

On UNIX
^^^^^^^

.. code-block:: bash

    $ export VENV=~/pyramidtut

On Windows
^^^^^^^^^^

.. code-block:: doscon

    c:\> set VENV=c:\pyramidtut





Create a virtual environment
----------------------------

On UNIX
^^^^^^^

.. code-block:: bash

    $ python3 -m venv env

On Windows
^^^^^^^^^^

.. code-block:: doscon

Each version of Python uses different paths, so you will need to adjust the path to the command for your Python version.

Python 2.7:

.. code-block:: doscon

    c:\> c:\Python27\Scripts\virtualenv %VENV%

Python 3.6:

.. code-block:: doscon

    c:\> c:\Python36\Scripts\python -m venv %VENV%


Upgrade packaging tools in the virtual environment
--------------------------------------------------

On UNIX
^^^^^^^

.. code-block:: bash

    $ $VENV/bin/pip install --upgrade pip setuptools wheel

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\> %VENV%\Scripts\pip install --upgrade pip setuptools wheel


.. _installing_project_in_dev_mode_zodb:

Installing the project in development mode
------------------------------------------

In order to do development on the project easily, you must "register" the project as a development egg in your workspace. We can also install testing requirements at the same time. We do so with the following command.

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/pip install -e ".[testing]"

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\pip install -e ".[testing]"

The console will show ``pip`` checking for packages and installing missing packages. Success executing this command will show a line like the following:

.. code-block:: bash

   Successfully installed BTrees-4.2.0 Chameleon-2.24 Mako-1.0.4 \
   MarkupSafe-0.23 Pygments-2.1.3 ZConfig-3.1.0 ZEO-4.2.0b1 ZODB-4.2.0 \
   ZODB3-3.11.0 mock-2.0.0 pbr-1.8.1 persistent-4.1.1 pyramid-chameleon-0.3 \
   pyramid-debugtoolbar-2.4.2 pyramid-mako-1.0.2 pyramid-tm-0.12.1 \
   pyramid-zodbconn-0.7 six-1.10.0 transaction-1.4.4 tutorial waitress-0.8.10 \
   zc.lockfile-1.1.0 zdaemon-4.1.0 zodbpickle-0.6.0 zodburi-2.0

Testing requirements are defined in our project's ``setup.py`` file, in the ``tests_require`` and ``extras_require`` stanzas.

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


.. _running_tests:

Run the tests
-------------

After you've installed the project in development mode as well as the testing requirements, you may run the tests for the project. The following commands provide options to py.test that specify the module for which its tests shall be run, and to run py.test in quiet mode.

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

   .
   1 passed in 0.24 seconds


Expose test coverage information
--------------------------------

You can run the ``py.test`` command to see test coverage information. This runs the tests in the same way that ``py.test`` does, but provides additional "coverage" information, exposing which lines of your project are covered by the tests.

We've already installed the ``pytest-cov`` package into our virtual environment, so we can run the tests with coverage.

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
   platform Python 3.6.0, pytest-2.9.1, py-1.4.31, pluggy-0.3.1
   rootdir: /Users/stevepiercy/projects/pyramidtut/tutorial, inifile:
   plugins: cov-2.2.1
   collected 1 items

   tutorial/tests.py .
   ------------------ coverage: platform Python 3.6.0 ------------------
   Name                   Stmts   Miss  Cover   Missing
   ----------------------------------------------------
   tutorial/__init__.py      12      7    42%   7-8, 14-18
   tutorial/models.py        10      6    40%   9-14
   tutorial/tests.py         12      0   100%
   tutorial/views.py          4      0   100%
   ----------------------------------------------------
   TOTAL                     38     13    66%

   ===================== 1 passed in 0.31 seconds ======================

Our package doesn't quite have 100% test coverage.


.. _test_and_coverage_scaffold_defaults_zodb:

Test and coverage cookiecutter defaults
---------------------------------------

Cookiecutters include configuration defaults for ``py.test`` and test coverage. These configuration files are ``pytest.ini`` and ``.coveragerc``, located at the root of your package. Without these defaults, we would need to specify the path to the module on which we want to run tests and coverage.

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/py.test --cov=tutorial tutorial/tests.py -q

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\py.test --cov=tutorial \
       --cov-report=term-missing tutorial\tests.py -q

py.test follows :ref:`conventions for Python test discovery <pytest:test discovery>`, and the configuration defaults from the scaffold tell ``py.test`` where to find the module on which we want to run tests and coverage.

.. seealso:: See py.test's documentation for :ref:`pytest:usage` or invoke ``py.test -h`` to see its full set of options.


.. _wiki-start-the-application:

Start the application
---------------------

Start the application. See :ref:`what_is_this_pserve_thing` for more information on ``pserve``.

On UNIX
^^^^^^^

.. code-block:: bash

   $ $VENV/bin/pserve development.ini --reload

On Windows
^^^^^^^^^^

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\pserve development.ini --reload

.. note::

   Your OS firewall, if any, may pop up a dialog asking for authorization to allow python to accept incoming network connections.

If successful, you will see something like this on your console:

.. code-block:: text

   Starting subprocess with file monitor
   Starting server in PID 82349.
   serving on http://127.0.0.1:6543

This means the server is ready to accept requests.


Visit the application in a browser
----------------------------------

In a browser, visit http://localhost:6543/. You will see the generated application's default page.

One thing you'll notice is the "debug toolbar" icon on right hand side of the page.  You can read more about the purpose of the icon at :ref:`debug_toolbar`.  It allows you to get information about your application while you develop.


Decisions the ``zodb`` scaffold has made for you
------------------------------------------------

Creating a project using the ``zodb`` scaffold makes the following assumptions:

- You are willing to use :term:`ZODB` as persistent storage.

- You are willing to use :term:`traversal` to map URLs to code.

- You want to use `pyramid_zodbconn <http://docs.pylonsproject.org/projects/pyramid-zodbconn/en/latest/>`_, `pyramid_tm <http://docs.pylonsproject.org/projects/pyramid-tm/en/latest/>`_, and the `transaction <http://zodb.readthedocs.org/en/latest/transactions.html>`_ packages
  to manage connections and transactions with :term:`ZODB`.

- You want to use `pyramid_chameleon <http://docs.pylonsproject.org/projects/pyramid-chameleon/en/latest/>`_ to render your templates. Different templating engines can be used, but we had to choose one to make this tutorial. See :ref:`available_template_system_bindings` for some options.

.. note::

   :app:`Pyramid` supports any persistent storage mechanism (e.g., an SQL database or filesystem files). It also supports an additional mechanism to map URLs to code (:term:`URL dispatch`). However, for the purposes of this tutorial, we'll only be using :term:`traversal` and :term:`ZODB`.
