=========================
28: REST with Ajax Layout
=========================

Produce a grid-like UI to prepare for async REST operations.

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    (env27)$ cd ..; cp -r rest_bootstrap rest_ajax_layout; cd rest_ajax_layout
    (env27)$ python setup.py develop

#. Get a new menu item for ``Folders`` in
   ``rest_ajax_layout/tutorial/templates/layout.jinja2``:

   .. literalinclude:: rest_ajax_layout/tutorial/templates/layout.jinja2
    :language: html
    :linenos:

#. In  ``rest_ajax_layout/tutorial/views.py``, add a JSON view and remove
   unused previous views:

   .. literalinclude:: rest_ajax_layout/tutorial/views.py
      :linenos:

#. Create a template at
   ``rest_ajax_layout/tutorial/templates/folder.jinja2``:

   .. literalinclude:: rest_ajax_layout/tutorial/templates/folder.jinja2
    :language: html
    :linenos:

#. Do some cleanup:

   .. code-block:: bash

    (env27)$ rm tutorial/templates/*.pt

#. Run your Pyramid application with:

   .. code-block:: bash

    (env27)$ pserve development.ini --reload

#. Open ``http://localhost:6543/`` in your browser.

