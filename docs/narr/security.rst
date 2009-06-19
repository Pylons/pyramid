.. _security_chapter:

Security
========

:mod:`repoze.bfg` provides an optional declarative authorization
system that prevents views that are protected by a :term:`permission`
from being invoked when the user represented by credentials in the
:term:`request` does not have an appropriate level of access in a
specific context.

Authorization is enabled by modifying your application's invocation of
``repoze.bfg.router.make_app``, often located in the ``run.py`` module
of a :mod:`repoze.bfg` application.

Enabling an Authorization Policy
--------------------------------

By default, :mod:`repoze.bfg` enables no authorization policy.  All
views are accessible by completely anonymous users.

However, if you change the call to ``repoze.bfg.router.make_app``
(usually found within the ``run.py`` module in your application), you
will enable an authorization policy.

You must enable a a :term:`authentication policy` in order to enable
an authorization policy.

For example, to enable a policy which compares the ``REMOTE_USER``
variable passed in the request's environment (as the sole
:term:`principal`) against the principals present in any :term:`ACL`
found in model data when attempting to call some :term:`view`, modify
your ``run.py`` to look something like this:

.. code-block:: python
   :linenos:

   from repoze.bfg.router import make_app
   from repoze.bfg.authentication import RemoteUserAuthenticationPolicy

   def app(global_config, **kw):
       """ This function returns a repoze.bfg.router.Router object.  It
       is usually called by the PasteDeploy framework during ``paster
       serve``"""
       # paster app config callback
       from myproject.models import get_root
       import myproject
       policy = RemoteUserAuthenticationPolicy()
       return make_app(get_root, myproject, authentication_policy=policy,
                       options=kw)

This injects an instance of the
``repoze.bfg.authentication.RemoteUserAuthenticationPolicy`` as the
:term:`authentication policy`.  It is possible to use a different
authentication policy.  :mod:`repoze.bfg` ships with a few prechewed
authentication policies that should prove useful (see
:ref:`authentication_policies_api_section`).  It is also possible to
construct your own authentication policy.  Any instance which
implements the interface defined in
``repoze.bfg.interfaces.IAuthenticationPolicy`` can be used.

It's not common, but it is also possible to change the default
:term:`authorization policy` (to use some other persistent
authorization mechanism other than ACLs).  To do so, pass an object
which implements the ``repoze.bfg.interfaces.IAuthorizationPolicy``)
to ``make_app`` as the ``authorization_policy`` value.
:mod:`repoze.who` ships with only one.  See
:ref:`authorization_policies_api_section` for the details of the ACL
authorization policy which is the default

Protecting Views with Permissions
---------------------------------

You declaratively protected a particular view with a
:term:`permission` via the ``configure.zcml`` application registry.
For example, the following declaration protects the view named
``add_entry.html`` when invoked against a ``Blog`` context with the
``add`` permission:

.. code-block:: xml
   :linenos:

   <view
       for=".models.Blog"
       view=".views.blog_entry_add_view"
       name="add_entry.html"
       permission="add"
       />

The equivalent view registration including the 'add' permission may be
performed via the ``bfg_view`` decorator within the "views" module of
your project's package

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view
   from models import Blog

   @bfg_view(for_=Blog, name='add_entry.html', permission='add')
   def blog_entry_add_view(context, request):
       """ Add blog entry code goes here """
       pass

If an authorization policy is in place when this view is found during
normal application operations, the user will need to possess the
``add`` permission against the context to be able to invoke the
``blog_entry_add_view`` view.

Permission names are just strings.  They hold no special significance
to the system.  You can name permissions whatever you like.

.. _assigning_acls:

Assigning ACLs to your Model Objects
------------------------------------

When :mod:`repoze.bfg` determines whether a user possesses a particular
permission in a :term:`context`, it examines the :term:`ACL`
associated with the context.  An ACL is associated with a context by
virtue of the ``__acl__`` attribute of the model object representing
the context.  This attribute can be defined on the model *instance*
(if you need instance-level security), or it can be defined on the
model *class* (if you just need type-level security).

For example, an ACL might be attached to model for a blog via its
class:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow

   class Blog(object):
       __acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]

Or, if your models are persistent, an ACL might be specified via the
``__acl__`` attribute of an *instance* of a model:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow

   class Blog(object):
       pass

   blog = Blog()

   blog.__acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]

