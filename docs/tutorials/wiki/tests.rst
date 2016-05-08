.. _wiki_adding_tests:

============
Adding Tests
============

We will now add tests for the models and the views and a few functional tests
in ``tests.py``.  Tests ensure that an application works, and that it
continues to work when changes are made in the future.

Test the models
===============

We write tests for the ``model`` classes and the ``appmaker``.  Changing
``tests.py``, we'll write a separate test class for each ``model`` class, and
we'll write a test class for the ``appmaker``.

To do so, we'll retain the ``tutorial.tests.ViewTests`` class that was
generated as part of the ``zodb`` scaffold.  We'll add three test classes: one
for the ``Page`` model named ``PageModelTests``, one for the ``Wiki`` model
named ``WikiModelTests``, and one for the appmaker named ``AppmakerTests``.

Test the views
==============

We'll modify our ``tests.py`` file, adding tests for each view function we
added previously.  As a result, we'll *delete* the ``ViewTests`` class that
the ``zodb`` scaffold provided, and add four other test classes:
``ViewWikiTests``, ``ViewPageTests``, ``AddPageTests``, and ``EditPageTests``.
These test the ``view_wiki``, ``view_page``, ``add_page``, and ``edit_page``
views.

Functional tests
================

We'll test the whole application, covering security aspects that are not
tested in the unit tests, like logging in, logging out, checking that
the ``viewer`` user cannot add or edit pages, but the ``editor`` user
can, and so on.

View the results of all our edits to ``tests.py``
=================================================

Open the ``tutorial/tests.py`` module, and edit it such that it appears as
follows:

.. literalinclude:: src/tests/tutorial/tests.py
   :linenos:
   :language: python

Running the tests
=================

We can run these tests by using ``py.test`` similarly to how we did in
:ref:`running_tests`. Courtesy of the scaffold, our testing dependencies have
already been satisfied and ``py.test`` and coverage have already been
configured, so we can jump right to running tests.

On UNIX:

.. code-block:: text

   $ $VENV/bin/py.test -q

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\py.test -q

The expected result should look like the following:

.. code-block:: text

   ........................
   24 passed in 2.46 seconds
