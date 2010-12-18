\.. index::
   single: unit testing
   single: integration testing

.. _unittesting_chapter:

Unit and Integration Testing
============================

*Unit testing* is, not surprisingly, the act of testing a "unit" in
your application.  In this context, a "unit" is often a function or a
method of a class instance.  The unit is also referred to as a "unit
under test".

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

An *integration test*, on the other hand, is a different form of
testing in which the interaction between two or more "units" is
explicitly tested.  Integration tests verify that the components of
your application work together.  You *might* make sure that an email
was actually sent in an integration test.

It is often considered best practice to write both types of tests for
any given codebase.  Unit testing often provides the opportunity to
obtain better "coverage": it's usually possible to supply a unit under
test with arguments and/or an environment which causes *all* of its
potential codepaths to be executed.  This is usually not as easy to do
with a set of integration tests, but integration testing provides a
measure of assurance that your "units" work together, as they will be
expected to when your application is run in production.

The suggested mechanism for unit and integration testing of a
:app:`Pyramid` application is the Python :mod:`unittest` module.
Although this module is named :mod:`unittest`, it is actually capable
of driving both unit and integration tests.  A good :mod:`unittest`
tutorial is available within `Dive Into Python
<http://diveintopython.org/unit_testing/index.html>`_ by Mark Pilgrim.

:app:`Pyramid` provides a number of facilities that make unit and
integration tests easier to write.  The facilities become particularly
useful when your code calls into :app:`Pyramid` -related framework
functions.

.. index::
   single: test setup
   single: test tear down
   single: unittest

.. _test_setup_and_teardown:

Test Set Up and Tear Down
--------------------------

:app:`Pyramid` uses a "global" (actually :term:`thread local`) data
structure to hold on to two items: the current :term:`request` and the
current :term:`application registry`.  These data structures are
available via the :func:`pyramid.threadlocal.get_current_request`
and :func:`pyramid.threadlocal.get_current_registry` functions,
respectively.  See :ref:`threadlocals_chapter` for information about
these functions and the data structures they return.

If your code uses these ``get_current_*`` functions or calls
:app:`Pyramid` code which uses ``get_current_*`` functions, you
will need to construct a :term:`Configurator` and call its ``begin``
method within the ``setUp`` method of your unit test and call the same
Configurator's ``end`` method within the ``tearDown`` method of your
unit test.

We'll also instruct the Configurator we use during testing to *autocommit*.
Normally when a Configurator is used by an application, it defers performing
any "real work" until its ``.commit`` method is called (often implicitly by
the :meth:`pyramid.config.Configurator.make_wsgi_app` method).  Passing
``autocommit=True`` to the Configurator constructor causes the Configurator
to perform all actions implied by methods called on it immediately, which is
more convenient for unit-testing purposes than needing to call
:meth:`pyramid.config.Configurator.commit` in each test.

The use of a Configurator and its ``begin`` and ``end`` methods allows
you to supply each unit test method in a test case with an environment
that has an isolated registry and an isolated request for the duration
of a single test.  Here's an example of using this feature:

.. code-block:: python
   :linenos:

   import unittest
   from pyramid.config import Configurator

   class MyTest(unittest.TestCase):
       def setUp(self):
           self.config = Configurator(autocommit=True)
           self.config.begin()

       def tearDown(self):
           self.config.end()

The above will make sure that
:func:`pyramid.threadlocal.get_current_registry` will return the
:term:`application registry` associated with the ``config`` Configurator
instance when :func:`pyramid.threadlocal.get_current_registry` is called in a
test case method attached to ``MyTest``.  Each test case method attached to
``MyTest`` will use an isolated registry.

The :meth:`pyramid.config.Configurator.begin` method accepts
various arguments that influence the code run during the test.  See
the :ref:`configuration_module` chapter for information about the API
of a :term:`Configurator`, including its ``begin`` and ``end``
methods.

If you also want to make :func:`pyramid.get_current_request`
return something other than ``None`` during the course of a single
test, you can pass a :term:`request` object into the
:meth:`pyramid.config.Configurator.begin` method of the
Configurator within the ``setUp`` method of your test:

