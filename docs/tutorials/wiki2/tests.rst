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

We will move parts of ``tests.py`` into appropriate new files in the ``tests``
subpackage, and add several new tests.

Start by creating a new directory and a new empty file ``tests/__init__.py``.


Test the views
==============

We'll create a new ``tests/test_views.py`` file, adding tests for each view
function we previously added to our application.  As a result, we'll *delete*
the ``ViewTests`` class that the ``alchemy`` scaffold provided, and add four
other test classes: ``ViewWikiTests``, ``ViewPageTests``, ``AddPageTests``, and
``EditPageTests``. These test the ``view_wiki``, ``view_page``, ``add_page``,
and ``edit_page`` views.


Functional tests
================

We'll test the whole application, covering security aspects that are not
tested in the unit tests, like logging in, logging out, checking that
the ``viewer`` user cannot add or edit pages, but the ``editor`` user
can, and so on.


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


Running the tests
=================

We can run these tests by using ``setup.py test`` in the same way we did in
:ref:`running_tests`.  However, first we must edit our ``setup.py`` to include
a dependency on `WebTest
<http://docs.pylonsproject.org/projects/webtest/en/latest/>`_, which we've used
in our ``tests.py``.  Change the ``requires`` list in ``setup.py`` to include
``WebTest``.

.. literalinclude:: src/tests/setup.py
   :linenos:
   :language: python
   :lines: 11-22
   :emphasize-lines: 11

After we've added a dependency on WebTest in ``setup.py``, we need to run
``setup.py develop`` to get WebTest installed into our virtualenv.  Assuming
our shell's current working directory is the "tutorial" distribution directory:

On UNIX:

.. code-block:: bash

   $ $VENV/bin/python setup.py develop

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\python setup.py develop

Once that command has completed successfully, we can run the tests themselves:

On UNIX:

.. code-block:: bash

   $ $VENV/bin/python setup.py test -q

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> %VENV%\Scripts\python setup.py test -q

The expected result should look like the following:

.. code-block:: text

   ....................
   ----------------------------------------------------------------------
   Ran 20 tests in 0.524s

   OK

   Process finished with exit code 0
