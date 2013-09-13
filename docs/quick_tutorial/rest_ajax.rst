==================
29: REST with Ajax
==================

Use Ajax operations to talk to a REST interface.

Objectives
==========

- Populate a list with JSON data

- Update contents with client-side forms that post to REST operations

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    (env27)$ cd ..; cp -r rest_ajax_layout rest_ajax; cd rest_ajax
    (env27)$ python setup.py develop

#. Let's first add a Javascript file that implements our browser-side
   logic and talks to the REST service:

#. Introduce ``pyramid_jinja2`` dependency in
   ``rest_ajax/tutorial/static/site.js``:

   .. literalinclude:: rest_ajax/tutorial/static/site.js
    :language: js
    :linenos:

#. Add a ``<script>`` reference to this at the bottom of
   ``rest_ajax/tutorial/templates/layout.jinja2``

   .. literalinclude:: rest_ajax/tutorial/templates/layout.jinja2
    :language: html
    :linenos:

#. Update ``rest_ajax/tutorial/templates/folder.jinja2`` to include a
   modal dialog:

   .. literalinclude:: rest_ajax/tutorial/templates/folder.jinja2
    :language: html
    :linenos:

#. Our views in ``rest_ajax/tutorial/views.py`` need to handle our
   REST operations:

   .. literalinclude:: rest_ajax/tutorial/views.py
      :linenos:

#. Run your Pyramid application with:

   .. code-block:: bash

    (env27)$ pserve development.ini --reload

#. Open ``http://localhost:6543/`` in your browser and
   add (+ button), edit (click link), and delete (click trash icon)
   items in the root folder.