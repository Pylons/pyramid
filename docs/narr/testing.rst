.. index::
   single: unit testing
   single: integration testing
   single: functional testing

.. _testing_chapter:

Unit, Integration, and Functional Testing
=========================================

*Unit testing* is, not surprisingly, the act of testing a "unit" in your
application.  In this context, a "unit" is often a function or a method of a
class instance.  The unit is also referred to as a "unit under test".

The goal of a single unit test is to test **only** some permutation of the
"unit under test".  If you write a unit test that aims to verify the result
of a particular codepath through a Python function, you need only be
concerned about testing the code that *lives in the function body itself*.
If the function accepts a parameter that represents a complex application
"domain object" (such as a resource, a database connection, or an SMTP
server), the argument provided to this function during a unit test *need not
be* and likely *should not be* a "real" implementation object.  For example,
although a particular function implementation may accept an argument that
represents an SMTP server object, and the function may call a method of this
object when the system is operating normally that would result in an email
being sent, a unit test of this codepath of the function does *not* need to
test that an email is actually sent.  It just needs to make sure that the
function calls the method of the object provided as an argument that *would*
send an email if the argument happened to be the "real" implementation of an
SMTP server object.

An *integration test*, on the other hand, is a different form of testing in
which the interaction between two or more "units" is explicitly tested.
Integration tests verify that the components of your application work
together.  You *might* make sure that an email was actually sent in an
integration test.

A *functional test* is a form of integration test in which the application is
run "literally".  You would *have to* make sure that an email was actually
sent in a functional test, because it tests your code end to end.

It is often considered best practice to write each type of tests for any
given codebase.  Unit testing often provides the opportunity to obtain better
"coverage": it's usually possible to supply a unit under test with arguments
and/or an environment which causes *all* of its potential codepaths to be
executed.  This is usually not as easy to do with a set of integration or
functional tests, but integration and functional testing provides a measure of
assurance that your "units" work together, as they will be expected to when
your application is run in production.

The suggested mechanism for unit and integration testing of a :app:`Pyramid`
application is the Python :mod:`unittest` module.  Although this module is
named :mod:`unittest`, it is actually capable of driving both unit and
integration tests.  A good :mod:`unittest` tutorial is available within `Dive
Into Python <http://diveintopython.nfshost.com/unit_testing/index.html>`_ by Mark
Pilgrim.

:app:`Pyramid` provides a number of facilities that make unit, integration,
and functional tests easier to write.  The facilities become particularly
useful when your code calls into :app:`Pyramid` -related framework functions.

.. index::
   single: test setup
   single: test tear down
   single: unittest

.. _test_setup_and_teardown:

Test Set Up and Tear Down
--------------------------

:app:`Pyramid` uses a "global" (actually :term:`thread local`) data structure
to hold on to two items: the current :term:`request` and the current
:term:`application registry`.  These data structures are available via the
:func:`pyramid.threadlocal.get_current_request` and
:func:`pyramid.threadlocal.get_current_registry` functions, respectively.
See :ref:`threadlocals_chapter` for information about these functions and the
data structures they return.

If your code uses these ``get_current_*`` functions or calls :app:`Pyramid`
code which uses ``get_current_*`` functions, you will need to call
:func:`pyramid.testing.setUp` in your test setup and you will need to call
:func:`pyramid.testing.tearDown` in your test teardown.
:func:`~pyramid.testing.setUp` pushes a registry onto the :term:`thread
local` stack, which makes the ``get_current_*`` functions work.  It returns a
:term:`Configurator` object which can be used to perform extra configuration
required by the code under test.  :func:`~pyramid.testing.tearDown` pops the
thread local stack.

Normally when a Configurator is used directly with the ``main`` block of
a Pyramid application, it defers performing any "real work" until its
``.commit`` method is called (often implicitly by the
:meth:`pyramid.config.Configurator.make_wsgi_app` method).  The
Configurator returned by :func:`~pyramid.testing.setUp` is an
*autocommitting* Configurator, however, which performs all actions
implied by methods called on it immediately.  This is more convenient
for unit-testing purposes than needing to call
:meth:`pyramid.config.Configurator.commit` in each test after adding
extra configuration statements.

The use of the :func:`~pyramid.testing.setUp` and
:func:`~pyramid.testing.tearDown` functions allows you to supply each unit
test method in a test case with an environment that has an isolated registry
and an isolated request for the duration of a single test.  Here's an example
of using this feature:

.. code-block:: python
   :linenos:

   import unittest
   from pyramid import testing

   class MyTest(unittest.TestCase):
       def setUp(self):
           self.config = testing.setUp()

       def tearDown(self):
           testing.tearDown()

The above will make sure that
:func:`~pyramid.threadlocal.get_current_registry` called within a test
case method of ``MyTest`` will return the :term:`application registry`
associated with the ``config`` Configurator instance.  Each test case
method attached to ``MyTest`` will use an isolated registry.

The :func:`~pyramid.testing.setUp` and :func:`~pyramid.testing.tearDown`
functions accepts various arguments that influence the environment of the
test.  See the :ref:`testing_module` chapter for information about the extra
arguments supported by these functions.

