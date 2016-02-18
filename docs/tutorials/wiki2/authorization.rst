.. _wiki2_adding_authorization:

====================
Adding authorization
====================

In the last chapter we built :term:`authentication` into our wiki2. We also
went one step further and used the ``request.user`` object to perform some explicit :term:`authorization` checks. This is fine for a lot of
applications but :app:`Pyramid` provides some facilities for cleaning this
up and decoupling the constraints from the view function itself.

We will implement access control with the following steps:

* Update the :term:`authentication policy` to break down the
  :term:`userid` into a list of :term:`principals <principal>`
  (``security.py``).
* Define an :term:`authorization policy` for mapping users, resources and
  permissions (``security.py``).
* Add new :term:`resource` definitions that will be used as the
  :term:`context` for the wiki pages (``routes.py``).
* Add an :term:`ACL` to each resource (``routes.py``).
* Replace the inline checks on the views with :term:`permission` declarations
  (``views/default.py``).

Add user principals
-------------------

A :term:`principal` is a level of abstraction on top of the raw
:term:`userid` that describes the user in terms of capabilities, roles or
other identifiers that are easier to generalize. The permissions are then
written against the principals without focusing on the exact user involved.

:app:`Pyramid` defines two builtin principals used in every application:
:attr:`pyramid.security.Everyone` and :attr:`pyramid.security.Authenticated`.
On top of these we have already mentioned the required principals for this
application in the original design. The user has two possible roles:
``editor`` and ``basic``. These will be prefixed by the ``role:``
string to avoid clasing with any other types of principals.

Open the file ``tutorial/security.py`` and edit the following lines:

.. literalinclude:: src/authorization/tutorial/security.py
   :linenos:
   :emphasize-lines: 3-6,17-24
   :language: python

Only the highlighted lines need to be added.

Note that the role comes from the ``User`` object and finally we also
add the ``user.id`` as a principal for when we want to allow that exact
user to edit page's they've created.

Add the authorization policy
----------------------------

We already added the :term:`authorization policy` in the previous chapter
because :app:`Pyramid` requires one when adding an
:term:`authentication policy`. However, it was not used anywhere and so we'll
mention it now.

Open the file ``tutorial/security.py`` and notice the following lines:

.. literalinclude:: src/authorization/tutorial/security.py
   :lines: 38-40
   :lineno-match:
   :emphasize-lines: 2
   :language: python

We're using the :class:`pyramid.authorization.ACLAuthorizationPolicy` which
will suffice for most applications. It uses the :term:`context` to define
the mapping between a :term:`principal` and :term:`permission` for the
current request via the ``__acl__``.

Add resources and ACLs
----------------------

Resources are the hidden gem of :app:`Pyramid`. You've made it!

Every URL in a web application is representing a :term:`resource`
(the **R** in Uniform Resource Locator). Often the resource is something
in your data model but it could also be an abstraction over many models.

Our wiki has two resources:

#. A ``PageResource``. Represents a ``Page`` that is to be viewed or edited.
   Only ``editor`` users as well as the original creator of the ``Page``
   may edit the ``PageResource`` but anyone may view it.

#. A ``NewPage``. Represents a potential ``Page`` that does not exist.
   Any logged-in user (roles ``basic`` or ``editor``) can create pages.

.. note::

   The wiki data model is simple enough that the ``PageResource`` is
   actually mostly redundant with our ``models.Page`` SQLAlchemy class. It is
   completely valid to combine these into one class. However, for this
   tutorial they are explicitly separated to make it clear the
   parts that :app:`Pyramid` cares about versus application-defined objects.

There are many ways to define these resources, and they can even be grouped
into collections with a hierarchy. However, we're keeping it simple here!

Open the file ``tutorial/routes.py`` and edit the following lines:

.. literalinclude:: src/authorization/tutorial/routes.py
   :linenos:
   :emphasize-lines: 1-7,14-50
   :language: python

The highlighted lines need to be edited or added.