.. code-block:: python
   :linenos:

   import unittest
   from pyramid.config import Configurator
   from pyramid import testing

   class MyTest(unittest.TestCase):
       def setUp(self):
           self.config = Configurator(autocommit=True)
           request = testing.DummyRequest()
           self.config.begin(request=request)

       def tearDown(self):
           self.config.end()

If you pass a :term:`request` object into the ``begin`` method of the
configurator within your test case's ``setUp``, any test method
attached to the ``MyTest`` test case that directly or indirectly calls
:func:`pyramid.threadlocal.get_current_request` will receive the
request you passed into the ``begin`` method.  Otherwise, during
testing, :func:`pyramid.threadlocal.get_current_request` will
return ``None``.  We use a "dummy" request implementation supplied by
:class:`pyramid.testing.DummyRequest` because it's easier to
construct than a "real" :app:`Pyramid` request object.

What?
~~~~~

Thread local data structures are always a bit confusing, especially when
they're used by frameworks.  Sorry.  So here's a rule of thumb: if you don't
*know* whether you're calling code that uses the
:func:`pyramid.threadlocal.get_current_registry` or
:func:`pyramid.threadlocal.get_current_request` functions, or you don't care
about any of this, but you still want to write test code, just always create
an autocommitting Configurator instance and call its ``begin`` method within
the ``setUp`` of a unit test, then subsequently call its ``end`` method in
the test's ``tearDown``.  This won't really hurt anything if the application
you're testing does not call any ``get_current*`` function.

.. index::
   single: pyramid.testing
   single: Configurator testing API

Using the ``Configurator`` and ``pyramid.testing`` APIs in Unit Tests
------------------------------------------------------------------------

The ``Configurator`` API and the ``pyramid.testing`` module
provide a number of functions which can be used during unit testing.
These functions make :term:`configuration declaration` calls to the
current :term:`application registry`, but typically register a "stub"
or "dummy" feature in place of the "real" feature that the code would
call if it was being run normally.

For example, let's imagine you want to unit test a :app:`Pyramid`
view function.

.. code-block:: python
   :linenos:

   def view_fn(request):
       from pyramid.chameleon_zpt import render_template_to_response
       if 'say' in request.params:
           return render_template_to_response('templates/submitted.pt',
                                               say=request.params['say'])
       return render_template_to_response('templates/show.pt', say='Hello')

