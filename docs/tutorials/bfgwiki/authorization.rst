====================
Adding Authorization
====================

Our application currently allows anyone with access to the server to
view, edit, and add pages to our wiki.  For purposes of demonstration
we'll change our application to allow people whom possess a specific
username (`editor`) to add and edit wiki pages but we'll continue
allowing anyone with access to the server to view pages.
:mod:`repoze.bfg` provides facilities for *authorization* and
*authentication*.  We'll make use of both features to provide security
to our application.

The source code for this tutorial stage can be browsed at
`docs.repoze.org <http://docs.repoze.org/bfgwiki-1.2/authorization>`_.

Configuring a ``repoze.bfg`` Authentication Policy
--------------------------------------------------

For any :mod:`repoze.bfg` application to perform authorization, we
need to add a ``security.py`` module and we'll need to change our
:term:`application registry` to add an :term:`authentication policy`
and a :term:`authorization policy`.

Changing ``configure.zcml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll change our ``configure.zcml`` file to enable an
``AuthTktAuthenticationPolicy`` and an ``ACLAuthorizationPolicy`` to
enable declarative security checking.  We'll also add a ``forbidden``
stanza, which species a :term:`forbidden view`.  This configures our
login view to show up when :mod:`repoze.bfg` detects that a view
invocation can not be authorized.  When you're done, your
``configure.zcml`` will look like so:

.. literalinclude:: src/authorization/tutorial/configure.zcml
   :linenos:
   :language: xml


Adding ``security.py``
~~~~~~~~~~~~~~~~~~~~~~

Add a ``security.py`` module within your package (in the same
directory as ``run.py``, ``views.py``, etc) with the following
content:

.. literalinclude:: src/authorization/tutorial/security.py
   :linenos:
   :language: python

