.. _unittesting_chapter:

Unit Testing
============

The suggested mechanism for unit testing :mod:`repoze.bfg`
applications is the Python ``unittest`` module.  :mod:`repoze.bfg`
provides a number of facilities that make writing ``unittest`` -based
test cases easier to write.  The facilities become particularly useful
when your code calls into :mod:`repoze.bfg` -related framework
functions.

Writing A Unit Test
-------------------

The ``repoze.bfg.testing`` module provides a number of functions which
can be used during unit testing.  An example of a unit test class that
uses these functions is below.

.. code-block:: python :linenos:

   def view_fn(context, request):
       from repoze.bfg.chameleon_zpt import render_template_to_response
       if 'say' in request.params:
           return render_template_to_response('templates/submitted.pt',
                                               say=request.params['say'])
       return render_template_to_response('templates/show.pt', say='Hello')

   import unittest
   from zope.testing.cleanup import cleanUp
   from.repoze.bfg import testing

   class MyTest(unittest.TestCase):
       def setUp(self):
           cleanUp()

       def tearDown(self):
           cleanUp()
       
       def test_view_fn_not_submitted(self):
           renderer = testing.registerTemplateRenderer('templates/show.pt')
           context = testing.DummyModel()
           request = testing.DummyRequest()
           response = view_fn(context, request)
           self.assertEqual(renderer.say, 'Hello')

        def test_view_fn_submitted(self):
           renderer = testing.registerTemplateRenderer('templates/submitted.pt')
           context = testing.DummyModel()
           request = testing.DummyRequest()
           request.params['say'] = 'Yo'
           response = view_fn(context, request)
           self.assertEqual(renderer.say, 'Yo')

In the above example, we create a ``MyTest`` test case that inherits
from ``unittest.TestCase``.  It has two test methods.

The first test method, ``test_view_fn_not_submitted`` tests the
``view_fn`` function in the case that no "form" values (represented by
request.params) have been submitted.  Its first line registers a
"dummy template renderer" named ``templates/show.pt`` via the
``registerTemplateRenderer`` function (a ``repoze.bfg.testing`` API);
this function returns a DummyTemplateRenderer instance which we hang
on to for later.  We then call ``DummyRequest`` to get a dummy request
object, and ``DummyModel`` to get a dummy context object.  We call the
function being tested with the manufactured context and request.  When
the function is called, ``render_template_to_response`` will call the
"dummy" template renderer object instead of the real template renderer
object.  When it's called, it will set attributes on itself
corresponding to the non-path keyword arguments provided to the
``render_template_to_response`` function.  We check that the ``say``
parameter sent into the template rendering function was ``Hello`` in
this specific example.

The second test method, named ``test_view_fn_submitted`` tests the
alternate case, where the ``say`` form value has already been set in
the request and performs a similar template registration and
assertion.

Note that the test calls the ``zope.testing.cleanup.cleanUp`` function
in its ``setUp`` and ``tearDown`` functions.  This is required to
perform cleanup between the test runs.  If you use any of the testing
API, be sure to call this function at setup and teardown of individual
tests.

See the :ref:`testing_module` chapter for the entire
:mod:`repoze.bfg` -specific testing API.

