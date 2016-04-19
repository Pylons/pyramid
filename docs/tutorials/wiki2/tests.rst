.. _wiki2_adding_tests:

============
Adding Tests
============

We will now add tests for the models and views as well as a few functional
tests in a new ``tests`` subpackage.  Tests ensure that an application works,
and that it continues to work when changes are made in the future.

The file ``tests.py`` was generated as part of the ``alchemy`` scaffold, but it
is a common practice to put tests into a ``tests`` subpackage, especially as
projects grow in size and complexity.  Each module in the test subpackage
should contain tests for its corresponding module in our application.  Each
corresponding pair of modules should have the same names, except the test
module should have the prefix ``test_``.

Start by deleting ``tests.py``, then create a new directory to contain our new
tests as well as a new empty file ``tests/__init__.py``.

.. warning::

   It is very important when refactoring a Python module into a package to be
   sure to delete the cache files (``.pyc`` files or ``__pycache__`` folders)
   sitting around! Python will prioritize the cache files before traversing
   into folders, using the old code, and you will wonder why none of your
   changes are working!


Test the views
==============

We'll create a new ``tests/test_views.py`` file, adding a ``BaseTest`` class
used as the base for other test classes. Next we'll add tests for each view
function we previously added to our application. We'll add four test classes:
``ViewWikiTests``, ``ViewPageTests``, ``AddPageTests``, and ``EditPageTests``.
These test the ``view_wiki``, ``view_page``, ``add_page``, and ``edit_page``
views.


Functional tests
================

We'll test the whole application, covering security aspects that are not tested
in the unit tests, like logging in, logging out, checking that the ``basic``
user cannot edit pages that it didn't create but the ``editor`` user can, and
so on.


View the results of all our edits to ``tests`` subpackage
=========================================================

Open ``tutorial/tests/test_views.py``, and edit it such that it appears as
follows:

.. literalinclude:: src/tests/tutorial/tests/test_views.py
   :linenos:
   :language: python

Open ``tutorial/tests/test_functional.py``, and edit it such that it appears as
follows:

.. literalinclude:: src/tests/tutorial/tests/test_functional.py
   :linenos:
   :language: python


.. note::

   We're utilizing the excellent WebTest_ package to do functional testing of
   the application. This is defined in the ``tests_require`` section of our
   ``setup.py``. Any other dependencies needed only for testing purposes can be
   added there and will be installed automatically when running
   ``setup.py test``.


Running the tests
=================

We can run these tests similarly to how we did in :ref:`running_tests`:

On UNIX:

.. code-block:: bash

   $ $VENV/bin/py.test -q

On Windows:

.. code-block:: doscon

   c:\pyramidtut\tutorial> %VENV%\Scripts\py.test -q

The expected result should look like the following:

.. code-block:: text

   ......................
   22 passed, 1 pytest-warnings in 5.81 seconds

.. note:: If you use Python 3 during this tutorial, you will see deprecation
   warnings in the output, which we will choose to ignore. In making this
   tutorial run on both Python 2 and 3, the authors prioritized simplicity and
   focus for the learner over accommodating warnings. In your own app or as
   extra credit, you may choose to either drop Python 2 support or hack your
   code to work without warnings on both Python 2 and 3.

.. _webtest: http://docs.pylonsproject.org/projects/webtest/en/latest/
