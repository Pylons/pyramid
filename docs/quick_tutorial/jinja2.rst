.. _qtut_jinja2:

==============================
12: Templating With ``jinja2``
==============================

We just said Pyramid doesn't prefer one templating language over another. Time
to prove it. Jinja2 is a popular templating system, used in Flask and modeled
after Django's templates. Let's add ``pyramid_jinja2``, a Pyramid
:term:`add-on` which enables Jinja2 as a :term:`renderer` in our Pyramid
applications.


Objectives
==========

- Show Pyramid's support for different templating systems.

- Learn about installing Pyramid add-ons.


Steps
=====

#. In this step let's start by copying the ``view_class`` step's  directory,
   and then installing the ``pyramid_jinja2`` add-on.

   .. code-block:: bash

    $ cd ..; cp -r view_classes jinja2; cd jinja2
    $ $VENV/bin/pip install -e .
    $ $VENV/bin/pip install pyramid_jinja2

#. We need to include ``pyramid_jinja2`` in ``jinja2/tutorial/__init__.py``:

   .. literalinclude:: jinja2/tutorial/__init__.py
    :linenos:

#. Our ``jinja2/tutorial/views.py`` simply changes its ``renderer``:

   .. literalinclude:: jinja2/tutorial/views.py
    :linenos:

#. Add ``jinja2/tutorial/home.jinja2`` as a template:

   .. literalinclude:: jinja2/tutorial/home.jinja2
    :language: html

#. Now run the tests:

   .. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py -q
    ....
    4 passed in 0.40 seconds

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in your browser.


Analysis
========

Getting a Pyramid add-on into Pyramid is simple. First you use normal Python
package installation tools to install the add-on package into your Python
virtual environment. You then tell Pyramid's configurator to run the setup code
in the add-on. In this case the setup code told Pyramid to make a new
"renderer" available that looked for ``.jinja2`` file extensions.

Our view code stayed largely the same. We simply changed the file extension on
the renderer. For the template, the syntax for Chameleon and Jinja2's basic
variable insertion is very similar.


Extra credit
============

#. Our project now depends on ``pyramid_jinja2``. We installed that dependency
   manually. What is another way we could have made the association?

#. We used ``config.include`` which is an imperative configuration to get the
   :term:`Configurator` to load ``pyramid_jinja2``'s configuration. What is
   another way could include it into the config?

.. seealso:: `Jinja2 homepage <http://jinja.pocoo.org/>`_, and
   :ref:`pyramid_jinja2 Overview <jinja2:overview>`
