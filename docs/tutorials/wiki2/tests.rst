.. _wiki2_adding_tests:

============
Adding Tests
============

We will now add tests for the models and views as well as a few functional
tests in a new ``tests`` package.  Tests ensure that an application works,
and that it continues to work when changes are made in the future.


Test harness
============

The project came bootstrapped with some tests and a basic harness.
These are located in the ``tests`` package at the top-level of the project.
It is a common practice to put tests into a ``tests`` package alongside the application package, especially as projects grow in size and complexity.
A useful convention is for each module in the application to contain a corresponding module in the ``tests`` package.
The test module would have the same name with the prefix ``test_``.

The harness consists of the following setup:

- ``[tool.pytest.ini_options]`` in ``pyproject.toml``.

  Controls basic ``pytest`` config including where to find the tests.
  We have configured ``pytest`` to search for tests in the application package and in the ``tests`` package.

- ``[tool.coverage.run]`` in ``pyproject.toml``.

  In our setup, it works with the ``pytest-cov`` plugin that we use via the ``--cov`` options to the ``pytest`` command.

- ``testing.ini``

  A mirror of ``development.ini`` and ``production.ini`` that contains settings used for executing the test suite.
  Most importantly, it contains the database connection information used by tests that require the database.

- ``testing`` optional dependencies in ``[project.optional-dependencies]`` section of ``pyproject.toml``.

  Controls the dependencies installed when testing.
  When the list is changed, it's necessary to re-run ``$VENV/bin/pip install -e ".[testing]"`` to ensure the new dependencies are installed.

- ``tests/conftest.py``.

  The core fixtures available throughout our tests.
  The fixtures are explained in more detail below.


Session-scoped test fixtures
----------------------------

- ``app_settings`` - the settings ``dict`` parsed from the ``testing.ini`` file that would normally be passed by ``pserve`` into your app's ``main`` function.

- ``dbengine`` - initializes the database.
  It's important to start each run of the test suite from a known state, and this fixture is responsible for preparing the database appropriately.
  This includes deleting any existing tables, running migrations, and potentially even loading some fixture data into the tables for use within the tests.

- ``app`` - the :app:`Pyramid` WSGI application, implementing the :class:`pyramid.interfaces.IRouter` interface.
  Most commonly this would be used for functional tests.


Per-test fixtures
-----------------

- ``tm`` - a :class:`transaction.TransactionManager` object controlling a transaction lifecycle.
  Generally other fixtures would join to the ``tm`` fixture to control their lifecycle and ensure they are aborted at the end of the test.

- ``dbsession`` - a :class:`sqlalchemy.orm.session.Session` object connected to the database.
  The session is scoped to the ``tm`` fixture.
  Any changes made will be aborted at the end of the test.

- ``testapp`` - a :class:`webtest.TestApp` instance wrapping the ``app`` and is used to sending requests into the application and return full response objects that can be inspected.
  The ``testapp`` is able to mutate the request environ such that the ``dbsession`` and ``tm`` fixtures are injected and used by any code that's touching ``request.dbsession`` and ``request.tm``.
  The ``testapp`` maintains a cookiejar, so it can be used to share state across requests, as well as the transaction database connection.

- ``app_request`` - a :class:`pyramid.request.Request` object that can be used for more lightweight tests versus the full ``testapp``.
  The ``app_request`` can be passed to view functions and other code that need a fully functional request object.

- ``dummy_request`` - a :class:`pyramid.testing.DummyRequest` object that is very lightweight.
  This is a great object to pass to view functions that have minimal side-effects as it'll be fast and simple.

- ``dummy_config`` — a :class:`pyramid.config.Configurator` object used as configuration by ``dummy_request``.
  Useful for mocking configuration like routes and security policies.


Modifying the fixtures
----------------------

We're going to make a few application-specific changes to the test harness.
It's always good to come up with patterns for things that are done often to avoid lots of boilerplate.

- Initialize the cookiejar with a CSRF token.
  Remember our application is using :class:`pyramid.csrf.CookieCSRFStoragePolicy`.

- ``testapp.get_csrf_token()`` - every POST/PUT/DELETE/PATCH request must contain the current CSRF token to prove to our app that the client isn't a third-party.
  So we want an easy way to grab the current CSRF token and add it to the request.

- ``testapp.login(params)`` - many pages are only accessible by logged in users so we want a simple way to login a user at the start of a test.

Update ``tests/conftest.py`` to look like the following, adding the highlighted lines:

.. literalinclude:: src/tests/tests/conftest.py
    :linenos:
    :emphasize-lines: 10,69-104,111,118-120
    :language: python


Unit tests
==========

We can test individual APIs within our codebase to ensure they fulfill the expected contract that the rest of the application expects.
For example, we'll test the password hashing features we added to the ``tutorial.models.User`` object.

Create ``tests/test_user_model.py`` such that it appears as follows:

.. literalinclude:: src/tests/tests/test_user_model.py
    :linenos:
    :language: python


Integration tests
=================

We can directly execute the view code, bypassing :app:`Pyramid` and testing just the code that we've written.
These tests use dummy requests that we'll prepare appropriately to set the conditions each view expects, such as adding dummy data to the session.
We'll be using ``dummy_config`` to configure the necessary routes, as well as setting the security policy as :class:`pyramid.testing.DummySecurityPolicy` to mock ``dummy_request.identity``.

Update ``tests/test_views.py`` such that it appears as follows:

.. literalinclude:: src/tests/tests/test_views.py
    :linenos:
    :language: python


Functional tests
================

We'll test the whole application, covering security aspects that are not tested in the unit and integration tests, like logging in, logging out, checking that the ``basic`` user cannot edit pages that it didn't create but the ``editor`` user can, and so on.

Update ``tests/test_functional.py`` such that it appears as follows:

.. literalinclude:: src/tests/tests/test_functional.py
    :linenos:
    :language: python


Running the tests
=================

On Unix:

.. code-block:: bash

    $VENV/bin/pytest -q

On Windows:

.. code-block:: doscon

    %VENV%\Scripts\pytest -q

The expected result should look like the following:

.. code-block:: text

    ...........................                                         [100%]
    27 passed in 6.91s

.. _webtest: https://docs.pylonsproject.org/projects/webtest/en/latest/
