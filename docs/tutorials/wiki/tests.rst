.. _wiki_adding_tests:

============
Adding Tests
============

We will now add tests for the models and the views and a few functional tests in ``tests/test_it.py``.
Tests ensure that an application works, and that it continues to work when changes are made in the future.


Test the models
===============

We write tests for the ``model`` classes and the ``appmaker``.
We will modify our ``test_it.py`` file, writing a separate test class for each ``model`` class.
We will also write a test class for the ``appmaker``.

We will add three test classes, one for each of the following:

-   the ``Page`` model named ``PageModelTests``
-   the ``Wiki`` model named ``WikiModelTests``
-   the appmaker named ``AppmakerTests``


Test the views
==============

We will modify our ``test_it.py`` file, adding tests for each view function that we added previously.
As a result, we will delete the ``ViewTests`` class that the ``zodb`` backend option provided, and add four other test classes: ``ViewWikiTests``, ``ViewPageTests``, ``AddPageTests``, and ``EditPageTests``.
These test the ``view_wiki``, ``view_page``, ``add_page``, and ``edit_page`` views.


Functional tests
================

We will test the whole application, covering security aspects that are not tested in the unit tests, such as logging in, logging out, checking that the ``viewer`` user cannot add or edit pages, but the ``editor`` user can, and so on.
As a result we will add two test classes, ``SecurityTests`` and ``FunctionalTests``.


View the results of all our edits to ``tests/test_it.py``
=========================================================

Open the ``tests/test_it.py`` module, and edit it such that it appears as follows:

.. literalinclude:: src/tests/tests/test_it.py
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
    25 passed in 6.87 seconds
