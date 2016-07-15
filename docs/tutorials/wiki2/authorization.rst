.. _wiki2_adding_authorization:

====================
Adding authorization
====================

In the last chapter we built :term:`authentication` into our wiki. We also
went one step further and used the ``request.user`` object to perform some
explicit :term:`authorization` checks. This is fine for a lot of applications,
but :app:`Pyramid` provides some facilities for cleaning this up and decoupling
the constraints from the view function itself.

We will implement access control with the following steps:

* Update the :term:`authentication policy` to break down the :term:`userid`
  into a list of :term:`principals <principal>` (``security.py``).
* Define an :term:`authorization policy` for mapping users, resources and
  permissions (``security.py``).
* Add new :term:`resource` definitions that will be used as the :term:`context`
  for the wiki pages (``routes.py``).
* Add an :term:`ACL` to each resource (``routes.py``).
* Replace the inline checks on the views with :term:`permission` declarations
  (``views/default.py``).


Add user principals
-------------------

A :term:`principal` is a level of abstraction on top of the raw :term:`userid`
that describes the user in terms of its capabilities, roles, or other
identifiers that are easier to generalize. The permissions are then written
against the principals without focusing on the exact user involved.

:app:`Pyramid` defines two builtin principals used in every application:
:attr:`pyramid.security.Everyone` and :attr:`pyramid.security.Authenticated`.
On top of these we have already mentioned the required principals for this
application in the original design. The user has two possible roles: ``editor``
or ``basic``. These will be prefixed by the string ``role:`` to avoid clashing
with any other types of principals.

Open the file ``tutorial/security.py`` and edit it as follows:

.. literalinclude:: src/authorization/tutorial/security.py
   :linenos:
   :emphasize-lines: 3-6,17-24
   :language: python

Only the highlighted lines need to be added.

Note that the role comes from the ``User`` object. We also add the ``user.id``
as a principal for when we want to allow that exact user to edit pages which
they have created.


Add the authorization policy
----------------------------

We already added the :term:`authorization policy` in the previous chapter
because :app:`Pyramid` requires one when adding an
:term:`authentication policy`. However, it was not used anywhere, so we'll
mention it now.

In the file ``tutorial/security.py``, notice the following lines:

.. literalinclude:: src/authorization/tutorial/security.py
   :lines: 38-40
   :lineno-match:
   :emphasize-lines: 2
   :language: python

We're using the :class:`pyramid.authorization.ACLAuthorizationPolicy`, which
will suffice for most applications. It uses the :term:`context` to define the
mapping between a :term:`principal` and :term:`permission` for the current
request via the ``__acl__``.


Add resources and ACLs
----------------------

Resources are the hidden gem of :app:`Pyramid`. You've made it!

Every URL in a web application represents a :term:`resource` (the "R" in
Uniform Resource Locator). Often the resource is something in your data model,
but it could also be an abstraction over many models.

Our wiki has two resources:

#. A ``NewPage``. Represents a potential ``Page`` that does not exist. Any
   logged-in user, having either role of ``basic`` or ``editor``, can create
   pages.

#. A ``PageResource``. Represents a ``Page`` that is to be viewed or edited.
   ``editor`` users, as well as the original creator of the ``Page``, may edit
   the ``PageResource``. Anyone may view it.

.. note::

   The wiki data model is simple enough that the ``PageResource`` is mostly
   redundant with our ``models.Page`` SQLAlchemy class. It is completely valid
   to combine these into one class. However, for this tutorial, they are
   explicitly separated to make clear the distinction between the parts about
   which :app:`Pyramid` cares versus application-defined objects.

There are many ways to define these resources, and they can even be grouped
into collections with a hierarchy. However, we're keeping it simple here!

Open the file ``tutorial/routes.py`` and edit the following lines:

.. literalinclude:: src/authorization/tutorial/routes.py
   :linenos:
   :emphasize-lines: 1-11,17-
   :language: python

The highlighted lines need to be edited or added.

The ``NewPage`` class has an ``__acl__`` on it that returns a list of mappings
from :term:`principal` to :term:`permission`. This defines *who* can do *what*
with that :term:`resource`. In our case we want to allow only those users with
the principals of either ``role:editor`` or ``role:basic`` to have the
``create`` permission:

.. literalinclude:: src/authorization/tutorial/routes.py
   :lines: 30-38
   :lineno-match:
   :emphasize-lines: 5-9
   :language: python

The ``NewPage`` is loaded as the :term:`context` of the ``add_page`` route by
declaring a ``factory`` on the route:

