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
"unit under test".  If you write a unit test that aims to verify the result of
a particular codepath through a Python function, you need only be concerned
about testing the code that *lives in the function body itself*. If the
function accepts a parameter that represents a complex application "domain
object" (such as a resource, a database connection, or an SMTP server), the
argument provided to this function during a unit test *need not be* and likely
*should not be* a "real" implementation object.  For example, although a
particular function implementation may accept an argument that represents an
SMTP server object, and the function may call a method of this object when the
system is operating normally that would result in an email being sent, a unit
test of this codepath of the function does *not* need to test that an email is
actually sent.  It just needs to make sure that the function calls the method
of the object provided as an argument that *would* send an email if the
argument happened to be the "real" implementation of an SMTP server object.

An *integration test*, on the other hand, is a different form of testing in
which the interaction between two or more "units" is explicitly tested.
Integration tests verify that the components of your application work together.
You *might* make sure that an email was actually sent in an integration test.

A *functional test* is a form of integration test in which the application is
run "literally".  You would *have to* make sure that an email was actually sent
in a functional test, because it tests your code end to end.

It is often considered best practice to write each type of tests for any given
codebase.  Unit testing often provides the opportunity to obtain better
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
Into Python <http://www.diveintopython.net/unit_testing/index.html>`_ by Mark
Pilgrim.

:app:`Pyramid` provides a number of facilities that make unit, integration, and
functional tests easier to write.  The facilities become particularly useful
when your code calls into :app:`Pyramid`-related framework functions.

.. index::
   single: test setup
   single: test tear down
   single: unittest

.. _test_setup_and_teardown:

Test Set Up and Tear Down
-------------------------

:app:`Pyramid` uses a "global" (actually :term:`thread local`) data structure
to hold two items: the current :term:`request` and the current
:term:`application registry`.  These data structures are available via the
:func:`pyramid.threadlocal.get_current_request` and
:func:`pyramid.threadlocal.get_current_registry` functions, respectively. See
:ref:`threadlocals_chapter` for information about these functions and the data
structures they return.

If your code uses these ``get_current_*`` functions or calls :app:`Pyramid`
code which uses ``get_current_*`` functions, you will need to call
:func:`pyramid.testing.setUp` in your test setup and you will need to call
:func:`pyramid.testing.tearDown` in your test teardown.
:func:`~pyramid.testing.setUp` pushes a registry onto the :term:`thread local`
stack, which makes the ``get_current_*`` functions work.  It returns a
:term:`Configurator` object which can be used to perform extra configuration
required by the code under test.  :func:`~pyramid.testing.tearDown` pops the
thread local stack.

Normally when a Configurator is used directly with the ``main`` block of a
Pyramid application, it defers performing any "real work" until its ``.commit``
method is called (often implicitly by the
:meth:`pyramid.config.Configurator.make_wsgi_app` method).  The Configurator
returned by :func:`~pyramid.testing.setUp` is an *autocommitting* Configurator,
however, which performs all actions implied by methods called on it
immediately.  This is more convenient for unit testing purposes than needing to
call :meth:`pyramid.config.Configurator.commit` in each test after adding extra
configuration statements.

The use of the :func:`~pyramid.testing.setUp` and
:func:`~pyramid.testing.tearDown` functions allows you to supply each unit test
method in a test case with an environment that has an isolated registry and an
isolated request for the duration of a single test.  Here's an example of using
this feature:

.. code-block:: python
   :linenos:

   import unittest
   from pyramid import testing

   class MyTest(unittest.TestCase):
       def setUp(self):
           self.config = testing.setUp()

       def tearDown(self):
           testing.tearDown()

The above will make sure that :func:`~pyramid.threadlocal.get_current_registry`
called within a test case method of ``MyTest`` will return the
:term:`application registry` associated with the ``config`` Configurator
instance.  Each test case method attached to ``MyTest`` will use an isolated
registry.

The :func:`~pyramid.testing.setUp` and :func:`~pyramid.testing.tearDown`
functions accept various arguments that influence the environment of the test.
See the :ref:`testing_module` API for information about the extra arguments
supported by these functions.

