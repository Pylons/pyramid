.. _unittesting_chapter:

Unit and Integration Testing
============================

The suggested mechanism for unit testing :mod:`repoze.bfg`
applications is the Python ``unittest`` module.  :mod:`repoze.bfg`
provides a number of facilities that make unit tests easier to write.
The facilities become particularly useful when your code calls into
:mod:`repoze.bfg` -related framework functions.

Test Set Up and Tear Down
--------------------------

:mod:`repoze.bfg` uses a "global" (actually thread-local) data
structure to hold on to two items: the current :term:`request` and the
current :term:`application registry`.  These data structures are
available via the ``repoze.bfg.threadlocal.get_current_request`` and
``repoze.bfg.threadlocal.get_current_registry`` functions,
respectively.

If your code uses these ``get_current_*`` functions (or calls
:mod:`repoze.bfg` code which uses the ``get_current_*`` functions),
you will need to use the ``repoze.bfg.testing.setUp`` and
``repoze.bfg.testing.tearDown`` functions within the ``setUp`` and
``tearDown`` methods of your unit tests, respectively.

If you don't *know* whether you're calling code that uses these
functions, a rule of thumb applies: just always use the
``repoze.bfg.testing.setUp`` and ``repoze.bfg.testing.tearDown``
functions in the ``setUp`` and ``tearDown`` respectively of unit tests
that test :mod:`repoze.bfg` application code, unless it's obvious
you're not calling any :mod:`repoze.bfg` APIs which might make use of
the any "current" global.

The ``repoze.bfg.testing.setUp`` and ``repoze.bfg.testing.tearDown``
functions accept various arguments that influence the code run during
the test.  See the :ref:`testing_module` chapter for information about
the APIs of ``repoze.bfg.testing.setUp`` and
``repoze.bfg.testing.tearDown``.

Using the ``repoze.bfg.testing`` API in Unit Tests
--------------------------------------------------

The ``repoze.bfg.testing`` module provides a number of functions which
can be used during unit testing.  For example, let's imagine you want
to unit test a :mod:`repoze.bfg` view function.

.. code-block:: python
   :linenos:

   def view_fn(request):
       from repoze.bfg.chameleon_zpt import render_template_to_response
       if 'say' in request.params:
           return render_template_to_response('templates/submitted.pt',
                                               say=request.params['say'])
       return render_template_to_response('templates/show.pt', say='Hello')

Without invoking any ZCML or using the testing API, an attempt to run
this view function will result in an error.  When a :mod:`repoze.bfg`
application starts normally, it will create an application registry
from the information it finds in the application's ``configure.zcml``
file.  But if this application registry is not created and populated
(e.g. with ``view`` declarations in ZCML), like when you invoke
application code via a unit test, :mod:`repoze.bfg` API functions will
tend to fail.

The testing API provided by ``repoze.bfg`` allows you to simulate
various application registry registrations for use under a unit
testing framework without needing to invoke the actual application
ZCML configuration.  For example, if you wanted to test the above
``view_fn`` (assuming it lived in ``my.package``), you could write a
unittest TestCase that used the testing API.

.. code-block:: python
   :linenos:

   import unittest
   from repoze.bfg import testing

   class MyTest(unittest.TestCase):
       def setUp(self):
           testing.setUp()

       def tearDown(self):
           testing.tearDown()
       
       def test_view_fn_not_submitted(self):
           from my.package import view_fn
           renderer = testing.registerTemplateRenderer('templates/show.pt')
           request = testing.DummyRequest()
           response = view_fn(request)
           renderer.assert_(say='Hello')

       def test_view_fn_submitted(self):
           from my.package import view_fn
           renderer = testing.registerTemplateRenderer('templates/submitted.pt')
           request = testing.DummyRequest()
           request.params['say'] = 'Yo'
           response = view_fn(request)
           renderer.assert_(say='Yo')