.. literalinclude:: src/authorization/tutorial/routes.py
   :lines: 18-19
   :lineno-match:
   :emphasize-lines: 1-2
   :language: python

The ``PageResource`` class defines the :term:`ACL` for a ``Page``. It uses an
actual ``Page`` object to determine *who* can do *what* to the page.

.. literalinclude:: src/authorization/tutorial/routes.py
   :lines: 47-
   :lineno-match:
   :emphasize-lines: 5-10
   :language: python

The ``PageResource`` is loaded as the :term:`context` of the ``view_page`` and
``edit_page`` routes by declaring a ``factory`` on the routes:

.. literalinclude:: src/authorization/tutorial/routes.py
   :lines: 17-21
   :lineno-match:
   :emphasize-lines: 1,4-5
   :language: python


Add view permissions
--------------------

At this point we've modified our application to load the ``PageResource``,
including the actual ``Page`` model in the ``page_factory``. The
``PageResource`` is now the :term:`context` for all ``view_page`` and
``edit_page`` views. Similarly the ``NewPage`` will be the context for the
``add_page`` view.

Open the file ``tutorial/views/default.py``.

First, you can drop a few imports that are no longer necessary:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 5-7
   :lineno-match:
   :emphasize-lines: 1
   :language: python

Edit the ``view_page`` view to declare the ``view`` permission, and remove the
explicit checks within the view:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 18-23
   :lineno-match:
   :emphasize-lines: 1-2,4
   :language: python

The work of loading the page has already been done in the factory, so we can
just pull the ``page`` object out of the ``PageResource``, loaded as
``request.context``. Our factory also guarantees we will have a ``Page``, as it
raises the ``HTTPNotFound`` exception if no ``Page`` exists, again simplifying
the view logic.

Edit the ``edit_page`` view to declare the ``edit`` permission:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 38-42
   :lineno-match:
   :emphasize-lines: 1-2,4
   :language: python

Edit the ``add_page`` view to declare the ``create`` permission:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 52-56
   :lineno-match:
   :emphasize-lines: 1-2,4
   :language: python

Note the ``pagename`` here is pulled off of the context instead of
``request.matchdict``. The factory has done a lot of work for us to hide the
actual route pattern.

The ACLs defined on each :term:`resource` are used by the :term:`authorization
policy` to determine if any :term:`principal` is allowed to have some
:term:`permission`. If this check fails (for example, the user is not logged
in) then an ``HTTPForbidden`` exception will be raised automatically. Thus
we're able to drop those exceptions and checks from the views themselves.
Rather we've defined them in terms of operations on a resource.

The final ``tutorial/views/default.py`` should look like the following:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :linenos:
   :language: python

Viewing the application in a browser
------------------------------------

We can finally examine our application in a browser (See
:ref:`wiki2-start-the-application`).  Launch a browser and visit each of the
following URLs, checking that the result is as expected:

- http://localhost:6543/ invokes the ``view_wiki`` view.  This always
  redirects to the ``view_page`` view of the ``FrontPage`` page object.  It
  is executable by any user.

- http://localhost:6543/FrontPage invokes the ``view_page`` view of the
  ``FrontPage`` page object. There is a "Login" link in the upper right corner
  while the user is not authenticated, else it is a "Logout" link when the user
  is authenticated.

- http://localhost:6543/FrontPage/edit_page invokes the ``edit_page`` view for
  the ``FrontPage`` page object.  It is executable by only the ``editor`` user.
  If a different user (or the anonymous user) invokes it, then a login form
  will be displayed. Supplying the credentials with the username ``editor`` and
  password ``editor`` will display the edit page form.

- http://localhost:6543/add_page/SomePageName invokes the ``add_page`` view for
  a page. If the page already exists, then it redirects the user to the
  ``edit_page`` view for the page object. It is executable by either the
  ``editor`` or ``basic`` user.  If a different user (or the anonymous user)
  invokes it, then a login form will be displayed. Supplying the credentials
  with either the username ``editor`` and password ``editor``, or username
  ``basic`` and password ``basic``, will display the edit page form.

- http://localhost:6543/SomePageName/edit_page invokes the ``edit_page`` view
  for an existing page, or generates an error if the page does not exist. It is
  editable by the ``basic`` user if the page was created by that user in the
  previous step. If, instead, the page was created by the ``editor`` user, then
  the login page should be shown for the ``basic`` user.

- After logging in (as a result of hitting an edit or add page and submitting
  the login form with the ``editor`` credentials), we'll see a "Logout" link in
  the upper right hand corner.  When we click it, we're logged out, redirected
  back to the front page, and a "Login" link is shown in the upper right hand
  corner.