If you also want to make :func:`~pyramid.threadlocal.get_current_request`
return something other than ``None`` during the course of a single test, you
can pass a :term:`request` object into the :func:`pyramid.testing.setUp` within
the ``setUp`` method of your test:

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

If you pass a :term:`request` object into :func:`pyramid.testing.setUp` within
your test case's ``setUp``, any test method attached to the ``MyTest`` test
case that directly or indirectly calls
:func:`~pyramid.threadlocal.get_current_request` will receive the request
object.  Otherwise, during testing,
:func:`~pyramid.threadlocal.get_current_request` will return ``None``. We use a
"dummy" request implementation supplied by
:class:`pyramid.testing.DummyRequest` because it's easier to construct than a
"real" :app:`Pyramid` request object.

Test setup using a context manager
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An alternative style of setting up a test configuration is to use the ``with``
statement and :func:`pyramid.testing.testConfig` to create a context manager.
The context manager will call :func:`pyramid.testing.setUp` before the code
under test and :func:`pyramid.testing.tearDown` afterwards.

This style is useful for small self-contained tests. For example:

.. code-block:: python
   :linenos:

   import unittest

   class MyTest(unittest.TestCase):

       def test_my_function(self):
           from pyramid import testing
           with testing.testConfig() as config:
               config.add_route('bar', '/bar/{id}')
               my_function_which_needs_route_bar()

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
won't really hurt anything if the application you're testing does not call any
``get_current*`` function.

.. index::
   single: pyramid.testing
   single: Configurator testing API

Using the ``Configurator`` and ``pyramid.testing`` APIs in Unit Tests
---------------------------------------------------------------------

The ``Configurator`` API and the :mod:`pyramid.testing` module provide a number
of functions which can be used during unit testing.  These functions make
:term:`configuration declaration` calls to the current :term:`application
registry`, but typically register a "stub" or "dummy" feature in place of the
"real" feature that the code would call if it was being run normally.

For example, let's imagine you want to unit test a :app:`Pyramid` view
function.

.. code-block:: python
   :linenos:

   from pyramid.httpexceptions import HTTPForbidden

   def view_fn(request):
       if request.has_permission('edit'):
           raise HTTPForbidden
       return {'greeting':'hello'}

.. note::

   This code implies that you have defined a renderer imperatively in a
   relevant :class:`pyramid.config.Configurator` instance, otherwise it would
   fail when run normally.

Without doing anything special during a unit test, the call to
:meth:`~pyramid.request.Request.has_permission` in this view function will
always return a ``True`` value.  When a :app:`Pyramid` application starts
normally, it will populate an :term:`application registry` using
:term:`configuration declaration` calls made against a :term:`Configurator`.
But if this application registry is not created and populated (e.g., by
initializing the configurator with an authorization policy), like when you
invoke application code via a unit test, :app:`Pyramid` API functions will tend
to either fail or return default results.  So how do you test the branch of the
code in this view function that raises
:exc:`~pyramid.httpexceptions.HTTPForbidden`?

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
:class:`unittest.TestCase`.  If it's in our :app:`Pyramid` application, it will
be found when ``py.test`` is run.  It has two test methods.

The first test method, ``test_view_fn_forbidden`` tests the ``view_fn`` when
the authentication policy forbids the current user the ``edit`` permission. Its
third line registers a "dummy" "non-permissive" authorization policy using the
:meth:`~pyramid.config.Configurator.testing_securitypolicy` method, which is a
special helper method for unit testing.

We then create a :class:`pyramid.testing.DummyRequest` object which simulates a
WebOb request object API.  A :class:`pyramid.testing.DummyRequest` is a request
object that requires less setup than a "real" :app:`Pyramid` request.  We call
the function being tested with the manufactured request.  When the function is
called, :meth:`pyramid.request.Request.has_permission` will call the "dummy"
authentication policy we've registered through
:meth:`~pyramid.config.Configurator.testing_securitypolicy`, which denies
access.  We check that the view function raises a
:exc:`~pyramid.httpexceptions.HTTPForbidden` error.

The second test method, named ``test_view_fn_allowed``, tests the alternate
case, where the authentication policy allows access.  Notice that we pass
different values to :meth:`~pyramid.config.Configurator.testing_securitypolicy`
to obtain this result.  We assert at the end of this that the view function
returns a value.

