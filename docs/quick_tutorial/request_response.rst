.. _qtut_request_response:

=======================================
10: Handling Web Requests and Responses
=======================================

Web applications handle incoming requests and return outgoing responses.
Pyramid makes working with requests and responses convenient and reliable.


Objectives
==========

- Learn the background on Pyramid's choices for requests and responses.

- Grab data out of the request.

- Change information in the response headers.


Background
==========

Developing for the web means processing web requests. As this is a critical
part of a web application, web developers need a robust, mature set of software
for web requests and returning web responses.

Pyramid has always fit nicely into the existing world of Python web development
(virtual environments, packaging, cookiecutters, first to embrace Python 3, and
so on). Pyramid turned to the well-regarded :term:`WebOb` Python library for
request and response handling. In our example above, Pyramid hands
``hello_world`` a ``request`` that is :ref:`based on WebOb <webob_chapter>`.


Steps
=====

#. First we copy the results of the ``view_classes`` step:

   .. code-block:: bash

    $ cd ..; cp -r view_classes request_response; cd request_response
    $ $VENV/bin/pip install -e .

#. Simplify the routes in ``request_response/tutorial/__init__.py``:

   .. literalinclude:: request_response/tutorial/__init__.py
    :linenos:

#. We only need one view in ``request_response/tutorial/views.py``:

   .. literalinclude:: request_response/tutorial/views.py
    :linenos:

#. Update the tests in ``request_response/tutorial/tests.py``:

   .. literalinclude:: request_response/tutorial/tests.py
    :linenos:

#. Now run the tests:

   .. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py -q
    .....
    5 passed in 0.30 seconds

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in your browser. You will be redirected to
   http://localhost:6543/plain.

#. Open http://localhost:6543/plain?name=alice in your browser.


Analysis
========

In this view class, we have two routes and two views, with the first leading to
the second by an HTTP redirect. Pyramid can :ref:`generate redirects
<http_redirect>` by returning a special object from a view or raising a special
exception.

In this Pyramid view, we get the URL being visited from ``request.url``. Also,
if you visited http://localhost:6543/plain?name=alice, the name is included in
the body of the response:

.. code-block:: text

  URL http://localhost:6543/plain?name=alice with name: alice

Finally, we set the response's content type and body, then return the response.

We updated the unit and functional tests to prove that our code does the
redirection, but also handles sending and not sending ``/plain?name``.


Extra credit
============

#. Could we also ``raise HTTPFound(location='/plain')`` instead of returning
   it?  If so, what's the difference?

.. seealso:: :ref:`webob_chapter`,
   :ref:`generate redirects <http_redirect>`
