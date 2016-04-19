.. _qtut_unit_testing:

=============================
05: Unit Tests and ``pytest``
=============================

Provide unit testing for our project's Python code.


Background
==========

As the mantra says, "Untested code is broken code." The Python community has
had a long culture of writing test scripts which ensure that your code works
correctly as you write it and maintain it in the future. Pyramid has always had
a deep commitment to testing, with 100% test coverage from the earliest
pre-releases.

Python includes a :ref:`unit testing framework
<python:unittest-minimal-example>` in its standard library. Over the years a
number of Python projects, such as :ref:`pytest <pytest:features>`, have
extended this framework with alternative test runners that provide more
convenience and functionality. The Pyramid developers use ``pytest``, which
we'll use in this tutorial.

Don't worry, this tutorial won't be pedantic about "test-driven development"
(TDD). We'll do just enough to ensure that, in each step, we haven't majorly
broken the code. As you're writing your code, you might find this more
convenient than changing to your browser constantly and clicking reload.

We'll also leave discussion of `pytest-cov
<http://pytest-cov.readthedocs.org/en/latest/>`_ for another section.


Objectives
==========

- Write unit tests that ensure the quality of our code.

- Install a Python package (``pytest``) which helps in our testing.


Steps
=====

#. First we copy the results of the previous step, as well as install the
   ``pytest`` package:

   .. code-block:: bash

    $ cd ..; cp -r debugtoolbar unit_testing; cd unit_testing
    $ $VENV/bin/pip install -e .
    $ $VENV/bin/pip install pytest

#. Now we write a simple unit test in ``unit_testing/tutorial/tests.py``:

   .. literalinclude:: unit_testing/tutorial/tests.py
    :linenos:

#. Now run the tests:

   .. code-block:: bash


    $ $VENV/bin/py.test tutorial/tests.py -q
    .
    1 passed in 0.14 seconds


Analysis
========

Our ``tests.py`` imports the Python standard unit testing framework. To make
writing Pyramid-oriented tests more convenient, Pyramid supplies some
``pyramid.testing`` helpers which we use in the test setup and teardown. Our
one test imports the view, makes a dummy request, and sees if the view returns
what we expect.

The ``tests.TutorialViewTests.test_hello_world`` test is a small example of a
unit test. First, we import the view inside each test. Why not import at the
top, like in normal Python code? Because imports can cause effects that break a
test. We'd like our tests to be in *units*, hence the name *unit* testing. Each
test should isolate itself to the correct degree.

Our test then makes a fake incoming web request, then calls our Pyramid view.
We test the HTTP status code on the response to make sure it matches our
expectations.

Note that our use of ``pyramid.testing.setUp()`` and
``pyramid.testing.tearDown()`` aren't actually necessary here; they are only
necessary when your test needs to make use of the ``config`` object (it's a
Configurator) to add stuff to the configuration state before calling the view.


Extra Credit
============

#. Change the test to assert that the response status code should be ``404``
   (meaning, not found). Run ``py.test`` again. Read the error report and see
   if you can decipher what it is telling you.

#. As a more realistic example, put the ``tests.py`` back as you found it, and
   put an error in your view, such as a reference to a non-existing variable.
   Run the tests and see how this is more convenient than reloading your
   browser and going back to your code.

#. Finally, for the most realistic test, read about Pyramid ``Response``
   objects and see how to change the response code. Run the tests and see how
   testing confirms the "contract" that your code claims to support.

#. How could we add a unit test assertion to test the HTML value of the
   response body?

#. Why do we import the ``hello_world`` view function *inside* the
   ``test_hello_world`` method instead of at the top of the module?

.. seealso:: See also :ref:`testing_chapter`