Note that the test calls the :func:`pyramid.testing.setUp` function in its
``setUp`` method and the :func:`pyramid.testing.tearDown` function in its
``tearDown`` method.  We assign the result of :func:`pyramid.testing.setUp` as
``config`` on the unittest class.  This is a :term:`Configurator` object and
all methods of the configurator can be called as necessary within tests. If you
use any of the :class:`~pyramid.config.Configurator` APIs during testing, be
sure to use this pattern in your test case's ``setUp`` and ``tearDown``; these
methods make sure you're using a "fresh" :term:`application registry` per test
run.

See the :ref:`testing_module` chapter for the entire :app:`Pyramid`-specific
testing API.  This chapter describes APIs for registering a security policy,
registering resources at paths, registering event listeners, registering views
and view permissions, and classes representing "dummy" implementations of a
request and a resource.

.. seealso::

    See also the various methods of the :term:`Configurator` documented in
    :ref:`configuration_module` that begin with the ``testing_`` prefix.

.. index::
   single: integration tests

.. _integration_tests:

Creating Integration Tests
--------------------------

In :app:`Pyramid`, a *unit test* typically relies on "mock" or "dummy"
implementations to give the code under test enough context to run.

"Integration testing" implies another sort of testing.  In the context of a
:app:`Pyramid` integration test, the test logic exercises the functionality of
the code under test *and* its integration with the rest of the :app:`Pyramid`
framework.

Creating an integration test for a :app:`Pyramid` application usually means
invoking the application's ``includeme`` function via
:meth:`pyramid.config.Configurator.include` within the test's setup code.  This
causes the entire :app:`Pyramid` environment to be set up, simulating what
happens when your application is run "for real".  This is a heavy-hammer way of
making sure that your tests have enough context to run properly, and tests your
code's integration with the rest of :app:`Pyramid`.

.. seealso::

   See also :ref:`including_configuration`

Writing unit tests that use the :class:`~pyramid.config.Configurator` API to
set up the right "mock" registrations is often preferred to creating
integration tests.  Unit tests will run faster (because they do less for each
test) and are usually easier to reason about.

.. index::
   single: functional tests

.. _functional_tests:

Creating Functional Tests
-------------------------

Functional tests test your literal application.

In Pyramid, functional tests are typically written using the :term:`WebTest`
package, which provides APIs for invoking HTTP(S) requests to your application.
We also like ``py.test`` and ``pytest-cov`` to provide simple testing and
coverage reports.

Regardless of which testing :term:`package` you use, be sure to add a
``tests_require`` dependency on that package to your application's ``setup.py``
file. Using the project ``myproject`` generated by the starter cookiecutter as
described in :doc:`project`, we would insert the following code immediately
following the ``requires`` block in the file ``myproject/setup.py``.

.. literalinclude:: myproject/setup.py
    :language: python
    :lines: 11-23
    :lineno-match:
    :emphasize-lines: 9-

Remember to change the dependency.

.. literalinclude:: myproject/setup.py
    :language: python
    :lines: 42-46
    :lineno-match:
    :emphasize-lines: 2-4

As always, whenever you change your dependencies, make sure to run the correct
``pip install -e`` command.

.. code-block:: bash

    $VENV/bin/pip install -e ".[testing]"

In your ``MyPackage`` project, your :term:`package` is named ``myproject``
which contains a ``views`` module, which in turn contains a :term:`view`
function ``my_view`` that returns an HTML body when the root URL is invoked:

   .. literalinclude:: myproject/myproject/views.py
      :linenos:
      :language: python

The following example functional test demonstrates invoking the above
:term:`view`:

   .. literalinclude:: myproject/myproject/tests.py
      :linenos:
      :pyobject: FunctionalTests
      :language: python

When this test is run, each test method creates a "real" :term:`WSGI`
application using the ``main`` function in your ``myproject.__init__`` module,
using :term:`WebTest` to wrap that WSGI application.  It assigns the result to
``self.testapp``.  In the test named ``test_root``, the ``TestApp``'s ``GET``
method is used to invoke the root URL.  Finally, an assertion is made that the
returned HTML contains the text ``Pyramid``.

See the :term:`WebTest` documentation for further information about the methods
available to a :class:`webtest.app.TestApp` instance.
