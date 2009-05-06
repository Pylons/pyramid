.. _security_chapter:

Security
========

:mod:`repoze.bfg` provides an optional declarative security system
that prevents views that are protected by a :term:`permission` from
being rendered when the user represented by the request does not have
the appropriate level of access in a context.

Security is enabled by adding configuration to your ``configure.zcml``
which specifies a :term:`security policy`.

Enabling a Security Policy
--------------------------

By default, :mod:`repoze.bfg` enables no security policy.  All views
are accessible by completely anonymous users.

However, if you add the following bit of code to your application's
``configure.zcml``, you will enable a security policy:

.. code-block:: xml
   :linenos:

   <utility
     provides="repoze.bfg.interfaces.ISecurityPolicy"
     factory="repoze.bfg.security.RemoteUserInheritingACLSecurityPolicy"
     />

The above inscrutable stanza enables the
``RemoteUserInheritingACLSecurityPolicy`` to be in effect for every
request to your application.  The
``RemoteUserInheritingACLSecurityPolicy`` is a policy which compares
the ``REMOTE_USER`` variable passed in the request's environment (as
the sole :term:`principal`) against the principals present in any
:term:`ACL` found in model data when attempting to call some
:term:`view`.  The policy either allows the view that the permission
was declared for to be called, or returns a ``401 Unathorized``
response code to the upstream WSGI server.

.. note:: Another "inheriting" security policy also exists:
   ``WhoInheritingACLSecurityPolicy``.  This policy uses principal
   information found in the ``repoze.who.identity`` value set into the
   WSGI environment by the :term:`repoze.who` middleware rather than
   ``REMOTE_USER`` information. This policy only works properly when
   :term:`repoze.who` middleware is present in the WSGI pipeline.

.. note:: "non-inheriting" security policy variants of the
   (``WhoACLSecurityPolicy`` and ``RemoteUserACLSecurityPolicy``) also
   exist.  These policies use the *first* ACL found as the canonical
   ACL; they do not continue searching up the context lineage to find
   "inherited" ACLs.  It is recommended that you use the inheriting
   variants unless you need this feature.

.. note:: See :ref:`security_policies_api_section` for more
   information about the features of the default security policies.

Protecting Views with Permissions
---------------------------------

You declaratively protected a particular view with a
:term:`permission` via the ``configure.zcml`` application registry.
For example, the following declaration protects the view named
``add_entry.html`` when invoked against an ``IBlog`` context with the
``add`` permission:

.. code-block:: xml
   :linenos:

   <view
       for=".models.IBlog"
       view=".views.blog_entry_add_view"
       name="add_entry.html"
       permission="add"
       />

If a security policy is in place when this view is found during normal
application operations, the user will need to possess the ``add``
permission against the context to be able to invoke the
``blog_entry_add_view`` view.

Permission names are just strings.  They hold no special significance
to the system.  You can name permissions whatever you like.

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

   class IBlog(Interface):
       pass

   class Blog(dict):
       __acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]
       implements(IBlog)

The above ACL indicates that the ``Everyone`` principal (a special
system-defined principal indicating, literally, everyone) is allowed
to view the blog, the ``group:editors`` principal is allowed to add to
and edit the blog.

.. note:: Each tuple within the above ``__acl__`` structure is known
          as a :term:`ACE`, which stands for "access control entry".

The third argument in an ACE can also be a sequence of permission
names instead of a single permission name.  So instead of the above,
where we assign a differnt ACE for two grants to the ``group.editors``
group, we can collapse this into a single ACE, as below.

.. code-block:: python

   __acl__ = [
       (Allow, Everyone, 'view'),
       (Allow, 'group:editors', ('add', 'edit')),
       ]

A principal is usually a user id, however it also may be a group id if
your authentication system provides group information and the security
policy is written to respect them.  The
``RemoteUserInheritingACLSecurityPolicy`` does not respect group
information.

ACL Inheritance
---------------

While any security policy is in place, if a model object does not have
an ACL when it is the context, its *parent* is consulted for an ACL.
If that object does not have an ACL, *its* parent is consulted for an
ACL, ad infinitum, until we've reached the root and there are no more
parents left.

With *non-inheriting* security policy variants
(e.g. ``WhoACLSecurityPolicy`` and ``RemoteUserACLSecurityPolicy``),
the *first* ACL found by the security policy will be used as the
effective ACL.  No combination of ACLs found during traversal or
backtracking is done.

With *inheriting* security policy variants
(e.g. ``WhoInheritingACLSecurityPolicy`` and
``RemoteUserInheritingACLSecurityPolicy``), *all* ACLs in the
context's :term:`lineage` are consulted when determining whether
access is allowed or denied.

:ref:`security_policies_api_section` for more information about the
features of the default security policies and the difference between
the inheriting and non-inheriting variants.

.. note:: It is recommended that you use the inheriting variant of a
   security policy.  Inheriting variants of security policies make it
   possible for you to form a security strategy based on context ACL
   "inheritance" rather than needing to keep all information about an
   object's security state in a single ACL attached to that object.
   It's much easier to code applications that dynamically change ACLs
   if ACL inheritance is used.  In reality, the non-inheriting
   security policy variants exist only for backwards compatibility
   with applications that used them in versions of :mod:`repoze.bfg`
   before 0.8.  If this backwards compatibility was not required, the
   non-inheriting variants probably just wouldn't exist.

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
