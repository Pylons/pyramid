Models
======

A :term:`model` class is typically a simple Python class defined in a
module.  References to these classes and instances of such classes are
omnipresent in :mod:`repoze.bfg`:

- Model instances make up the graph that :mod:`repoze.bfg` is
  willing to walk over when :term:`traversal` is used.

- The ``context`` and ``containment`` arguments to
  :meth:`repoze.bfg.configuration.Configurator.add_view` often
  reference a model class.

- A :term:`root factory` returns a model instance.

- A model instance is generated as a result of :term:`url dispatch`
  (see the ``factory`` argument to
  :meth:`repoze.bfg.configuration.Configurator.add_route`).

- A model instance is exposed to :term:`view` code as the
  :term:`context` of a view.

Model objects typically store data and offer methods related to
mutating that data.

.. note::

   A terminology overlap confuses people who write applications that
   always use ORM packages such as SQLAlchemy, which has a very
   different notion of the definition of a "model".  When using the API
   of common ORM packages, its conception of "model" is almost
   certainly not the same conception of "model" used by
   :mod:`repoze.bfg`.  In particular, it can be unnatural to think of
   :mod:`repoze.bfg` model objects as "models" if you develop your
   application using :term:`traversal` and a relational database.  When
   you develop such applications, the object graph *might* be composed
   completely of "model" objects (as defined by the ORM) but it also
   might not be.  The things that :mod:`repoze.bfg` refers to as
   "models" in such an application may instead just be stand-ins that
   perform a query and generate some wrapper *for* an ORM "model" or
   set of ORM models.  This naming overlap is slightly unfortunate.
   However, many :mod:`repoze.bfg` applications (especially ones which
   use :term:`ZODB`) do indeed traverse a graph full of literal model
   nodes.  Each node in the graph is a separate persistent object that
   is stored within a database.  This was the use case considered when
   coming up with the "model" terminology.  However, if we had it to do
   all over again, we'd probably call these objects something
   different to avoid confusion.

.. index::
   single: model constructor

Defining a Model Constructor
----------------------------

An example of a model constructor, ``BlogEntry`` is presented below.
It is implemented as a class which, when instantiated, becomes a model
instance.

.. code-block:: python
   :linenos:

   import datetime

   class BlogEntry(object):
       def __init__(self, title, body, author):
           self.title = title
           self.body =  body
           self.author = author
           self.created = datetime.datetime.now()

A model constructor may be essentially any Python object which is
callable, and which returns a model instance.  In the above example,
the ``BlogEntry`` class can be "called", returning a model instance.

.. index::
   single: model interfaces

.. _models_which_implement_interfaces:

Model Instances Which Implement Interfaces
------------------------------------------

Model instances can optionally be made to implement an
:term:`interface`.  An interface is used to tag a model object with a
"type" that can later be referred to within :term:`view
configuration`.

Specifying an interface instead of a class as the ``context`` or
``containment`` arguments within :term:`view configuration` statements
effectively makes it possible to use a single view callable for more
than one class of object.  If your application is simple enough that
you see no reason to want to do this, you can skip reading this
section of the chapter.

For example, here's some code which describes a blog entry which also
declares that the blog entry implements an :term:`interface`.

.. code-block:: python
   :linenos:

   import datetime
   from zope.interface import implements
   from zope.interface import Interface

   class IBlogEntry(Interface):
       pass

   class BlogEntry(object):
       implements(IBlogEntry)
       def __init__(self, title, body, author):
           self.title = title
           self.body =  body
           self.author = author
           self.created = datetime.datetime.now()

This model consists of two things: the class which defines the model
constructor (above as the class ``BlogEntry``), and an
:term:`interface` attached to the class (via an ``implements``
statement at class scope using the ``IBlogEntry`` interface as its
sole argument).

The interface object used must be an instance of a class that inherits
from :class:`zope.interface.Interface`.

A model class may *implement* zero or more interfaces.  You specify
that a model implements an interface by using the
:func:`zope.interface.implements` function at class scope.  The above
``BlogEntry`` model implements the ``IBlogEntry`` interface.

You can also specify that a *particular* model instance provides an
interface (as opposed to its class).  To do so, use the
:func:`zope.interface.directlyProvides` function:

.. code-block:: python
   :linenos:

   from zope.interface import directlyProvides
   from zope.interface import Interface

   class IBlogEntry(Interface):
       pass

   class BlogEntry(object):
       def __init__(self, title, body, author):
           self.title = title
           self.body =  body
           self.author = author
           self.created = datetime.datetime.now()

   entry = BlogEntry('title', 'body', 'author')
   directlyProvides(entry, IBlogEntry)

:func:`zope.interface.directlyProvides` will replace any existing
interface that was previously provided by an instance.  If a model
object already has instance-level interface declarations that you
don't want to replace, use the :func:`zope.interface.alsoProvides`
function:

.. code-block:: python
   :linenos:

   from zope.interface import alsoProvides
   from zope.interface import directlyProvides
   from zope.interface import Interface

   class IBlogEntry1(Interface):
       pass

   class IBlogEntry2(Interface):
       pass

   class BlogEntry(object):
       def __init__(self, title, body, author):
           self.title = title
           self.body =  body
           self.author = author
           self.created = datetime.datetime.now()

   entry = BlogEntry('title', 'body', 'author')
   directlyProvides(entry, IBlogEntry1)
   alsoProvides(entry, IBlogEntry2)

