.. _qtut_view_classes:

======================================
09: Organizing Views With View Classes
======================================

Change our view functions to be methods on a view class, then move some
declarations to the class level.


Background
==========

So far our views have been simple, free-standing functions. Many times your
views are related to one another. They may be different ways to look at or work
on the same data, or be a REST API that handles multiple operations. Grouping
these views together as a :ref:`view class <class_as_view>` makes sense:

- Group views.

- Centralize some repetitive defaults.

- Share some state and helpers.

In this step we just do the absolute minimum to convert the existing views to a
view class. In a later tutorial step, we'll examine view classes in depth.


Objectives
==========

- Group related views into a view class.

- Centralize configuration with class-level ``@view_defaults``.


Steps
=====

#. First we copy the results of the previous step:

   .. code-block:: bash

    $ cd ..; cp -r templating view_classes; cd view_classes
    $ $VENV/bin/pip install -e .

#. Our ``view_classes/tutorial/views.py`` now has a view class with our two
   views:

   .. literalinclude:: view_classes/tutorial/views.py
    :linenos:

#. Our unit tests in ``view_classes/tutorial/tests.py`` don't run, so let's
   modify them to import the view class, and make an instance before getting a
   response:

   .. literalinclude:: view_classes/tutorial/tests.py
    :linenos:

#. Now run the tests:

   .. code-block:: bash


    $ $VENV/bin/py.test tutorial/tests.py -q
    ....
    4 passed in 0.34 seconds

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ and http://localhost:6543/howdy in your browser.


Analysis
========

To ease the transition to view classes, we didn't introduce any new
functionality. We simply changed the view functions to methods on a view class,
then updated the tests.

In our ``TutorialViews`` view class, you can see that our two view classes are
logically grouped together as methods on a common class. Since the two views
shared the same template, we could move that to a ``@view_defaults`` decorator
at the class level.

The tests needed to change. Obviously we needed to import the view class. But
you can also see the pattern in the tests of instantiating the view class with
the dummy request first, then calling the view method being tested.

.. seealso:: :ref:`class_as_view`
