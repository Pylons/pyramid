.. _qtut_authorization:

===========================================
21: Protecting Resources With Authorization
===========================================

Assign security statements to resources describing the permissions required to
perform an operation.


Background
==========

Our application has URLs that allow people to add/edit/delete content via a web
browser. Time to add security to the application. Let's protect our add/edit
views to require a login (username of ``editor`` and password of ``editor``).
We will allow the other views to continue working without a password.


Objectives
==========

- Introduce the Pyramid concepts of authentication, authorization, permissions,
  and access control lists (ACLs).

- Make a :term:`root factory` that returns an instance of our class for the top
  of the application.

- Assign security statements to our root resource.

- Add a permissions predicate on a view.

- Provide a :term:`Forbidden view` to handle visiting a URL without adequate
  permissions.


Steps
=====

#. We are going to use the authentication step as our starting point:

   .. code-block:: bash

    $ cd ..; cp -r authentication authorization; cd authorization
    $ $VENV/bin/pip install -e .

#. Start by changing ``authorization/tutorial/__init__.py`` to specify a root
   factory to the :term:`configurator`:

   .. literalinclude:: authorization/tutorial/__init__.py
    :linenos:

#. That means we need to implement ``authorization/tutorial/resources.py``:

   .. literalinclude:: authorization/tutorial/resources.py
    :linenos:

#. Change ``authorization/tutorial/views.py`` to require the ``edit``
   permission on the ``hello`` view and implement the forbidden view:

   .. literalinclude:: authorization/tutorial/views.py
    :linenos:

#. Run your Pyramid application with:

   .. code-block:: bash

    $ $VENV/bin/pserve development.ini --reload

#. Open http://localhost:6543/ in a browser.

#. If you are still logged in, click the "Log Out" link.

#. Visit http://localhost:6543/howdy in a browser. You should be asked to
   login.


Analysis
========

This simple tutorial step can be boiled down to the following:

- A view can require a *permission* (``edit``).

- The context for our view (the ``Root``) has an access control list (ACL).

- This ACL says that the ``edit`` permission is available on ``Root``  to the
  ``group:editors`` *principal*.

- The registered ``groupfinder`` answers whether a particular user (``editor``)
  has a particular group (``group:editors``).

In summary, ``hello`` wants ``edit`` permission, ``Root`` says
``group:editors`` has ``edit`` permission.

Of course, this only applies on ``Root``. Some other part of the site (a.k.a.
*context*) might have a different ACL.

If you are not logged in and visit ``/howdy``, you need to get shown the login
screen. How does Pyramid know what is the login page to use? We explicitly told
Pyramid that the ``login`` view should be used by decorating the view with
``@forbidden_view_config``.


Extra credit
============

#. Do I have to put a ``renderer`` in my ``@forbidden_view_config`` decorator?

#. Perhaps you would like the experience of not having enough permissions
   (forbidden) to be richer. How could you change this?

#. Perhaps we want to store security statements in a database and allow editing
   via a browser. How might this be done?

#. What if we want different security statements on different kinds of objects?
   Or on the same kinds of objects, but in different parts of a URL hierarchy?
