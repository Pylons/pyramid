.. _qtut_functional_testing:

===================================
06: Functional Testing with WebTest
===================================

Write end-to-end full-stack testing using ``webtest``.


Background
==========

Unit tests are a common and popular approach to test-driven development (TDD).
In web applications, though, the templating and entire apparatus of a web site
are important parts of the delivered quality. We'd like a way to test these.

`WebTest <http://docs.pylonsproject.org/projects/webtest/en/latest/>`_ is a
Python package that does functional testing. With WebTest you can write tests
which simulate a full HTTP request against a WSGI application, then test the
information in the response. For speed purposes, WebTest skips the
setup/teardown of an actual HTTP server, providing tests that run fast enough
to be part of TDD.


Objectives
==========

- Write a test which checks the contents of the returned HTML.


Steps
=====

#. First we copy the results of the previous step, as well as install the
   ``webtest`` package:

   .. code-block:: bash

    $ cd ..; cp -r unit_testing functional_testing; cd functional_testing
    $ $VENV/bin/pip install -e .
    $ $VENV/bin/pip install webtest

#. Let's extend ``functional_testing/tutorial/tests.py`` to include a
   functional test:

   .. literalinclude:: functional_testing/tutorial/tests.py
    :linenos:

   Be sure this file is not executable, or ``pytest`` may not include your
   tests.
   
#. Now run the tests:

   .. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py -q
    ..
    2 passed in 0.25 seconds


Analysis
========

We now have the end-to-end testing we were looking for. WebTest lets us simply
extend our existing ``pytest``-based test approach with functional tests that
are reported in the same output. These new tests not only cover our templating,
but they didn't dramatically increase the execution time of our tests.


Extra credit
============

#. Why do our functional tests use ``b''``?
