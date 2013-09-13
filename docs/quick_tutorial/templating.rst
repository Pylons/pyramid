===================================
08: HTML Generation With Templating
===================================

Most web frameworks don't embed HTML in programming code. Instead,
they pass data into a templating system. In this step we look at the
basics of using HTML templates in Pyramid.

Background
==========

Ouch. We have been making our own ``Response`` and filling the response
body with HTML. You usually won't embed an HTML string directly in
Python, but instead, will use a templating language.

Pyramid doesn't mandate a particular database system, form library,
etc. It encourages replaceability. This applies equally to templating,
which is fortunate: developers have strong views about template
languages. That said, Pyramid bundles Chameleon and Mako,
so in this step, let's use Chameleon as an example.

Objectives
==========

- Generate HTML from template files

- Connect the templates as "renderers" for view code

- Change the view code to simply return data

Steps
=====

#. Let's begin by using the previous package as a starting point for a new
   distribution, then making it active:

   .. code-block:: bash

    (env27)$ cd ..; cp -r views templating; cd templating
    (env27)$ python setup.py develop

#. Our ``templating/tutorial/views.py`` no longer has HTML in it:

   .. literalinclude:: templating/tutorial/views.py
    :linenos:

#. Instead we have ``templating/tutorial/home.pt`` as a template:

   .. literalinclude:: templating/tutorial/home.pt
    :language: html

#. For convenience, change ``templating/development.ini`` to reload
   templates automatically with ``pyramid.reload_templates``:

   .. literalinclude:: templating/development.ini
    :language: ini

#. Our unit tests in ``templating/tutorial/tests.py`` can focus on
   data:

   .. literalinclude:: templating/tutorial/tests.py
    :linenos:

#. Now run the tests:

   .. code-block:: bash


    (env27)$ nosetests tutorial
    .
    ----------------------------------------------------------------------
    Ran 4 tests in 0.141s

    OK

#. Run your Pyramid application with:

   .. code-block:: bash

    (env27)$ pserve development.ini --reload

#. Open ``http://localhost:6543/`` and ``http://localhost:6543/howdy``
   in your browser.

Analysis
========

Ahh, that looks better. We have a view that is focused on Python code.
Our ``@view_config`` decorator specifies a
:term:`pyramid:renderer` that points
our template file. Our view then simply returns data which is then
supplied to our template. Note that we used the same template for both
views.

Note the effect on testing. We can focus on having a data-oriented
contract with our view code.

.. seealso:: :ref:`pyramid:templates_chapter`,
   :ref:`pyramid:debugging_templates`, and
   :ref:`pyramid:mako_templates`
