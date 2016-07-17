.. _qtut_routing:

==========================================
11: Dispatching URLs To Views With Routing
==========================================

Routing matches incoming URL patterns to view code. Pyramid's routing has a
number of useful features.


Background
==========

Writing web applications usually means sophisticated URL design. We just saw
some Pyramid machinery for requests and views. Let's look at features that help
in routing.

Previously we saw the basics of routing URLs to views in Pyramid.

- Your project's "setup" code registers a route name to be used when matching
  part of the URL

- Elsewhere a view is configured to be called for that route name.

.. note::

    Why do this twice? Other Python web frameworks let you create a route and
    associate it with a view in one step. As illustrated in
    :ref:`routes_need_ordering`, multiple routes might match the same URL
    pattern. Rather than provide ways to help guess, Pyramid lets you be
    explicit in ordering. Pyramid also gives facilities to avoid the problem.
    It's relatively easy to build a system that uses implicit route ordering
    with Pyramid too. See `The Groundhog series of screencasts
    <http://static.repoze.org/casts/videotags.html>`_ if you're interested in
    doing so.


Objectives
==========

- Define a route that extracts part of the URL into a Python dictionary.

- Use that dictionary data in a view.


Steps
=====

#. First we copy the results of the ``view_classes`` step:

   .. code-block:: bash

    $ cd ..; cp -r view_classes routing; cd routing
    $ $VENV/bin/pip install -e .

#. Our ``routing/tutorial/__init__.py`` needs a route with a replacement
   pattern:

   .. literalinclude:: routing/tutorial/__init__.py
    :linenos:

#. We just need one view in ``routing/tutorial/views.py``:

   .. literalinclude:: routing/tutorial/views.py
    :linenos:

#. We just need one view in ``routing/tutorial/home.pt``:

   .. literalinclude:: routing/tutorial/home.pt
    :language: html
    :linenos:

#. Update ``routing/tutorial/tests.py``:

   .. literalinclude:: routing/tutorial/tests.py
    :linenos:

#. Now run the tests:

   .. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py -q
    ..
    2 passed in 0.39 seconds

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/howdy/amy/smith in your browser.


Analysis
========

In ``__init__.py`` we see an important change in our route declaration:

.. code-block:: python

    config.add_route('hello', '/howdy/{first}/{last}')

With this we tell the :term:`configurator` that our URL has a "replacement
pattern". With this, URLs such as ``/howdy/amy/smith`` will assign ``amy`` to
``first`` and ``smith`` to ``last``. We can then use this data in our view:

.. code-block:: python

    self.request.matchdict['first']
    self.request.matchdict['last']

``request.matchdict`` contains values from the URL that match the "replacement
patterns" (the curly braces) in the route declaration. This information can
then be used anywhere in Pyramid that has access to the request.

Extra credit
============

#. What happens if you to go the URL http://localhost:6543/howdy? Is this the
   result that you expected?

.. seealso:: `Weird Stuff You Can Do With URL Dispatch
   <http://www.plope.com/weird_pyramid_urldispatch>`_