The ``NewPage`` has an ``__acl__`` on it that returns a list of
mappings from :term:`principal` to :term:`permission`. This defines **who**
can do **what** with that :term:`resource`. In our case we want to only
allow users with the principals ``role:editor`` and ``role:basic`` to
have the ``create`` permission:

.. literalinclude:: src/authorization/tutorial/routes.py
   :lines: 20-32
   :lineno-match:
   :emphasize-lines: 11,12
   :language: python

The ``NewPage`` is loaded as the :term:`context` of the ``add_page``
route by declaring a ``factory`` on the route:

.. literalinclude:: src/authorization/tutorial/routes.py
   :lines: 15-16
   :lineno-match:
   :emphasize-lines: 2
   :language: python

The ``PageResource`` defines the :term:`ACL` for a ``Page``. It uses an
actual ``Page`` object to determine **who** can do **what** to the page.

.. literalinclude:: src/authorization/tutorial/routes.py
   :lines: 34-50
   :lineno-match:
   :emphasize-lines: 14-16
   :language: python

The ``PageResource`` is loaded as the :term:`context` of the ``view_page``
and ``edit_page`` route by declaring a ``factory`` on the routes:

.. literalinclude:: src/authorization/tutorial/routes.py
   :lines: 14-18
   :lineno-match:
   :emphasize-lines: 1,4-5
   :language: python

Add view permissions
--------------------

At this point we've modified our application to load the ``PageResource``,
including the actual ``Page`` model in the ``page_factory``. The
``PageResource`` is now the :term:`context` for all ``view_page`` and
``edit_page`` views. Similarly the ``NewPage`` will be the context for
the ``add_page`` view.

Open the file ``views/default.py``.

First, you can drop a few imports that are no longer necessary:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 5-7
   :lineno-match:
   :emphasize-lines: 1
   :language: python

Edit the ``view_page`` view to declare the ``view`` permission and remove
the explicit checks within the view:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 18-23
   :lineno-match:
   :emphasize-lines: 2,4
   :language: python

The work of loading the page has already been done in the factory so we
can just pull the ``page`` object out of the ``PageResource`` loaded as
``request.context``. Our factory also guarantees we will have a ``Page`` as it
raises ``HTTPNotFound`` otherwise - again simplifying the view logic.

Edit the ``edit_page`` view to declare the ``edit`` permission:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 38-42
   :lineno-match:
   :emphasize-lines: 2,4
   :language: python

Edit the ``add_page`` view to declare the ``create`` permission:

.. literalinclude:: src/authorization/tutorial/views/default.py
   :lines: 52-56
   :lineno-match:
   :emphasize-lines: 2,4
   :language: python

Note the ``pagename`` here is pulled off of the context instead of
``request.matchdict``. The factory has done a lot of work for us to hide the
actual route pattern.

The ACLs defined on each :term:`resource` are used by the
:term:`authorization policy` to determine if any
:term:`principal` is allowed to have some :term:`permission`. If this check
fails (for example, the user is not logged in) then a ``HTTPForbidden``
exception will be raised automatically, thus we're able to drop those
exceptions and checks from the views themselves. Rather we've defined them in
terms of operations on a resource.

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
  ``FrontPage`` page object.

- http://localhost:6543/FrontPage/edit_page invokes the edit view for the
  FrontPage object.  It is executable by only the ``editor`` user.  If a
  different user (or the anonymous user) invokes it, a login form will be
  displayed.  Supplying the credentials with the username ``editor``, password
  ``editor`` will display the edit page form.

- http://localhost:6543/add_page/SomePageName invokes the add view for a page.
  It is executable by only the ``editor`` user.  If a different user (or the
  anonymous user) invokes it, a login form will be displayed. Supplying the
  credentials with the username ``editor``, password ``editor`` will display
  the edit page form.

- After logging in (as a result of hitting an edit or add page and submitting
  the login form with the ``editor`` credentials), we'll see a Logout link in
  the upper right hand corner.  When we click it, we're logged out, and
  redirected back to the front page.