Whether an ACL is attached to a model's class or an instance of the
model itself, the effect is the same.  It is useful to decorate
individual model instances with an ACL (as opposed to just decorating
their class) in applications such as "CMS" systems where fine-grained
access is required on an object-by-object basis.

Elements of an ACL
------------------

Here's an example ACL:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow

   __acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]

The example ACL indicates that the ``Everyone`` principal (a special
system-defined principal indicating, literally, everyone) is allowed
to view the blog, the ``group:editors`` principal is allowed to add to
and edit the blog.

The third argument in an ACE can also be a sequence of permission
names instead of a single permission name.  So instead of creating
multiple ACEs representing a number of different permission grants to
a single ``group.editors`` group, we can collapse this into a single
ACE, as below.

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow

   __acl__ = [
       (Allow, Everyone, 'view'),
       (Allow, 'group:editors', ('add', 'edit')),
       ]

A principal is usually a user id, however it also may be a group id if
your authentication system provides group information and the
effective :term:`authentication policy` policy is written to respect
group information.  The ``RepozeWho1AuthenicationPolicy``
authentication policy that comes with :mod:`repoze.bfg` respects group
information (see the :mod:`repoze.bfg.authentication` API docs for
more info on authentication policies).

Each tuple within an ACL structure is known as a :term:`ACE`, which
stands for "access control entry".  For example, in the above ACL,
``(Allow, Everyone, 'view')`` is an ACE.  Each ACE in an ACL is
processed by an authorization policy *in the order dictated by the
ACL*.  So if you have an ACL like this:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow
   from repoze.bfg.security import Deny

   __acl__ = [
       (Allow, Everyone, 'view'),
       (Deny, Everyone, 'view'),
       ]

The authorization policy will *allow* everyone the view permission,
even though later in the ACL you have an ACE that denies everyone the
view permission.  On the other hand, if you have an ACL like this:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Everyone
   from repoze.bfg.security import Allow
   from repoze.bfg.security import Deny

   __acl__ = [
       (Deny, Everyone, 'view'),
       (Allow, Everyone, 'view'),
       ]

The authorization policy will deny Everyone the view permission, even
though later in the ACL is an ACE that allows everyone.

Special Principal Names
-----------------------

Special principal names exist in the :mod:`repoze.bfg.security`
module.  They can be imported for use in your own code to populate
ACLs, e.g. ``from repoze.bfg.security import Everyone``.

``Everyone``

  Literally, everyone, no matter what.  This object is actually a
  string "under the hood" (``system.Everyone``).  Every user "is" the
  principal named Everyone during every request, even if a security
  policy is not in use.

``Authenticated``

  Any user with credentials as determined by the current security
  policy.  You might think of it as any user that is "logged in".
  This object is actually a string "under the hood"
  (``system.Authenticated``).

Special Permissions
-------------------

Special permission names exist in the :mod:`repoze.bfg.security`
module.  These can be imported for use in ACLs.

.. _all_permissions:

``ALL_PERMISSIONS``

  An object representing, literally, *all* permissions.  Useful in an
  ACL like so: ``(Allow, 'fred', ALL_PERMISSIONS)``.  The
  ``ALL_PERMISSIONS`` object is actually a standin object that has a
  ``__contains__`` method that always returns True, which, for all
  known authorization policies, has the effect of indicating that a
  given principal "has" any permission asked for by the system.

Special ACEs
------------

A convenience :term:`ACE` is defined within the
:mod:`repoze.bfg.security` module named ``DENY_ALL``.  It equals the
following:

.. code-block:: python

   (Deny, Everyone, ALL_PERMISSIONS)

This ACE is often used as the *last* ACE of an ACL to explicitly cause
inheriting authorization policies to "stop looking up the traversal
tree" (effectively breaking any inheritance).  For example, an ACL
which allows *only* ``fred`` the view permission in a particular
traversal context despite what inherited ACLs may say when the default
authorization policy is in effect might look like so:

.. code-block:: python
   :linenos:

   from repoze.bfg.security import Allow
   from repoze.bfg.security import DENY_ALL

   __acl__ = [ (Allow, 'fred', 'view'),
               DENY_ALL ]

ACL Inheritance
---------------

While the default :term:`authorization policy` is in place, if a model
object does not have an ACL when it is the context, its *parent* is
consulted for an ACL.  If that object does not have an ACL, *its*
parent is consulted for an ACL, ad infinitum, until we've reached the
root and there are no more parents left.

