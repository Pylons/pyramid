.. _unittesting_chapter:

Unit Testing
============

The suggested mechanism for unit testing :mod:`repoze.bfg`
applications is the Python ``unittest`` module.  :mod:`repoze.bfg`
provides a number of facilities that make unit tests easier to write.
The facilities become particularly useful when your code calls into
:mod:`repoze.bfg` -related framework functions.

Using the ``repoze.bfg.testing`` API
------------------------------------

The ``repoze.bfg.testing`` module provides a number of functions which
can be used during unit testing.  For example, let's imagine you want
to unit test a :mod:`repoze.bfg` view function.

.. code-block:: python
   :linenos:

   def view_fn(context, request):
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
           testing.cleanUp()

       def tearDown(self):
           testing.cleanUp()
       
       def test_view_fn_not_submitted(self):
           from my.package import view_fn
           renderer = testing.registerTemplateRenderer('templates/show.pt')
           context = testing.DummyModel()
           request = testing.DummyRequest()
           response = view_fn(context, request)
           renderer.assert_(say='Hello')

       def test_view_fn_submitted(self):
           from my.package import view_fn
           renderer = testing.registerTemplateRenderer('templates/submitted.pt')
           context = testing.DummyModel()
           request = testing.DummyRequest()
           request.params['say'] = 'Yo'
           response = view_fn(context, request)
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
on to for later.  We then create a ``DummyRequest`` object (it
simulates a WebOb request object), and we create a ``DummyModel``
context object.  We call the function being tested with the
manufactured context and request.  When the function is called,
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

Note that the test calls the ``repoze.bfg.testing.cleanUp`` function
in its ``setUp`` and ``tearDown`` functions.  This is required to
perform cleanup between the test runs.  If you use any of the testing
API, be sure to call this function at setup and teardown of individual
tests.

See the :ref:`testing_module` chapter for the entire :mod:`repoze.bfg`
-specific testing API.  This chapter describes APIs for registering a
security policy, registering models at paths, registering event
listeners, registering views and view permissions, and classes
representing "dummy" implementations of a request and a model.

