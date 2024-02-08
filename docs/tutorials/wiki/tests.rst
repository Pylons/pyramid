.. _wiki_adding_tests:

============
Adding Tests
============

We will now add tests for the models and the views and a few functional tests in the ``tests`` package.
Tests ensure that an application works, and that it continues to work when changes are made in the future.


Test harness
============

The project came bootstrapped with some tests and a basic harness.
These are located in the ``tests`` package at the top-level of the project.
It is a common practice to put tests into a ``tests`` package alongside the application package, especially as projects grow in size and complexity.
A useful convention is for each module in the application to contain a corresponding module in the ``tests`` package.
The test module would have the same name with the prefix ``test_``.

The harness consists of the following setup:

- The ``project.optional-dependencies`` stanza of ``pyproject.toml`` - controls the dependencies installed when testing.
  When the list is changed, it is necessary to re-run ``$VENV/bin/pip install -e ".[testing]"`` to ensure the new dependencies are installed.

- The ``tool.pytest.ini_options`` stanza of ``pyproject.toml`` controls basic ``pytest`` configuration, including where to find the tests.
  We have configured ``pytest`` to search for tests in the application package and in the ``tests`` package.

- The ``tool.coverage.run`` stanza of ``pyproject.toml`` controls coverage config.
  In our setup, it works with the ``pytest-cov`` plugin that we use via the ``--cov`` options to the ``pytest`` command.

- The ``testing.ini`` file is a mirror of ``development.ini`` and ``production.ini`` that contains settings used for executing the test suite.
  Most importantly, it contains the database connection information used by tests that require the database.

- The ``tests/conftest.py`` file defines the core fixtures available throughout our tests.
  The fixtures are explained in more detail in the following sections.
  Open ``tests/conftest.py`` and follow along.


Session-scoped test fixtures
----------------------------

- ``app_settings`` - the settings ``dict`` parsed from the ``testing.ini`` file that would normally be passed by ``pserve`` into your app's ``main`` function.

- ``app`` - the :app:`Pyramid` WSGI application, implementing the :class:`pyramid.interfaces.IRouter` interface.
  Most commonly this would be used for functional tests.


Per-test fixtures
-----------------

- ``tm`` - a :class:`transaction.TransactionManager` object controlling a transaction lifecycle.
  Generally other fixtures would join to the ``tm`` fixture to control their lifecycle and ensure they are aborted at the end of the test.

- ``testapp`` - a :class:`webtest.TestApp` instance wrapping the ``app`` and is used to sending requests into the application and return full response objects that can be inspected.
  The ``testapp`` is able to mutate the request environ such that the ``tm`` fixture is injected and used by any code that touches ``request.tm``.
  This should join the ``request.root`` ZODB model to the transaction manager as well, to enable rolling back changes to the database.
  The ``testapp`` maintains a cookiejar, so it can be used to share state across requests, as well as the transaction database connection.

- ``app_request`` - a :class:`pyramid.request.Request` object that can be used for more lightweight tests versus the full ``testapp``.
  The ``app_request`` can be passed to view functions and other code that need a fully functional request object.

- ``dummy_request`` - a :class:`pyramid.testing.DummyRequest` object that is very lightweight.
  This is a great object to pass to view functions that have minimal side-effects as it will be fast and simple.


Unit tests
==========

We can test individual APIs within our codebase to ensure they fulfill the expected contract that the rest of the application expects.
For example, we will test the password hashing features we added to ``tutorial.security`` and the rest of our models.

Create ``tests/test_models.py`` such that it appears as follows:

.. literalinclude:: src/tests/tests/test_models.py
    :linenos:
    :language: python


Integration tests
=================

We can directly execute the view code, bypassing :app:`Pyramid` and testing just the code that we have written.
These tests use dummy requests that we will prepare appropriately to set the conditions each view expects.

Update ``tests/test_views.py`` such that it appears as follows:

.. literalinclude:: src/tests/tests/test_views.py
    :linenos:
    :language: python


Functional tests
================

We will test the whole application, covering security aspects that are not tested in the unit and integration tests, like logging in, logging out, checking that the ``basic`` user cannot edit pages that it did not create, but that the ``editor`` user can, and so on.

Update ``tests/test_functional.py`` such that it appears as follows:

.. literalinclude:: src/tests/tests/test_functional.py
    :linenos:
    :language: python


Running the tests
=================

We can run these tests by using ``pytest`` similarly to how we did in :ref:`running_tests`.
Courtesy of the cookiecutter, our testing dependencies have already been satisfied.
``pytest`` and coverage have already been configured.
We can jump right to running tests.

On Unix:

.. code-block:: bash

    $VENV/bin/pytest -q

On Windows:

.. code-block:: doscon

    %VENV%\Scripts\pytest -q

The expected result should look like the following:

.. code-block:: text

    .........................
    25 passed in 3.87 seconds
