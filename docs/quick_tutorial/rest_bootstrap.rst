=========================================
27: Beginning REST with Twitter Bootstrap
=========================================

Begin making a REST application by adding Twitter Bootstrap, jQuery,
and a common layout.

Objectives
==========

- Switch to Jinja2

- Make a "layout" that is shared between templates

- Introduce jQuery and Twitter Bootstrap as well as local static
  resources

Steps
=====

#. We are going to use the previous step as our starting point:

   .. code-block:: bash

    (env27)$ cd ..; cp -r traversal_zodb rest_bootstrap; cd rest_bootstrap
    (env27)$ mkdir tutorial/static; mkdir tutorial/templates

#. Introduce ``pyramid_jinja2`` dependency in
   ``rest_bootstrap/setup.py``:

   .. literalinclude:: rest_bootstrap/setup.py
      :linenos:

#. We can now install our project:

   .. code-block:: bash

    (env27)$ python setup.py develop

#. Modify our ``rest_bootstrap/development.ini`` to include
   ``pyramid_jinja2`` configuration:

   .. literalinclude:: rest_bootstrap/development.ini
      :language: ini
      :linenos:

#. Our startup code in ``rest_bootstrap/tutorial/__init__.py`` gets
   a static view:

   .. literalinclude:: rest_bootstrap/tutorial/__init__.py
      :linenos:

#. Our home view in ``rest_bootstrap/tutorial/views.py`` references
   a Jinja2 template:

   .. literalinclude:: rest_bootstrap/tutorial/views.py
      :linenos:

#. Our site template in
   ``rest_bootstrap/tutorial/templates/site.jinja2``
   references a master layout:

   .. literalinclude:: rest_bootstrap/tutorial/templates/site.jinja2
    :language: html
    :linenos:

#. Add the master layout template in
   ``rest_bootstrap/tutorial/templates/layout.jinja2``:

   .. literalinclude:: rest_bootstrap/tutorial/templates/layout.jinja2
    :language: html
    :linenos:

#. A small amount of stying in
   ``rest_bootstrap/tutorial/static/site.css``:

   .. literalinclude:: rest_bootstrap/tutorial/static/site.css
    :language: css
    :linenos:

#. Run your Pyramid application with:

   .. code-block:: bash

    (env27)$ pserve development.ini --reload

#. Open ``http://localhost:6543/`` in your browser.

