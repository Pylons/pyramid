.. _wiki2_adding_authorization:

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

Adding A Root Factory
---------------------

We're going to start to use a custom *root factory* within our
``run.py`` file in order to be able to attach security declarations to
our :term:`context` object.  When we do this, we can begin to make use
of the declarative security features of :mod:`repoze.bfg`.

Let's modify our ``run.py``, passing in a :term:`root factory` as the
first argument to ``repoze.bfg.router.make_app``.  We'll point it at a
new class we create inside our ``models.py`` file.  Add the following
statements to your ``models.py`` file:

.. code-block:: python

   from repoze.bfg.security import Allow
   from repoze.bfg.security import Everyone

   class RootFactory(object):
    __acl__ = [ (Allow, Everyone, 'view'), (Allow, 'editor', 'edit') ]
    def __init__(self, environ):
        self.__dict__.update(environ['bfg.routes.matchdict'])

Defining a root factory allows us to use declarative security features
of :mod:`repoze.bfg`.  The ``RootFactory`` class we added will be used
to construct each of the ``context`` objects passed to our views.  All
of our ``context`` objects will possess an ``__acl__`` attribute that
allows "Everyone" (a special principal) to view all request, while
allowing only a user named ``editor`` to edit and add pages.  The
``__acl__`` attribute attached to a context is interpreted specially
by :mod:`repoze.bfg` as an access control list during view execution.
See :ref:`assigning_acls` for more information about what an
:term:`ACL` represents.

.. note: Although we don't use the functionality here, the ``factory``
   used to create route contexts may differ per-route instead of
   globally via a ZCML directive.  See the ``factory`` attribute in
   :ref:`route_zcml_directive` for more info.

Configuring a ``repoze.bfg`` Authentication Policy
--------------------------------------------------

For any :mod:`repoze.bfg` application to perform authorization, we
need to change our ``run.py`` module to add an :term:`authentication
policy`.  Adding an authentication policy actually causes the system
to begin to use :term:`authorization`.

Changing ``run.py``
~~~~~~~~~~~~~~~~~~~

Change your ``run.py`` module to import the
``AuthTktAuthenticationPolicy`` from ``repoze.bfg.authentication``.
Within the body of the ``make_app`` function, construct an instance of
the policy, and pass it as the ``authentication_policy`` argument to
the ``make_app`` function.  The first positional argument of an
``AuthTktAuthenticationPolicy`` is a secret used to encrypt cookie
data.  Its second argument ("callback") should be a callable that
accepts a userid.  If the userid exists in the system, the callback
should return a sequence of group identifiers (or an empty sequence if
the user isn't a member of any groups).  If the userid *does not*
exist in the system, the callback should return ``None``.  We'll use
"dummy" data to represent user and groups sources.

We'll also use the opportunity to pass our ``RootFactory`` in as the
first argument to ``make_app``.  When we're done, your application's
``run.py`` will look like this.

.. literalinclude:: src/authorization/tutorial/run.py
   :linenos:
   :language: python

BFG's ``make_app`` callable also can accept an authorization policy
parameter.  We don't need to specify one, we'll use the default.

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

.. code-block:: python
   :linenos:

   logged_in = authenticated_userid(request)

We'll then change the return value of ``render_template_to_response``
to pass the `resulting `logged_in`` value to the template, e.g.:

.. code-block:: python
   :linenos:

   return render_template_to_response('templates/view.pt',
                                      request = request,
                                      page = context,
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

   <span tal:condition="logged_in"><a href="${request.application_url}/logout">Logout</a></span>

Changing ``configure.zcml``
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change your application's ``configure.zcml`` to add a slightly
inscrutable ``utility`` stanza which "provides" ``IForbiddenView``.
This configures our login view to show up when BFG detects that a view
invocation can not be authorized.  Also, add ``permission`` attributes
with the value ``edit`` to the ``edit_page`` and ``add_page`` routes.
This indicates that the views which these routes reference cannot be
invoked without the authenticated user possessing the ``edit``
permission.  When you're done, your ``configure.zcml`` will look like
so:

.. literalinclude:: src/authorization/tutorial/configure.zcml
   :linenos:
   :language: xml

Viewing the Application in a Browser
------------------------------------

Once we've set up the WSGI pipeline properly, we can finally examine
our application in a browser.  The views we'll try are as follows:

- Visiting `http://localhost:6543/ <http://localhost:6543/>`_ in a
  browser invokes the ``view_wiki`` view.  This always redirects to
  the ``view_page`` view of the FrontPage page object.  It is
  executable by any user.

- Visiting `http://localhost:6543/FrontPage/
  <http://localhost:6543/FrontPage/>`_ in a browser invokes the
  ``view_page`` view of the FrontPage page object.

- Visiting `http://localhost:6543/FrontPage/edit_page
  <http://localhost:6543/FrontPage/edit_page>`_ in a browser invokes
  the edit view for the FrontPage object.  It is executable by only
  the ``editor`` user.  If a different user (or the anonymous user)
  invokes it, a login form will be displayed.  Supplying the
  credentials with the username ``editor``, password ``editor`` will
  display the edit page form.

- Visiting `http://localhost:6543/add_page/SomePageName
  <http://localhost:6543/add_page/SomePageName>`_ in a browser invokes
  the add view for a page.  It is executable by only the ``editor``
  user.  If a different user (or the anonymous user) invokes it, a
  login form will be displayed.  Supplying the credentials with the
  username ``editor``, password ``editor`` will display the edit page
  form.

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



