.. _glossary:

============================
Glossary
============================

.. glossary::

  Request
    A ``WebOb`` request object.
  Response
    An object that has three attributes: app_iter (representing an
    iterable body), headerlist (representing the http headers sent
    upstream), and status (representing the http status string).  This
    is the interface defined for ``WebOb`` response objects.
  Setuptools
    `Setuptools <http://peak.telecommunity.com/DevCenter/setuptools>`_
    builds on Python's ``distutils`` to provide easier building,
    distribution, and installation of packages.
  View
    A "view" is a callable which returns a response object.  It should
    accept two values: context and request.
  View name
    The "URL name" of a view, e.g "index.html".  If a view is
    configured without a name, its name is considered to be the empty
    string (which implies the "default view").
  Virtualenv
    An isolated Python environment.  Allows you to control which
    packages are used on a particular project by cloning your main
    Python.  `virtualenv <http://pypi.python.org/pypi/virtualenv>`_
    was created by Ian Bicking.
  Model
    An object representing data in the system.  A model is part of the
    object graph traversed by the system.  Models are traversed to
    determine a context.
  Context
    A model in the system that is found during traversal; it becomes
    the subject of a view.
  Application registry
    A registry which maps model types to views, as well as performing
    other application-specific component registrations.
  Template
    A file that is capable of representing some text when rendered.
  Interface
    An attribute of a model object that determines its type.
  Location
    The path to an object in a model graph.
  Security policy
    An object that provides a mechanism to check authorization using
    authentication data and a permission associated with a model.  It
    essentially returns "true" if the combination of the authorization
    information in the model (e.g. an ACL) and the authentication data
    in the request (e.g. the REMOTE_USER) allow the action implied by
    the permission associated with the view (e.g. "add").
  Principal
    A user id or group id.
  Permission
    A string or unicode object that represents an action being taken
    against a context.  A permission is associated with a view name
    and a model type by the developer.  Models are decorated with
    security declarations (e.g. ACLs), which reference these tokens
    also.  Permissions are used by the active to security policy to
    match the view permission against the model's statements about
    which permissions are granted to which principal in a context in
    order to to answer the question "is this user allowed to do this".
    Examples of permissions: "read", or "view_blog_entries".
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
  WSGI
    `Web Server Gateway Interface <http://wsgi.org/>`_.  This is a
    Python standard for connecting web applications to web servers,
    similar to the concept of Java Servlets.
  Zope
    `The Z Object Publishing Framework <http://zope.org>`_.  The granddaddy 
    of Python web frameworks.
  WebOb
    `WebOb <http://pythonpaste.org/webob/>`_ is a WSGI request/response
    library created by Ian Bicking.
  Paste
    `Paste <http://pythonpaste.org>`_ is a WSGI development and
    deployment system developed by Ian Bicking.
  LXML
    `lxml <http://codespeak.net/lxml/>`_ is a XML processing library
    for Python.

