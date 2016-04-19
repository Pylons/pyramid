.. _qtut_json:

========================================
14: AJAX Development With JSON Renderers
========================================

Modern web apps are more than rendered HTML. Dynamic pages now use JavaScript
to update the UI in the browser by requesting server data as JSON. Pyramid
supports this with a *JSON renderer*.


Background
==========

As we saw in :doc:`templating`, view declarations can specify a renderer.
Output from the view is then run through the renderer, which generates and
returns the response. We first used a Chameleon renderer, then a Jinja2
renderer.

Renderers aren't limited, however, to templates that generate HTML. Pyramid
supplies a JSON renderer which takes Python data, serializes it to JSON, and
performs some other functions such as setting the content type. In fact you can
write your own renderer (or extend a built-in renderer) containing custom logic
for your unique application.


Steps
=====

#. First we copy the results of the ``view_classes`` step:

   .. code-block:: bash

    $ cd ..; cp -r view_classes json; cd json
    $ $VENV/bin/pip install -e .

#. We add a new route for ``hello_json`` in ``json/tutorial/__init__.py``:

   .. literalinclude:: json/tutorial/__init__.py
    :linenos:

#. Rather than implement a new view, we will "stack" another decorator on the
   ``hello`` view in ``views.py``:

   .. literalinclude:: json/tutorial/views.py
    :linenos:

#. We need a new functional test at the end of ``json/tutorial/tests.py``:

   .. literalinclude:: json/tutorial/tests.py
    :linenos:

#. Run the tests:

   .. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py -q
    .....
    5 passed in 0.47 seconds


#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/howdy.json in your browser and you will see the
   resulting JSON response.


Analysis
========

Earlier we changed our view functions and methods to return Python data. This
change to a data-oriented view layer made test writing easier, decoupling the
templating from the view logic.

Since Pyramid has a JSON renderer as well as the templating renderers, it is an
easy step to return JSON. In this case we kept the exact same view and arranged
to return a JSON encoding of the view data. We did this by:

- Adding a route to map ``/howdy.json`` to a route name.

- Providing a ``@view_config`` that associated that route name with an existing
  view.

- *Overriding* the view defaults in the view config that mentions the
  ``hello_json`` route, so that when the route is matched, we use the JSON
  renderer rather than the ``home.pt`` template renderer that would otherwise 
  be used.

In fact, for pure AJAX-style web applications, we could re-use the existing
route by using Pyramid's view predicates to match on the ``Accepts:`` header
sent by modern AJAX implementations.

Pyramid's JSON renderer uses the base Python JSON encoder, thus inheriting its
strengths and weaknesses. For example, Python can't natively JSON encode
DateTime objects. There are a number of solutions for this in Pyramid,
including extending the JSON renderer with a custom renderer.

.. seealso:: :ref:`views_which_use_a_renderer`,
   :ref:`json_renderer`, and
   :ref:`adding_and_overriding_renderers`
