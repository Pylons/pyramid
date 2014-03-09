.. _qtut_jinja2:

==============================
12: Templating With ``jinja2``
==============================

We just said Pyramid doesn't prefer one templating language over
another. Time to prove it. Jinja2 is a popular templating system,
used in Flask and modelled after Django's templates. Let's add
``pyramid_jinja2``, a Pyramid :term:`add-on` which enables Jinja2 as a
:term:`renderer` in our Pyramid applications.

Objectives
==========

- Show Pyramid's support for different templating systems

- Learn about installing Pyramid add-ons

Steps
=====

#. In this step let's start by installing the ``pyramid_jinja2``
   add-on, the copying the ``view_class`` step's directory:

   .. code-block:: bash

    $ cd ..; cp -r view_classes jinja2; cd jinja2
    $ $VENV/bin/python setup.py develop
    $ $VENV/bin/easy_install pyramid_jinja2

#. We need to include ``pyramid_jinja2`` in
   ``jinja2/tutorial/__init__.py``:

   .. literalinclude:: jinja2/tutorial/__init__.py
    :linenos:

#. Our ``jinja2/tutorial/views.py`` simply changes its ``renderer``:

   .. literalinclude:: jinja2/tutorial/views.py
    :linenos:

#. Add ``jinja2/tutorial/home.jinja2`` as a template:

   .. literalinclude:: jinja2/tutorial/home.jinja2
    :language: html

#. Get the ``pyramid.includes`` into the functional test setup in
   ``jinja2/tutorial/tests.py``:

   .. literalinclude:: jinja2/tutorial/tests.py
    :linenos:

#. Now run the tests:

   .. code-block:: bash

    $ $VENV/bin/nosetests tutorial

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in your browser.

Analysis
========

Getting a Pyramid add-on into Pyramid is simple. First you use normal
Python package installation tools to install the add-on package into
your Python. You then tell Pyramid's configurator to run the setup code
in the add-on. In this case the setup code told Pyramid to make a new
"renderer" available that looked for ``.jinja2`` file extensions.

Our view code stayed largely the same. We simply changed the file
extension on the renderer. For the template, the syntax for Chameleon
and Jinja2's basic variable insertion is very similar.

Our functional tests don't have ``development.ini`` so they needed the
``pyramid.includes`` to be setup in the test setup.

Extra Credit
============

#. Our project now depends on ``pyramid_jinja2``. We installed that
   dependency manually. What is another way we could have made the
   association?

#. We used ``development.ini`` to get the :term:`configurator` to
   load ``pyramid_jinja2``'s configuration. What is another way could
   include it into the config?

.. seealso:: `Jinja2 homepage <http://jinja.pocoo.org/>`_,
   and
   :ref:`pyramid_jinja2 Overview <jinja2:overview>`
