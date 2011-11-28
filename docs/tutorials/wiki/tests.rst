============
Adding Tests
============

We will now add tests for the models and the views and a few functional
tests in the ``tests.py``.  Tests ensure that an application works, and
that it continues to work after some changes are made in the future.

Test the Models
===============

We write tests for the model classes and the appmaker.  Changing
``tests.py``, we'll write a separate test class for each model class, and
we'll write a test class for the ``appmaker``.

To do so, we'll retain the ``tutorial.tests.ViewTests`` class provided as a
result of the ``zodb`` project generator.  We'll add three test
classes: one for the ``Page`` model named ``PageModelTests``, one for the
``Wiki`` model named ``WikiModelTests``, and one for the appmaker named
``AppmakerTests``.

Test the Views
==============

We'll modify our ``tests.py`` file, adding tests for each view function we
added above.  As a result, we'll *delete* the ``ViewTests`` test in the file,
and add four other test classes: ``ViewWikiTests``, ``ViewPageTests``,
``AddPageTests``, and ``EditPageTests``.  These test the ``view_wiki``,
``view_page``, ``add_page``, and ``edit_page`` views respectively.


Functional tests
================

We test the whole application, covering security aspects that are not
tested in the unit tests, like logging in, logging out, checking that
the ``viewer`` user cannot add or edit pages, but the ``editor`` user
can, and so on.

View the results of all our edits to ``tests.py``
=================================================

Once we're done with the ``tests.py`` module, it will look a lot like the
below:

.. literalinclude:: src/tests/tutorial/tests.py
   :linenos:
   :language: python

Run the Tests
=============

We can run these tests by using ``setup.py test`` in the same way we did in
:ref:`running_tests`.  However, first we must edit our ``setup.py`` to
include a dependency on WebTest, which we've used in our ``tests.py``.
Change the ``requires`` list in ``setup.py`` to include ``WebTest``.

.. literalinclude:: src/tests/setup.py
   :linenos:
   :language: python
   :lines: 9-18

After we've added a dependency on WebTest in ``setup.py``, we need to rerun
``setup.py develop`` to get WebTest installed into our virtualenv.  Assuming
our shell's current working directory is the "tutorial" distribution
directory:

On UNIX:

.. code-block:: text

   $ ../bin/python setup.py develop

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> ..\Scripts\python setup.py develop

Once that command has completed successfully, we can run the tests
themselves:

On UNIX:

.. code-block:: text

   $ ../bin/python setup.py test -q

On Windows:

.. code-block:: text

   c:\pyramidtut\tutorial> ..\Scripts\python setup.py test -q

The expected result looks something like:

.. code-block:: text

   .........
   ----------------------------------------------------------------------
   Ran 23 tests in 1.653s
   
   OK
