Security
========

``repoze.bfg`` provides an optional declarative security system that
prevents views that are protected by a "permission" from being
rendered when the user represented by the request does not have the
appropriate level of access in a context.

Jargon
------

Permission

  A string or unicode object that represents an action being taken
  against a context.  For example, ``read``, or ``view_blog_entries``.

ACE

  An *access control entry*.  An access control entry is one element
  in an *ACL*.  An access control entry is a three-tuple that
  describes three things: an *action* (one of either ``Allow`` or
  ``Deny``), a *principal* (a string describing a user or group), and
  a *permission*.  For example the ACE, ``(Allow, 'bob', 'read')`` is
  a member of an ACL that indicates that the principal ``bob`` is
  allowed the permission ``read`` against the context the ACL is
  attached to.

ACL

  An *access control list*.  An ACL is a sequence of *ACE* s.  An ACL
  is attached to a model instance.  An example of an ACL is ``[
  (Allow, 'bob', 'read'), (Deny, 'fred', 'write')]``.  If an ACL is
  attached to a model instance, and that model instance is findable
  via the context, it will be consulted by the security policy to
  determine wither a particular request can be fulfilled given the
  *authentication* information in the request.

Authentication

  The act of determining that the credentials a user presents during a
  particular request are "good".  ``repoze.bfg`` does not perfom
  authentication: it leaves it up to an upstream component such as
  ``repoze.who``.  ``repoze.bfg`` uses the authentication data
  supplied by the upstream component as one input during
  authorization.

Authorization

  The act of determining whether a user can perform a specific action.
  In bfg terms, this means determining whether, for a given context,
  the *principals* associated with the request have the requisite
  *permission* to allow the request to continue.

Principal

  A *principal* is a string or unicode object representing a user or a
  user's membership in a group.  It is provided by the
  *authentication* machinery upstream, typically.  For example, if a
  user had the user id "bob", and Bob was part of two groups named
  "group foo" and "group bar", the request might have information
  attached to it that would indictate that Bob was represented by
  three principals: "bob", "group foo" and "group bar".

Security Policy

  A security policy in bfg terms is a bit of code which accepts a
  request, the *ACL* associated with a context, and the *permission*
  associated with a particular view, and determines whether or not the
  principals associated with the request can perform the action
  associated with the permission based on the ACL.

Enabling a Security Policy
--------------------------

By default, ``repoze.bfg`` enables no security policy.  All views are
accessible by completely anonymous users.

However, if you add the following bit of code to your application's
``configure.zcml``, you will enable a security policy::

  <utility
    provides="repoze.bfg.interfaces.ISecurityPolicy"
    factory="repoze.bfg.security.RemoteUserACLSecurityPolicy"
    />

The above insrcutable stanza enables the
``RemoteUserACLSecurityPolicy`` to be in effect for every request to
your application.  The ``RemoteUserACLSecurityPolicy`` is a policy
which compares the ``REMOTE_USER`` variable passed in the reqest's
environment (as the sole *principal*) against any *ACL* found in model
data when attempting to call some *view*.  The policy either allows
the view that the permission was declared for to be called, or returns
a ``401 Unathorized`` response code to the upstream WSGI server.

Protecting Views with Permissions
---------------------------------

You declaratively protected a particular view with a permisson via the
``configure.zcml`` application registry.  For example, the following
declaration protects the view named "add_entry.html" when invoked
against an IBlog context with the ``add`` permission::

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

When ``repoze.bfg`` determines whether a user possesses a particular
permission in a context, it examines the ACL associated with the
context.  An ACL is associated with a context by virtue of the
``__acl__`` attribute of the model object representing the context.
This attribute can be defined on the model *instance* (if you need
instance-level security), or it can be defined on the model *class*
(if you just need type-level security).

For example, an ACL might be attached to model for a blog via its
class::

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

The above ACL indicates that the Everyone principal (a system-defined
principal) is allowed to view the blog, the ``group:editors``
principal is allowed to add to and edit the blog.

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

If the root object in a ``repoze.bfg`` application declares that it
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
