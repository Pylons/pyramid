.. _unittesting_chapter:

Unit Testing
============

The suggested mechanism for unit testing :mod:`repoze.bfg`
applications is the Python ``unittest`` module.  :mod:`repoze.bfg`
provides a number of facilities that make writing ``unittest`` -based
test cases easier to write.  The facilities become particularly useful
when your code calls into :mod:`repoze.bfg` -related framework
functions.

The ``BFGTestCase`` Base Class
------------------------------

The ``repoze.bfg.testing`` module provides a class named
``BFGTestCase`` which you can use as a base class for unittest test
classes.

.. code-block:: python
   :linenos:

   def view_fn(context, request):
       from repoze.bfg.chameleon_zpt import render_template_to_response
       if 'say' in request.params:
           return render_template_to_response('templates/submitted.pt',
                                               say=request.params['say'])
       return render_template_to_response('templates/show.pt', say='Hello')

   from repoze.bfg.testing import BFGTestCase

   class MyTest(BFGTestCase):
       def test_view_fn_not_submitted(self):
           template = self.registerDummyTemplate('templates/show.pt')
           request = self.makeRequest()
           context = self.makeModel()
           response = view_fn(context, request)
           self.assertEqual(template.say, 'Hello')

        def test_view_fn_submitted(self):
           template = self.registerDummyTemplate('templates/submitted.pt')
           request = self.makeRequest()
           request.params['say'] = 'Yo'
           context = self.makeModel()
           response = view_fn(context, request)
           self.assertEqual(template.say, 'Yo')

In the above example, we create a ``MyTest`` test case that inherits
from ``BFGTestCase``.  It has two test methods.  The first test
method, ``test_view_fn_not_submitted`` tests the ``view_fn`` function
in the case that no "form" values (represented by request.params) have
been submitted.  Its first line registers a "dummy template" named
``templates/show.pt`` via the ``registerDummyTemplate`` method (a
``BFGTestCase`` API); this function returns a DummyTemplate instance
which we hang on to for later.  We then call ``makeRequest`` to get a
DummyRequest object, and ``makeModel`` to get a DummyModel object.  We
call the function being tested with the manufactured context and
request.  When the function is called, ``render_template_to_response``
will call the "dummy" template object instead of the real template
object.  When it's called, it will set attributes on itself
corresponding to the non-path keyword arguments provided to the
``render_template_to_response`` function.  We check that the ``say``
parameter sent into the template rendering function was ``Hello`` in
this specific example.  The second test, named
``test_view_fn_submitted`` tests the alternate case, where the ``say``
form value has already been set in the request and performs a similar
template registration and assertion.

See the :ref:`testing_module` chapter for the entire
:mod:`repoze.bfg` -specific testing API.

The ``BFGTestCase`` class inherits from ``unittest.TestCase``, so it
will be found by test finders.