In the above example, we create a ``MyTest`` test case that inherits
from ``unittest.TestCase``.  If it's in our :mod:`repoze.bfg`
application, it will be found when ``setup.py test`` is run.  It has
two test methods.

The first test method, ``test_view_fn_not_submitted`` tests the
``view_fn`` function in the case that no "form" values (represented by
request.params) have been submitted.  Its first line registers a
"dummy template renderer" named ``templates/show.pt`` via the
``registerTemplateRenderer`` function (a ``repoze.bfg.testing`` API);
this function returns a DummyTemplateRenderer instance which we hang
on to for later.  We then create a ``DummyRequest`` object which
simulates a WebOb request object).  We call the function being tested
with the manufactured request.  When the function is called,
``render_template_to_response`` will call the "dummy" template
renderer object instead of the real template renderer object.  When
the dummy renderer is called, it will set attributes on itself
corresponding to the non-path keyword arguments provided to the
``render_template_to_response`` function.  We check that the ``say``
parameter sent into the template rendering function was ``Hello`` in
this specific example.  The ``assert_`` method of the renderer we've
created will raise an ``AssertionError`` if the value passed to the
renderer as ``say`` does not equal ``Hello`` (any number of keyword
arguments are supported).

The second test method, named ``test_view_fn_submitted`` tests the
alternate case, where the ``say`` form value has already been set in
the request and performs a similar template registration and
assertion.  We assert at the end of this that the renderer's ``say``
attribute is ``Yo``, as this is what is expected of the view function
in the branch it's testing.

Note that the test calls the ``repoze.bfg.testing.setUp`` function in
its ``setUp`` method and the ``repoze.bfg.testing.tearDown`` function
in its ``tearDown`` method.  Use of this pattern is required to
perform cleanup between the test runs.  If you use any of the testing
API, be sure to call ``repoze.bfg.testing.setUp`` in the test setup
and ``repoze.bfg.testing.tearDown`` in the test teardown.

See the :ref:`testing_module` chapter for the entire :mod:`repoze.bfg`
-specific testing API.  This chapter describes APIs for registering a
security policy, registering models at paths, registering event
listeners, registering views and view permissions, and classes
representing "dummy" implementations of a request and a model.

.. _integration_tests:

Creating Integration Tests
--------------------------

In :mod:`repoze.bfg`, a unit test typically relies on "mock" or
"dummy" implementations to give the code under test only enough
context to run.

"Integration testing" implies another sort of testing.  In the context
of a :mod:`repoze.bfg`, integration test, the test logic tests the
functionality of some code *and* its integration with the rest of the
:mod:`repoze.bfg` framework.

In :mod:`repoze.bfg`, you create an integration test by *loading its
ZCML* in the test's setup code.  This causes the entire
:mod:`repoze.bfg` environment to be set up and torn down as if your
application was running "for real".  This is a heavy-hammer way of
making sure that your tests have enough context to run properly, and
it tests your code's integration with the rest of :mod:`repoze.bfg`.

Let's demonstrate this by showing an integration test for a view.  The
below test assumes that your application's package name is ``myapp``,
and that there is a ``views`` module in the app with a function with
the name ``my_view`` in it that returns the response 'Welcome to this
application' after accessing some values that require a fully set up
environment.

.. code-block:: python
   :linenos:

   import unittest

   from repoze.bfg import testing

   class ViewIntegrationTests(unittest.TestCase):
       def setUp(self):
           """ This sets up the application registry with the
           registrations your application declares in its configure.zcml
           (including dependent registrations for repoze.bfg itself).
           """
           testing.setUp()
           import myapp
           testing.zcml_configure('configure.zcml', package=myapp)

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

Unless you cannot avoid it, you should prefer writing unit tests that
use the :mod:`repoze.bfg.testing` API to set up the right "mock"
registrations rather than creating an integration test.  Unit tests
will run faster (because they don't have to parse and execute ZCML for
each test) and the result of a unit test is usually easier to make
assertions about.


