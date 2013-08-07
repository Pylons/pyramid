================================
Handling Web Requests With Views
================================

Free-standing functions are the regular way to do views. Many times,
though, you have several views that are closely related. For example,
a document might have many different ways to look at it,
or a form might submit to different targets, or a REST handler might
cover different operations.

Grouping these together makes logical sense. A view class lets you
group views, centralize some repetitive defaults, share some state
assignments, and use helper functions as class methods.

As an example, imagine we have some views around saying hello to a
person, then editing that person or perhaps deleting that person. They
might logically belong together. We could do these as independent
functions, but let's do them together as a view class:

.. literalinclude:: quick_glance/view_classes/views.py
    :start-after: Start View 1
    :end-before: End View 1

...and some routes that wire up the views to URLs:

.. literalinclude:: quick_glance/view_classes/app.py
    :start-after: Start Routes 1
    :end-before: End Routes 1

...and a form in ``hello_world.jinja2`` that submits to the second view:

.. literalinclude:: quick_glance/view_classes/hello_world.jinja2
    :language: html
    :start-after: Start Form 1
    :end-before: End Form 1

Just to review:

- The ``/howdy/amy`` URL matches the ``hello`` route, handled by the
  ``hello_view`` class method.