If you also want to make :func:`~pyramid.get_current_request` return something
other than ``None`` during the course of a single test, you can pass a
:term:`request` object into the :func:`pyramid.testing.setUp` within the
``setUp`` method of your test:

.. code-block:: python
   :linenos:

   import unittest
   from pyramid import testing

   class MyTest(unittest.TestCase):
       def setUp(self):
           request = testing.DummyRequest()
           self.config = testing.setUp(request=request)

       def tearDown(self):
           testing.tearDown()

If you pass a :term:`request` object into :func:`pyramid.testing.setUp`
within your test case's ``setUp``, any test method attached to the
``MyTest`` test case that directly or indirectly calls
:func:`~pyramid.threadlocal.get_current_request` will receive the request
object.  Otherwise, during testing,
:func:`~pyramid.threadlocal.get_current_request` will return ``None``.
We use a "dummy" request implementation supplied by
:class:`pyramid.testing.DummyRequest` because it's easier to construct
than a "real" :app:`Pyramid` request object.

What?
~~~~~

Thread local data structures are always a bit confusing, especially when
they're used by frameworks.  Sorry.  So here's a rule of thumb: if you don't
*know* whether you're calling code that uses the
:func:`~pyramid.threadlocal.get_current_registry` or
:func:`~pyramid.threadlocal.get_current_request` functions, or you don't care
about any of this, but you still want to write test code, just always call
:func:`pyramid.testing.setUp` in your test's ``setUp`` method and
:func:`pyramid.testing.tearDown` in your tests' ``tearDown`` method.  This
won't really hurt anything if the application you're testing does not call
any ``get_current*`` function.

.. index::
   single: pyramid.testing
   single: Configurator testing API

Using the ``Configurator`` and ``pyramid.testing`` APIs in Unit Tests
---------------------------------------------------------------------

The ``Configurator`` API and the ``pyramid.testing`` module provide a number
of functions which can be used during unit testing.  These functions make
:term:`configuration declaration` calls to the current :term:`application
registry`, but typically register a "stub" or "dummy" feature in place of the
"real" feature that the code would call if it was being run normally.

For example, let's imagine you want to unit test a :app:`Pyramid` view
function.

.. code-block:: python
   :linenos:

   from pyramid.security import has_permission
   from pyramid.httpexceptions import HTTPForbidden

   def view_fn(request):
       if not has_permission('edit', request.context, request):
           raise HTTPForbidden
       return {'greeting':'hello'}

Without doing anything special during a unit test, the call to
:func:`~pyramid.security.has_permission` in this view function will always
return a ``True`` value.  When a :app:`Pyramid` application starts normally,
it will populate a :term:`application registry` using :term:`configuration
declaration` calls made against a :term:`Configurator`.  But if this
application registry is not created and populated (e.g. by initializing the
configurator with an authorization policy), like when you invoke application
code via a unit test, :app:`Pyramid` API functions will tend to either fail
or return default results.  So how do you test the branch of the code in this
view function that raises :exc:`HTTPForbidden`?

The testing API provided by :app:`Pyramid` allows you to simulate various
application registry registrations for use under a unit testing framework
without needing to invoke the actual application configuration implied by its
``main`` function.  For example, if you wanted to test the above ``view_fn``
(assuming it lived in the package named ``my.package``), you could write a
:class:`unittest.TestCase` that used the testing API.

.. code-block:: python
   :linenos:

   import unittest
   from pyramid import testing

   class MyTest(unittest.TestCase):
       def setUp(self):
           self.config = testing.setUp()

       def tearDown(self):
           testing.tearDown()
       
       def test_view_fn_forbidden(self):
           from pyramid.httpexceptions import HTTPForbidden
           from my.package import view_fn
           self.config.testing_securitypolicy(userid='hank', 
                                              permissive=False)
           request = testing.DummyRequest()
           request.context = testing.DummyResource()
           self.assertRaises(HTTPForbidden, view_fn, request)

       def test_view_fn_allowed(self):
           from my.package import view_fn
           self.config.testing_securitypolicy(userid='hank', 
                                              permissive=True)
           request = testing.DummyRequest()
           request.context = testing.DummyResource()
           response = view_fn(request)
           self.assertEqual(response, {'greeting':'hello'})
           
In the above example, we create a ``MyTest`` test case that inherits from
:mod:`unittest.TestCase`.  If it's in our :app:`Pyramid` application, it will
be found when ``setup.py test`` is run.  It has two test methods.

The first test method, ``test_view_fn_forbidden`` tests the ``view_fn`` when
the authentication policy forbids the current user the ``edit`` permission.
Its third line registers a "dummy" "non-permissive" authorization policy
using the :meth:`~pyramid.config.Configurator.testing_securitypolicy` method,
which is a special helper method for unit testing.

