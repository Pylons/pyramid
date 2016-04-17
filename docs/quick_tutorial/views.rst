.. _qtut_views:

=================================
07: Basic Web Handling With Views
=================================

Organize a views module with decorators and multiple views.


Background
==========

For the examples so far, the ``hello_world`` function is a "view". In Pyramid,
views are the primary way to accept web requests and return responses.

So far our examples place everything in one file:

- The view function

- Its registration with the configurator

- The route to map it to a URL

- The WSGI application launcher

Let's move the views out to their own ``views.py`` module and change our
startup code to scan that module, looking for decorators that set up the views.
Let's also add a second view and update our tests.


Objectives
==========

- Move views into a module that is scanned by the configurator.

- Create decorators that do declarative configuration.


Steps
=====

#. Let's begin by using the previous package as a starting point for a new
   distribution, then making it active:

   .. code-block:: bash

    $ cd ..; cp -r functional_testing views; cd views
    $ $VENV/bin/pip install -e .

#. Our ``views/tutorial/__init__.py`` gets a lot shorter:

   .. literalinclude:: views/tutorial/__init__.py
    :linenos:

#. Let's add a module ``views/tutorial/views.py`` that is focused on
   handling requests and responses:

   .. literalinclude:: views/tutorial/views.py
    :linenos:

#. Update the tests to cover the two new views:

   .. literalinclude:: views/tutorial/tests.py
    :linenos:

#. Now run the tests:

   .. code-block:: bash


    $ $VENV/bin/py.test tutorial/tests.py -q
    ....
    4 passed in 0.28 seconds

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ and http://localhost:6543/howdy
   in your browser.


Analysis
========

We added some more URLs, but we also removed the view code from the application
startup code in ``tutorial/__init__.py``. Our views, and their view
registrations (via decorators) are now in a module ``views.py``, which is
scanned via ``config.scan('.views')``.

We have two views, each leading to the other. If you start at
http://localhost:6543/, you get a response with a link to the next view. The
``hello`` view (available at the URL ``/howdy``) has a link back to the first
view.

This step also shows that the name appearing in the URL, the name of the
"route" that maps a URL to a view, and the name of the view, can all be
different. More on routes later.

Earlier we saw ``config.add_view`` as one way to configure a view. This section
introduces ``@view_config``. Pyramid's configuration supports :term:`imperative
configuration`, such as the ``config.add_view`` in the previous example. You
can also use :term:`declarative configuration`, in which a Python
:term:`python:decorator` is placed on the line above the view. Both approaches
result in the same final configuration, thus usually, it is simply a matter of
taste.


Extra credit
============

#. What does the dot in ``.views`` signify?

#. Why might ``assertIn`` be a better choice in testing the text in responses
   than ``assertEqual``?

.. seealso:: :ref:`views_chapter`,
   :ref:`view_config_chapter`, and
   :ref:`debugging_view_configuration`