Location-Awareness
------------------

In order to allow the security machinery to perform ACL inheritance,
model objects must provide *location-awareness*.  Providing
location-awareness means two things: the root object in the graph must
have a ``_name__`` attribute and a ``__parent__`` attribute.

.. code-block:: python
   :linenos:

   class Blog(object):
       __name__ = ''
       __parent__ = None

An object with a ``__parent__`` attribute and a ``__name__`` attribute
is said to be *location-aware*.  Location-aware objects define an
``__parent__`` attribute which points at their parent object.  The
root object's ``__parent__`` is ``None``.

See :ref:`location_module` for documentations of functions which use
location-awareness.  See also :ref:`location_aware`.

.. _debug_authorization_section:

Debugging View Authorization Failures
-------------------------------------

If your application in your judgment is allowing or denying view
access inappropriately, start your application under a shell using the
``BFG_DEBUG_AUTHORIZATION`` environment variable set to ``1``.  For
example::

  $ BFG_DEBUG_AUTHORIZATION=1 bin/paster serve myproject.ini

When any authorization takes place during a top-level view rendering,
a message will be logged to the console (to stderr) about what ACE in
which ACL permitted or denied the authorization based on
authentication information.

This behavior can also be turned on in the application ``.ini`` file
by setting the ``debug_authorization`` key to ``true`` within the
application's configuration section, e.g.::

  [app:main]
  use = egg:MyProject#app
  debug_authorization = true

With this debug flag turned on, the response sent to the browser will
also contain security debugging information in its body.

Debugging Imperative Authorization Failures
-------------------------------------------

The ``has_permission`` API (see :ref:`security_module`) is used to
check security within view functions imperatively.  It returns
instances of objects that are effectively booleans.  But these objects
are not raw ``True`` or ``False`` objects, and have information
attached to them about why the permission was allowed or denied.  The
object will be one of ``ACLAllowed``, ``ACLDenied``, ``Allowed``, and
``Denied``, documented in :ref:`security_module`.  At very minimum
these objects will have a ``msg`` attribute, which is a string
indicating why permission was denied or allowed.  Introspecting this
information in the debugger or via print statements when a
``has_permission`` fails is often useful.

Creating Your Own Authentication Policy
---------------------------------------

:mod:`repoze.bfg` ships with a number of useful out-of-the-box
security policies (see :ref:`authentication_policies_api_section`).
However, creating your own authentication policy is often necessary
when you want to control the "horizontal and vertical" of how your
users authenticate.  Doing so is matter of creating an instance of
something that implements the following interface:

.. code-block:: python

   class AuthenticationPolicy(object):
       """ An object representing a BFG authentication policy. """
       def authenticated_userid(self, request):
           """ Return the authenticated userid or ``None`` if no
           authenticated userid can be found. """

       def effective_principals(self, request):
           """ Return a sequence representing the effective principals
           including the userid and any groups belonged to by the current
           user, including 'system' groups such as Everyone and
           Authenticated. """

       def remember(self, request, principal, **kw):
           """ Return a set of headers suitable for 'remembering' the
           principal named ``principal`` when set in a response.  An
           individual authentication policy and its consumers can decide
           on the composition and meaning of **kw. """
       
       def forget(self, request):
           """ Return a set of headers suitable for 'forgetting' the
           current user on subsequent requests. """

Pass the object you create into the ``repoze.bfg.router.make_app``
function as the ``authentication_policy`` argument at application
startup time (usually within a ``run.py`` module).

Creating Your Own Authorization Policy
--------------------------------------

An authentiction policy the policy that allows or denies access after
a user is authenticated.  By default, :mod:`repoze.bfg` will use the
``repoze.bfg.authorization.ACLAuthorizationPolicy`` if an
authentication policy is activated.  Creating and using your own
authorization policy is a matter of creating an instance of an object
that implements the following interface:

.. code-block:: python

    class IAuthorizationPolicy(object):
        """ A adapter on context """
        def permits(self, context, principals, permission):
            """ Return True if any of the principals is allowed the
            permission in the current context, else return False """
            
        def principals_allowed_by_permission(self, context, permission):
            """ Return a set of principal identifiers allowed by the 
                permission """

Pass the object you create into the ``repoze.bfg.router.make_app``
function as the ``authorization_policy`` argument at application
startup time (usually within a ``run.py`` module).  You must also pass
an ``authentication_policy`` if you pass an ``authorization_policy``.