Without invoking any startup code or using the testing API, an attempt
to run this view function in a unit test will result in an error.
When a :app:`Pyramid` application starts normally, it will populate
a :term:`application registry` using :term:`configuration declaration`
calls made against a :term:`Configurator` (sometimes deferring to the
application's ``configure.zcml`` :term:`ZCML` file via ``load_zcml``).
But if this application registry is not created and populated
(e.g. with an :meth:`pyramid.config.Configurator.add_view`
:term:`configuration declaration` or ``view`` declarations in
:term:`ZCML`), like when you invoke application code via a unit test,
:app:`Pyramid` API functions will tend to fail.

The testing API provided by :app:`Pyramid` allows you to simulate
various application registry registrations for use under a unit
testing framework without needing to invoke the actual application
configuration implied by its ``run.py``.  For example, if you wanted
to test the above ``view_fn`` (assuming it lived in the package named
``my.package``), you could write a :class:`unittest.TestCase` that
used the testing API.

.. code-block:: python
   :linenos:

   import unittest
   from pyramid.config import Configurator
   from pyramid import testing

   class MyTest(unittest.TestCase):
       def setUp(self):
           self.config = Configurator(autocommit=True)
           self.config.begin()

       def tearDown(self):
           self.config.end()
       
       def test_view_fn_not_submitted(self):
           from my.package import view_fn
           renderer = self.config.testing_add_renderer('templates/show.pt')
           request = testing.DummyRequest()
           response = view_fn(request)
           renderer.assert_(say='Hello')

       def test_view_fn_submitted(self):
           from my.package import view_fn
           renderer = self.config.testing_add_renderer(
                                          'templates/submitted.pt')
           request = testing.DummyRequest()
           request.params['say'] = 'Yo'
           response = view_fn(request)
           renderer.assert_(say='Yo')

In the above example, we create a ``MyTest`` test case that inherits
from :mod:`unittest.TestCase`.  If it's in our :app:`Pyramid`
application, it will be found when ``setup.py test`` is run.  It has
two test methods.

The first test method, ``test_view_fn_not_submitted`` tests the
``view_fn`` function in the case that no "form" values (represented by
request.params) have been submitted.  Its first line registers a
"dummy template renderer" named ``templates/show.pt`` via the
:meth:`pyramid.config.Configurator.testing_add_renderer`
method; this method returns a
:class:`pyramid.testing.DummyTemplateRenderer` instance which we
hang on to for later.

We then create a :class:`pyramid.testing.DummyRequest` object which
simulates a WebOb request object API.  A
:class:`pyramid.testing.DummyRequest` is a request object that
requires less setup than a "real" :app:`Pyramid` request.  We call
the function being tested with the manufactured request.  When the
function is called,
:func:`pyramid.chameleon_zpt.render_template_to_response` will call
the "dummy" template renderer object instead of the real template
renderer object.  When the dummy renderer is called, it will set
attributes on itself corresponding to the non-path keyword arguments
provided to the
:func:`pyramid.chameleon_zpt.render_template_to_response` function.
We check that the ``say`` parameter sent into the template rendering
function was ``Hello`` in this specific example.  The ``assert_``
method of the renderer we've created will raise an
:exc:`AssertionError` if the value passed to the renderer as ``say``
does not equal ``Hello`` (any number of keyword arguments are
supported).

The second test method, named ``test_view_fn_submitted`` tests the
alternate case, where the ``say`` form value has already been set in
the request and performs a similar template registration and
assertion.  We assert at the end of this that the renderer's ``say``
attribute is ``Yo``, as this is what is expected of the view function
in the branch it's testing.

Note that the test calls the
:meth:`pyramid.config.Configurator.begin` method in its
``setUp`` method and the ``end`` method of the same in its
``tearDown`` method.  If you use any of the
:class:`pyramid.config.Configurator` APIs during testing, be
sure to use this pattern in your test case's ``setUp`` and
``tearDown``; these methods make sure you're using a "fresh"
:term:`application registry` per test run.

See the :ref:`testing_module` chapter for the entire :app:`Pyramid`
-specific testing API.  This chapter describes APIs for registering a
security policy, registering resources at paths, registering event
listeners, registering views and view permissions, and classes
representing "dummy" implementations of a request and a resource.

See also the various methods of the :term:`Configurator` documented in
:ref:`configuration_module` that begin with the ``testing_`` prefix.

.. index::
   single: integration tests

.. _integration_tests:

Creating Integration Tests
--------------------------

In :app:`Pyramid`, a *unit test* typically relies on "mock" or
"dummy" implementations to give the code under test only enough
context to run.

"Integration testing" implies another sort of testing.  In the context
of a :app:`Pyramid`, integration test, the test logic tests the
functionality of some code *and* its integration with the rest of the
:app:`Pyramid` framework.

In :app:`Pyramid` applications that use :term:`ZCML`, you can
create an integration test by *loading its ZCML* in the test's setup
code.  This causes the entire :app:`Pyramid` environment to be set
up and torn down as if your application was running "for real".  This
is a heavy-hammer way of making sure that your tests have enough
context to run properly, and it tests your code's integration with the
rest of :app:`Pyramid`.

Let's demonstrate this by showing an integration test for a view.  The
below test assumes that your application's package name is ``myapp``,
and that there is a ``views`` module in the app with a function with
the name ``my_view`` in it that returns the response 'Welcome to this
application' after accessing some values that require a fully set up
environment.

.. code-block:: python
   :linenos:

   import unittest

   from pyramid.config import Configurator
   from pyramid import testing

   class ViewIntegrationTests(unittest.TestCase):
       def setUp(self):
           """ This sets up the application registry with the
           registrations your application declares in its configure.zcml
           (including dependent registrations for pyramid itself).
           """
           import myapp
           self.config = Configurator(package=myapp, autocommit=True)
           self.config.begin()
           self.config.load_zcml('myapp:configure.zcml')

       def tearDown(self):
           """ Clear out the application registry """
           self.config.end()

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

Unless you cannot avoid it, you should prefer writing unit tests that
use the :class:`pyramid.config.Configurator` API to set up
the right "mock" registrations rather than creating an integration
test.  Unit tests will run faster (because they do less for each test)
and the result of a unit test is usually easier to make assertions
about.