We then create a :class:`pyramid.testing.DummyRequest` object which simulates
a WebOb request object API.  A :class:`pyramid.testing.DummyRequest` is a
request object that requires less setup than a "real" :app:`Pyramid` request.
We call the function being tested with the manufactured request.  When the
function is called, :func:`pyramid.security.has_permission` will call the
"dummy" authentication policy we've registered through
:meth:`~pyramid.config.Configuration.testing_securitypolicy`, which denies
access.  We check that the view function raises a :exc:`HTTPForbidden` error.

The second test method, named ``test_view_fn_allowed`` tests the alternate
case, where the authentication policy allows access.  Notice that we pass
different values to
:meth:`~pyramid.config.Configurator.testing_securitypolicy` to obtain this
result.  We assert at the end of this that the view function returns a value.

Note that the test calls the :func:`pyramid.testing.setUp` function in its
``setUp`` method and the :func:`pyramid.testing.tearDown` function in its
``tearDown`` method.  We assign the result of :func:`pyramid.testing.setUp`
as ``config`` on the unittest class.  This is a :term:`Configurator` object
and all methods of the configurator can be called as necessary within
tests. If you use any of the :class:`~pyramid.config.Configurator` APIs during
testing, be sure to use this pattern in your test case's ``setUp`` and
``tearDown``; these methods make sure you're using a "fresh"
:term:`application registry` per test run.

See the :ref:`testing_module` chapter for the entire :app:`Pyramid` -specific
testing API.  This chapter describes APIs for registering a security policy,
registering resources at paths, registering event listeners, registering
views and view permissions, and classes representing "dummy" implementations
of a request and a resource.

See also the various methods of the :term:`Configurator` documented in
:ref:`configuration_module` that begin with the ``testing_`` prefix.

.. index::
   single: integration tests

.. _integration_tests:

Creating Integration Tests
--------------------------

In :app:`Pyramid`, a *unit test* typically relies on "mock" or "dummy"
implementations to give the code under test only enough context to run.

"Integration testing" implies another sort of testing.  In the context of a
:app:`Pyramid` integration test, the test logic tests the functionality of
some code *and* its integration with the rest of the :app:`Pyramid`
framework.

In :app:`Pyramid` applications that are plugins to Pyramid, you can create an
integration test by including its ``includeme`` function via
:meth:`pyramid.config.Configurator.include` in the test's setup code.  This
causes the entire :app:`Pyramid` environment to be set up and torn down as if
your application was running "for real".  This is a heavy-hammer way of
making sure that your tests have enough context to run properly, and it tests
your code's integration with the rest of :app:`Pyramid`.

Let's demonstrate this by showing an integration test for a view.  The below
test assumes that your application's package name is ``myapp``, and that
there is a ``views`` module in the app with a function with the name
``my_view`` in it that returns the response 'Welcome to this application'
after accessing some values that require a fully set up environment.

.. code-block:: python
   :linenos:

   import unittest

   from pyramid import testing

   class ViewIntegrationTests(unittest.TestCase):
       def setUp(self):
           """ This sets up the application registry with the
           registrations your application declares in its ``includeme`` 
           function.
           """
           import myapp
           self.config = testing.setUp()
           self.config.include('myapp')

       def tearDown(self):
           """ Clear out the application registry """
           testing.tearDown()

       def test_my_view(self):
           from myapp.views import my_view
           request = testing.DummyRequest()
           result = my_view(request)
           self.assertEqual(result.status, '200 OK')
           body = result.app_iter[0]
           self.failUnless('Welcome to' in body)
           self.assertEqual(len(result.headerlist), 2)
           self.assertEqual(result.headerlist[0],
                            ('Content-Type', 'text/html; charset=UTF-8'))
           self.assertEqual(result.headerlist[1], ('Content-Length',
                                                   str(len(body))))

Unless you cannot avoid it, you should prefer writing unit tests that use the
:class:`~pyramid.config.Configurator` API to set up the right "mock"
registrations rather than creating an integration test.  Unit tests will run
faster (because they do less for each test) and the result of a unit test is
usually easier to make assertions about.

.. index::
   single: functional tests

.. _functional_tests:

Creating Functional Tests
-------------------------

Functional tests test your literal application.

The below test assumes that your application's package name is ``myapp``, and
that there is a view that returns an HTML body when the root URL is invoked.
It further assumes that you've added a ``tests_require`` dependency on the
``WebTest`` package within your ``setup.py`` file.  :term:`WebTest` is a
functional testing package written by Ian Bicking.

.. code-block:: python
   :linenos:

   import unittest

   class FunctionalTests(unittest.TestCase):
       def setUp(self):
           from myapp import main
           app = main({})
           from webtest import TestApp
           self.testapp = TestApp(app)

       def test_root(self):
           res = self.testapp.get('/', status=200)
           self.failUnless('Pyramid' in res.body)

When this test is run, each test creates a "real" WSGI application using the
``main`` function in your ``myapp.__init__`` module and uses :term:`WebTest`
to wrap that WSGI application.  It assigns the result to ``self.testapp``.
In the test named ``test_root``, we use the testapp's ``get`` method to
invoke the root URL.  We then assert that the returned HTML has the string
``Pyramid`` in it.

See the :term:`WebTest` documentation for further information about the
methods available to a :class:`webtest.TestApp` instance.