The ``groupfinder`` function defined here is an authorization policy
"callback"; it is a callable that accepts a userid and a request.  If
the userid exists in the set of users known by the system, the
callback will return a sequence of group identifiers (or an empty
sequence if the user isn't a member of any groups).  If the userid
*does not* exist in the system, the callback will return ``None``.
We'll use "dummy" data to represent user and groups sources.

Adding Login and Logout Views
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll add a ``login`` view which renders a login form and processes
the post from the login form, checking credentials.

We'll also add a ``logout`` view to our application and provide a link
to it.  This view will clear the credentials of the logged in user and
redirect back to the front page.

We'll add a different file (for presentation convenience) to add login
and logout views.  Add a file named ``login.py`` to your application
(in the same directory as ``views.py``) with the following content:

.. literalinclude:: src/authorization/tutorial/login.py
   :linenos:
   :language: python

Changing Existing Views
~~~~~~~~~~~~~~~~~~~~~~~

Then we need to change each of our ``view_page``, ``edit_page`` and
``add_page`` views in ``views.py`` to pass a "logged in" parameter
into its template.  We'll add something like this to each view body:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from repoze.bfg.security import authenticated_userid
   logged_in = authenticated_userid(request)

We'll then change the return value of each view that has an associated
``renderer`` to pass the `resulting `logged_in`` value to the
template.  For example:

.. ignore-next-block
.. code-block:: python
   :linenos:

   return dict(page = context,
               content = content,
               logged_in = logged_in,
               edit_url = edit_url)

Adding the ``login.pt`` Template
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a ``login.pt`` template to your templates directory.  It's
referred to within the login view we just added to ``login.py``.

.. literalinclude:: src/authorization/tutorial/templates/login.pt
   :linenos:
   :language: xml

Change ``view.pt`` and ``edit.pt``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We'll also need to change our ``edit.pt`` and ``view.pt`` templates to
display a "Logout" link if someone is logged in.  This link will
invoke the logout view.

To do so we'll add this to both templates within the ``<div
class="main_content">`` div:

.. code-block:: xml
   :linenos:

   <span tal:condition="logged_in">
      <a href="${request.application_url}/logout">Logout</a>
   </span>

Giving Our Root Model Object an ACL
-----------------------------------

We need to give our root model object an :term:`ACL`.  This ACL will
be sufficient to provide enough information to the :mod:`repoze.bfg`
security machinery to challenge a user who doesn't have appropriate
credentials when he attempts to invoke the ``add_page`` or
``edit_page`` views.

We need to perform some imports at module scope in our ``models.py``
file:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Allow
   from repoze.bfg.security import Everyone

Our root model is a ``Wiki`` object.  We'll add the following line at
class scope to our ``Wiki`` class:

.. code-block:: python
   :linenos:

   __acl__ = [ (Allow, Everyone, 'view'), (Allow, 'editor', 'edit') ]

It's only happenstance that we're assigning this ACL at class scope.
An ACL can be attached to an object *instance* too; this is how "row
level security" can be achieved in :mod:`repoze.bfg` applications.  We
actually only need *one* ACL for the entire system, however, because
our security requirements are simple, so this feature is not
demonstrated.

Our resulting ``models.py`` file will now look like so:

.. literalinclude:: src/authorization/tutorial/models.py
   :linenos:
   :language: python

Adding ``permission`` Declarations to our ``bfg_view`` Decorators
-----------------------------------------------------------------

To protect each of our views with a particular permission, we need to
pass a ``permission`` argument to each of our
:class:`repoze.bfg.view.bfg_view` decorators.  To do so, within
``views.py``:

- We add ``permission='view'`` to the decorator attached to the
  ``view_wiki`` view function. This makes the assertion that only
  users who possess the effective ``view`` permission at the time of
  the request may invoke this view.  We've granted
  :data:`repoze.bfg.security.Everyone` the view permission at the root
  model via its ACL, so everyone will be able to invoke the
  ``view_wiki`` view.

- We add ``permission='view'`` to the decorator attached to the
  ``view_page`` view function.  This makes the assertion that only
  users who possess the effective ``view`` permission at the time of
  the request may invoke this view.  We've granted
  :data:`repoze.bfg.security.Everyone` the view permission at the root
  model via its ACL, so everyone will be able to invoke the
  ``view_page`` view.

- We add ``permission='edit'`` to the decorator attached to the
  ``add_page`` view function.  This makes the assertion that only
  users who possess the effective ``view`` permission at the time of
  the request may invoke this view.  We've granted the``editor``
  principal the view permission at the root model via its ACL, so only
  the user named ``editor`` will able to invoke the ``add_page`` view.

- We add ``permission='edit'`` to the ``bfg_view`` decorator attached
  to the ``edit_page`` view function.  This makes the assertion that
  only users who possess the effective ``view`` permission at the time
  of the request may invoke this view.  We've granted ``editor`` the
  view permission at the root model via its ACL, so only the user
  named ``editor`` will able to invoke the ``edit_page`` view.

Viewing the Application in a Browser
------------------------------------

We can finally examine our application in a browser.  The views we'll
try are as follows:

- Visiting ``http://localhost:6543/`` in a browser invokes the
  ``view_wiki`` view.  This always redirects to the ``view_page`` view
  of the FrontPage page object.  It is executable by any user.

- Visiting ``http://localhost:6543/FrontPage/`` in a browser invokes
  the ``view_page`` view of the front page page object.  This is
  because it's the :term:`default view` (a view without a ``name``)
  for ``Page`` objects.  It is executable by any user.

- Visiting ``http://localhost:6543/FrontPage/edit_page`` in a browser
  invokes the edit view for the front page object.  It is executable
  by only the ``editor`` user.  If a different user (or the anonymous
  user) invokes it, a login form will be displayed.  Supplying the
  credentials with the username ``editor``, password ``editor`` will
  show the edit page form being displayed.

- Visiting ``http://localhost:6543/add_page/SomePageName`` in a
  browser invokes the add view for a page.  It is executable by only
  the ``editor`` user.  If a different user (or the anonymous user)
  invokes it, a login form will be displayed.  Supplying the
  credentials with the username ``editor``, password ``editor`` will
  show the edit page form being displayed.

Seeing Our Changes To ``views.py`` and our Templates
----------------------------------------------------

Our ``views.py`` module will look something like this when we're done:

.. literalinclude:: src/authorization/tutorial/views.py
   :linenos:
   :language: python

Our ``edit.pt`` template will look something like this when we're done:

.. literalinclude:: src/authorization/tutorial/templates/edit.pt
   :linenos:
   :language: xml

Our ``view.pt`` template will look something like this when we're done:

.. literalinclude:: src/authorization/tutorial/templates/view.pt
   :linenos:
   :language: xml

Revisiting the Application
---------------------------

When we revisit the application in a browser, and log in (as a result
of hitting an edit or add page and submitting the login form with the
``editor`` credentials), we'll see a Logout link in the upper right
hand corner.  When we click it, we're logged out, and redirected back
to the front page.