:func:`zope.interface.alsoProvides` will augment the set of interfaces
directly provided by an instance instead of overwriting them like
:func:`zope.interface.directlyProvides` does.

For more information about how model interfaces can be used by view
configuration, see :ref:`using_model_interfaces`.

.. index::
   single: model graph
   single: traversal graph
   single: object graph
   single: container nodes
   single: leaf nodes

Defining a Graph of Model Instances for Traversal
-------------------------------------------------

When :term:`traversal` is used (as opposed to a purely :term:`url
dispatch` based application), :mod:`repoze.bfg` expects to be able to
traverse a graph composed of model instances.  Traversal begins at a
root model, and descends into the graph recursively via each found
model's ``__getitem__`` method.  :mod:`repoze.bfg` imposes the
following policy on model instance nodes in the graph:

- Nodes which contain other nodes (aka "container" nodes) must supply
  a ``__getitem__`` method which is willing to resolve a unicode name
  to a subobject.  If a subobject by that name does not exist in the
  container, ``__getitem__`` must raise a :exc:`KeyError`.  If a
  subobject by that name *does* exist, the container should return the
  subobject (another model instance).

- Nodes which do not contain other nodes (aka "leaf" nodes) must not
  implement a ``__getitem__``, or if they do, their ``__getitem__``
  method must raise a :exc:`KeyError`.

See :ref:`traversal_chapter` for more information about how traversal
works against model instances.

.. index::
   pair: location-aware; model

.. _location_aware:

Location-Aware Model Instances
------------------------------

.. sidebar::  Using :mod:`repoze.bfg.traversalwrapper`

  If you'd rather not manage the ``__name__`` and ``__parent__``
  attributes of your models "by hand", an add on package named
  :mod:`repoze.bfg.traversalwrapper` can help.

  In order to use this helper feature, you must first install the
  :mod:`repoze.bfg.traversalwrapper` package (available via `SVN
  <http://svn.repoze.org/repoze.bfg.traversalwrapper>`_), then
  register its ``ModelGraphTraverser`` as the traversal policy, rather
  than the default :mod:`repoze.bfg` traverser. The package contains
  instructions.

  Once :mod:`repoze.bfg` is configured with this feature, you will no
  longer need to manage the ``__parent__`` and ``__name__`` attributes
  on graph objects "by hand".  Instead, as necessary, during traversal
  :mod:`repoze.bfg` will wrap each object (even the root object) in a
  ``LocationProxy`` which will dynamically assign a ``__name__`` and a
  ``__parent__`` to the traversed object (based on the last traversed
  object and the name supplied to ``__getitem__``).  The root object
  will have a ``__name__`` attribute of ``None`` and a ``__parent__``
  attribute of ``None``.

Applications which use :term:`traversal` to locate the :term:`context`
of a view must ensure that the model instances that make up the model
graph are "location aware".

In order for :mod:`repoze.bfg` location, security, URL-generation, and
traversal functions (such as the functions exposed in
:ref:`location_module`, :ref:`traversal_module`, and :ref:`url_module`
as well as certain functions in :ref:`security_module` ) to work
properly against the instances in an object graph, all nodes in the
graph must be :term:`location` -aware.  This means they must have two
attributes: ``__parent__`` and ``__name__``.

The ``__parent__`` attribute should be a reference to the node's
parent model instance in the graph.  The ``__name__`` attribute should
be the name that a node's parent refers to the node via
``__getitem__``.

The ``__parent__`` of the root object should be ``None`` and its
``__name__`` should be the empty string.  For instance:

.. code-block:: python

   class MyRootObject(object):
       __name__ = ''
       __parent__ = None

A node returned from the root item's ``__getitem__`` method should
have a ``__parent__`` attribute that is a reference to the root
object, and its ``__name__`` attribute should match the name by which
it is reachable via the root object's ``__getitem__``.  *That*
object's ``__getitem__`` should return objects that have a
``__parent__`` attribute that points at that object, and
``__getitem__``-returned objects should have a ``__name__`` attribute
that matches the name by which they are retrieved via ``__getitem__``,
and so on.

.. warning:: If your root model object has a ``__name__`` argument
   that is not ``None`` or the empty string, URLs returned by the
   :func:`repoze.bfg.url.model_url` function and paths generated by
   the :func:`repoze.bfg.traversal.model_path` and
   :func:`repoze.bfg.traversal.model_path_tuple` APIs will be
   generated improperly.  The value of ``__name__`` will be prepended
   to every path and URL generated (as opposed to a single leading
   slash or empty tuple element).

.. index::
   single: model API functions
   single: url generation (traversal)

:mod:`repoze.bfg` API Functions That Act Against Models
-------------------------------------------------------

A model instance is used as the :term:`context` argument provided to a
view.  See :ref:`traversal_chapter` and :ref:`urldispatch_chapter` for
more information about how a model instance becomes the context.

The APIs provided by :ref:`traversal_module` are used against model
instances.  These functions can be used to find the "path" of a model,
the root model in an object graph, or generate a URL to a model.

The APIs provided by :ref:`location_module` are used against model
instances.  These can be used to walk down an object graph, or
conveniently locate one object "inside" another.

Some APIs in :ref:`security_module` accept a model object as a
parameter.  For example, the
:func:`repoze.bfg.security.has_permission` API accepts a "context" (a
model object) as one of its arguments; the ACL is obtained from this
model or one of its ancestors.  Other APIs in the
:mod:`repoze.bfg.security` module also accept :term:`context` as an
argument, and a context is always a model.
