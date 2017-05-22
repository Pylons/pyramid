.. _wiki2_adding_tests:

============
Adding Tests
============

We will now add tests for the models and views as well as a few functional
tests in a new ``tests`` subpackage.  Tests ensure that an application works,
and that it continues to work when changes are made in the future.

The file ``tests.py`` was generated as part of the ``alchemy`` cookiecutter, but it
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

Create ``tutorial/tests/test_views.py`` such that it appears as follows:

.. literalinclude:: src/tests/tutorial/tests/test_views.py
   :linenos:
   :language: python

Create ``tutorial/tests/test_functional.py`` such that it appears as follows:

.. literalinclude:: src/tests/tutorial/tests/test_functional.py
   :linenos:
   :language: python

Create ``tutorial/tests/test_initdb.py`` such that it appears as follows:

.. literalinclude:: src/tests/tutorial/tests/test_initdb.py
   :linenos:
   :language: python

Create ``tutorial/tests/test_security.py`` such that it appears as follows:

.. literalinclude:: src/tests/tutorial/tests/test_security.py
   :linenos:
   :language: python

Create ``tutorial/tests/test_user_model.py`` such that it appears as follows:

.. literalinclude:: src/tests/tutorial/tests/test_user_model.py
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

We can run these tests similarly to how we did in :ref:`running_tests`, but first delete the SQLite database ``tutorial.sqlite``. If you do not delete the database, then you will see an integrity error when running the tests.

On UNIX:

.. code-block:: bash

   $ rm tutorial.sqlite
   $ $VENV/bin/py.test -q

On Windows:

.. code-block:: doscon

   c:\tutorial> del tutorial.sqlite
   c:\tutorial> %VENV%\Scripts\py.test -q

The expected result should look like the following:

.. code-block:: text

   ................................
   32 passed in 9.90 seconds

.. _webtest: http://docs.pylonsproject.org/projects/webtest/en/latest/
