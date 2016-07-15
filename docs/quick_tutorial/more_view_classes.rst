.. _qtut_more_view_classes:

==========================
15: More With View Classes
==========================

Group views into a class, sharing configuration, state, and logic.


Background
==========

As part of its mission to help build more ambitious web applications, Pyramid
provides many more features for views and view classes.

The Pyramid documentation discusses views as a Python "callable". This callable
can be a function, an object with a ``__call__``, or a Python class. In this
last case, methods on the class can be decorated with ``@view_config`` to
register the class methods with the :term:`configurator` as a view.

At first, our views were simple, free-standing functions. Many times your views
are related: different ways to look at or work on the same data, or a REST API
that handles multiple operations. Grouping these together as a :ref:`view class
<class_as_view>` makes sense:

- Group views.

- Centralize some repetitive defaults.

- Share some state and helpers.

Pyramid views have :ref:`view predicates <view_configuration_parameters>` that
determine which view is matched to a request, based on factors such as the
request method, the form parameters, and so on. These predicates provide many
axes of flexibility.

The following shows a simple example with four operations: view a home page
which leads to a form, save a change, and press the delete button.


Objectives
==========

- Group related views into a view class.

- Centralize configuration with class-level ``@view_defaults``.

- Dispatch one route/URL to multiple views based on request data.

- Share states and logic between views and templates via the view class.


Steps
=====

#. First we copy the results of the previous step:

   .. code-block:: bash

    $ cd ..; cp -r templating more_view_classes; cd more_view_classes
    $ $VENV/bin/pip install -e .

#. Our route in ``more_view_classes/tutorial/__init__.py`` needs some
   replacement patterns:

   .. literalinclude:: more_view_classes/tutorial/__init__.py
    :linenos:

#. Our ``more_view_classes/tutorial/views.py`` now has a view class with
   several views:

   .. literalinclude:: more_view_classes/tutorial/views.py
    :linenos:

#. Our primary view needs a template at ``more_view_classes/tutorial/home.pt``:

   .. literalinclude:: more_view_classes/tutorial/home.pt
    :language: html

#. Ditto for our other view from the previous section at
   ``more_view_classes/tutorial/hello.pt``:

   .. literalinclude:: more_view_classes/tutorial/hello.pt
    :language: html

#. We have an edit view that also needs a template at
   ``more_view_classes/tutorial/edit.pt``:

   .. literalinclude:: more_view_classes/tutorial/edit.pt
    :language: html

#. And finally the delete view's template at
   ``more_view_classes/tutorial/delete.pt``:

   .. literalinclude:: more_view_classes/tutorial/delete.pt
    :language: html

#. Our tests in ``more_view_classes/tutorial/tests.py`` fail, so let's modify
   them:

   .. literalinclude:: more_view_classes/tutorial/tests.py
    :linenos:

#. Now run the tests:

   .. code-block:: bash

    $ $VENV/bin/py.test tutorial/tests.py -q
    ..
    2 passed in 0.40 seconds

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/howdy/jane/doe in your browser. Click the
   ``Save`` and ``Delete`` buttons, and watch the output in the console window.


Analysis
========

As you can see, the four views are logically grouped together. Specifically:

- We have a ``home`` view available at http://localhost:6543/ with a clickable
  link to the ``hello`` view.

- The second view is returned when you go to ``/howdy/jane/doe``. This URL is
  mapped to the ``hello`` route that we centrally set using the optional
  ``@view_defaults``.

- The third view is returned when the form is submitted with a ``POST`` method.
  This rule is specified in the ``@view_config`` for that view.

- The fourth view is returned when clicking on a button such as ``<input
  type="submit" name="form.delete" value="Delete"/>``.

In this step we show, using the following information as criteria, how to
decide which view to use:

- Method of the HTTP request (``GET``, ``POST``, etc.)

- Parameter information in the request (submitted form field names)

We also centralize part of the view configuration to the class level with
``@view_defaults``, then in one view, override that default just for that one
view. Finally, we put this commonality between views to work in the view class
by sharing:

- State assigned in ``TutorialViews.__init__``

- A computed value

These are then available both in the view methods and in the templates (e.g.,
``${view.view_name}`` and ``${view.full_name}``).

As a note, we made a switch in our templates on how we generate URLs. We
previously hardcoded the URLs, such as:

.. code-block:: html

  <a href="/howdy/jane/doe">Howdy</a>

In ``home.pt`` we switched to:

.. code-block:: xml

  <a href="${request.route_url('hello', first='jane',
        last='doe')}">form</a>

Pyramid has rich facilities to help generate URLs in a flexible, non-error
prone fashion.

Extra credit
============

#. Why could our template do ``${view.full_name}`` and not have to do
   ``${view.full_name()}``?

#. The ``edit`` and ``delete`` views are both receive ``POST`` requests. Why
   does the ``edit`` view configuration not catch the ``POST`` used by
   ``delete``?

#. We used Python ``@property`` on ``full_name``. If we reference this many
   times in a template or view code, it would re-compute this every time. Does
   Pyramid provide something that will cache the initial computation on a
   property?

#. Can you associate more than one route with the same view?

#. There is also a ``request.route_path`` API. How does this differ from
   ``request.route_url``?

.. seealso:: :ref:`class_as_view`, `Weird Stuff You Can Do With
   URL Dispatch <http://www.plope.com/weird_pyramid_urldispatch>`_
