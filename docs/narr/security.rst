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
     factory="repoze.bfg.security.RemoteUserACLSecurityPolicy"
     />

The above insrcutable stanza enables the
``RemoteUserACLSecurityPolicy`` to be in effect for every request to
your application.  The ``RemoteUserACLSecurityPolicy`` is a policy
which compares the ``REMOTE_USER`` variable passed in the reqest's
environment (as the sole :term:`principal`) against any *ACL* found in
model data when attempting to call some :term:`view`.  The policy
either allows the view that the permission was declared for to be
called, or returns a ``401 Unathorized`` response code to the upstream
WSGI server.

Protecting Views with Permissions
---------------------------------

You declaratively protected a particular view with a
:term:`permission` via the ``configure.zcml`` application registry.
For example, the following declaration protects the view named
``add_entry.html`` when invoked against an ``IBlog`` context with the
``add`` permission:

.. code-block:: xml
   :linenos:

   <bfg:view
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
   from zope.location.interfaces import ILocation
   from zope.location.location import Location

   class IBlog(Interface):
       pass

   class Blog(dict, Location):
       __acl__ = [
           (Allow, Everyone, 'view'),
           (Allow, 'group:editors', 'add'),
           (Allow, 'group:editors', 'edit'),
           ]
       implements(IBlog, ILocation)

The above ACL indicates that the ``Everyone`` principal (a special
system-defined principal indicating, literally, everyone) is allowed
to view the blog, the ``group:editors`` principal is allowed to add to
and edit the blog.

A principal is usually a user id, however it also may be a group id if
your authentication system provides group information and the security
policy is written to respect them.  The
``RemoteUserACLSecurityPolicy`` does not respect group information.

ACL Inheritance
---------------

While the security policy is in place, if a model object does not have
an ACL when it is the context, its *parent* is consulted for an ACL.
If that object does not have an ACL, *its* parent is consulted for an
ACL, ad infinitum, until we've reached the root and there are no more
parents left.

The *first* ACL found by the security policy will be used as the
effective ACL.  No combination of ACLs found during traversal or
backtracking is done.

Location-Awareness
------------------

In order to allow the security machinery to perform ACL inheritance,
model objects should provide *location-awareness*.

Objects have parents when they define an ``__parent__`` attribute
which points at their parent object.  The root object's ``__parent__``
is ``None``.  An object with a ``__parent__`` attribute and a
``__name__`` attribute is said to be *location-aware*.

If the root object in a :mod:`repoze.bfg` application declares that it
implements the ``ILocation`` interface, it is assumed that the objects
in the rest of the model are location-aware.  Even if they are not
explictly, if the root object is marked as ``ILocation``, the bfg
framework will wrap each object during traversal in a *location
proxy*, which will wrap each object found during traversal in a proxy
object that has both the ``__name__`` and ``__parent__`` attributes,
but otherwise acts the same as your model object.

You can of course supply ``__name__`` and ``__parent__`` attributes
explicitly on all of your model objects, and no location proxying will
be performed.
