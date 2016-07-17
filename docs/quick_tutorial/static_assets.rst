.. _qtut_static_assets:

==========================================
13: CSS/JS/Images Files With Static Assets
==========================================

Of course the Web is more than just markup. You need static assets: CSS, JS,
and images. Let's point our web app at a directory where Pyramid will serve
some static assets.

Objectives
==========

- Publish a directory of static assets at a URL.

- Use Pyramid to help generate URLs to files in that directory.


Steps
=====

#. First we copy the results of the ``view_classes`` step:

   .. code-block:: bash

    $ cd ..; cp -r view_classes static_assets; cd static_assets
    $ $VENV/bin/pip install -e .

#. We add a call ``config.add_static_view`` in
   ``static_assets/tutorial/__init__.py``:

   .. literalinclude:: static_assets/tutorial/__init__.py
    :linenos:

#. We can add a CSS link in the ``<head>`` of our template at
   ``static_assets/tutorial/home.pt``:

   .. literalinclude:: static_assets/tutorial/home.pt
    :language: html

#. Add a CSS file at ``static_assets/tutorial/static/app.css``:

   .. literalinclude:: static_assets/tutorial/static/app.css
    :language: css

#. Make sure we haven't broken any existing code by running the tests:

   .. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py -q
    ....
    4 passed in 0.50 seconds

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in your browser and note the new font.


Analysis
========

We changed our WSGI application to map requests under
http://localhost:6543/static/ to files and directories inside a ``static``
directory inside our ``tutorial`` package. This directory contained
``app.css``.

We linked to the CSS in our template. We could have hard-coded this link to
``/static/app.css``. But what if the site is later moved under
``/somesite/static/``? Or perhaps the web developer changes the arrangement on
disk? Pyramid gives a helper that provides flexibility on URL generation:

.. code-block:: html

  ${request.static_url('tutorial:static/app.css')}

This matches the ``path='tutorial:static'`` in our ``config.add_static_view``
registration. By using ``request.static_url`` to generate the full URL to the
static assets, you both ensure you stay in sync with the configuration and gain
refactoring flexibility later.


Extra credit
============

#. There is also a ``request.static_path`` API.  How does this differ from 
   ``request.static_url``?

.. seealso:: :ref:`assets_chapter`,
   :ref:`preventing_http_caching`, and
   :ref:`influencing_http_caching`
