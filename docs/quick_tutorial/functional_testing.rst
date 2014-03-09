.. _qtut_functional_testing:

===================================
06: Functional Testing with WebTest
===================================

Write end-to-end full-stack testing using ``webtest``.

Background
==========

Unit tests are a common and popular approach to test-driven development
(TDD.) In web applications, though, the templating and entire apparatus
of a web site are important parts of the delivered quality. We'd like a
way to test these.

WebTest is a Python package that does functional testing. With WebTest
you can write tests which simulate a full HTTP request against a WSGI
application, then test the information in the response. For speed
purposes, WebTest skips the setup/teardown of an actual HTTP server,
providing tests that run fast enough to be part of TDD.

Objectives
==========

- Write a test which checks the contents of the returned HTML

Steps
=====

#. First we copy the results of the previous step, as well as install
   the ``webtest`` package:

   .. code-block:: bash

    $ cd ..; cp -r unit_testing functional_testing; cd functional_testing
    $ $VENV/bin/python setup.py develop
    $ $VENV/bin/easy_install webtest

#. Let's extend ``unit_testing/tutorial/tests.py`` to include a
   functional test:

   .. literalinclude:: functional_testing/tutorial/tests.py
    :linenos:

#. Now run the tests:

   .. code-block:: bash


    $ $VENV/bin/nosetests tutorial
    .
    ----------------------------------------------------------------------
    Ran 2 tests in 0.141s

    OK

Analysis
========

We now have the end-to-end testing we were looking for. WebTest lets us
simply extend our existing ``nose``-based test approach with functional
tests that are reported in the same output. These new tests not only
cover our templating, but they didn't dramatically increase the
execution time of our tests.

Extra Credit
============

#. Why do our functional tests use ``b''``?