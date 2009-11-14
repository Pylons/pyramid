Defending BFG's Design
======================

From time to time, challenges to various aspects of :mod:`repoze.bfg`
design are lodged.  To give context to the discussions that follow, we
detail some of the design decisions and tradeoffs here.

BFG Uses The Zope Component Architecture ("ZCA")
------------------------------------------------

BFG uses the :term:`Zope Component Architecture` (ZCA) under the hood.
This is a point of some contention.  :mod:`repoze.bfg` is of a
:term:`Zope` pedigree, so it was natural for its developers to use the
ZCA at its inception.  However, :mod:`repoze.bfg` allegiance to its
Zope pedigree is not blind.  We understand that using the ZCA has
issues and consequences, which we've attempted to address as best we
can.  Here'a an introspection about BFG's use of the ZCA, and the
tradeoffs its usage involves.

Problems
++++++++

The API that is commonly used to access data in a ZCA "component
registry" is not particularly pretty or intuitive, and sometimes it's
just plain obtuse.  Likewise, the conceptual load on a casual source
code reader of code that uses the component architecture is somewhat
high.  Consider a ZCA neophyte reading the code that performs a
typical "unnamed utility" lookup:

.. code-block:: python
   :linenos:

   from repoze.bfg.interfaces import ISettings
   from zope.component import getUtility
   settings = getUtility(ISettings)

After this code runs, ``settings`` will be a Python dictionary.  But
it's unlikely that any "civilian" would know that just by reading the
code.  There are a number of comprehension issues with the bit of code
above that are pretty obvious.

First, what's a "utility"?  Well, for the purposes of this dicussion,
and for the purpose of the code above, it's just not very important.
If you really care, you can go read `this
<http://www.muthukadan.net/docs/zca.html#utility>`_.  However, still,
folks need to understand the concept in order to parse the code while
reading it.  This is problem number one.

Second, what's this ``ISettings`` thing?  Well, it's an
:term:`interface`.  Is that important here?  Not really, we're just
using it as a "key" for some lookup based on its identity as a marker:
it represents an object that has the dictionary API, but that's not
really very important.  That's problem number two.

Third of all, what does ``getUtility`` do?  It's performing a lookup
for the ``ISettings`` "utility" that should return.. well, a utility.
Note how we've already built up a dependency on the understanding of
an :term:`interface` and the concept of "utility" to answer this
question: a bad sign so far.  Note also that the answer is circular, a
*really* bad sign.

Fourth, where does ``getUtility`` look to get the data?  Well, the
"component registry" of course.  What's a component registry?  Problem
number four.

Fifth, assuming you buy that there's some magical registry hanging
around, where *is* this registry?  Homina homina... "around"?  That's
sort of the best answer in this context (a more specific answer would
require knowledge of internals).  Can there be more than one?  Yes.
So *which* registry does it find the registration in?  Well, the
"current" registry of course.  In terms of :mod:`repoze.bfg`, the
current registry is a thread local variable.  Using an API that
consults a thread local makes understanding how it works nonlocal.

Sixth, fine, you've bought in to the fact that there's a registry that
is just "hanging around".  But how does the registry get populated?
Why, :term:`ZCML` of course.  Sometimes.  In this particular case,
however, the registration of ``ISettings`` is made by the framework
itself "under the hood": it's not present in any ZCML.  This is
extremely hard to comprehend.

Clearly there's some amount of cognitive load here that needs to be
borne by a reader of code that extends the :mod:`repoze.bfg` framework
due to its use of the ZCA, even if he or she is already an expert
Python programmer and whom is an expert in the domain of web
applications.  This is suboptimal.

Ameliorations
+++++++++++++

First, the biggest amelioration: :mod:`repoze.bfg` *does not expect
application developers to understand ZCA concepts or its API*.  If an
*application* developer needs to understand a ZCA concept or API
during the creation of a :mod:`repoze.bfg` application, we've failed
on some axis.  

Instead, the framework hides the presence of the ZCA behind
special-purpose API functions that *do* use the ZCA API.  Take for
example the ``repoze.bfg.security.authenticated_userid`` function,
which returns the userid present in the current request or ``None`` if
no userid is present in the current request.  The application
developer calls it like so:

.. code-block:: python
   :linenos:

    from repoze.bfg.security import authenticated_userid
    userid = authenticated_userid(request)

He now has the current user id.

Under its hood however, the implementation of ``authenticated_userid``
is this:

.. code-block:: python
   :linenos:

   def authenticated_userid(request):
       """ Return the userid of the currently authenticated user or
       ``None`` if there is no authentication policy in effect or there
       is no currently authenticated user. """

       policy = queryUtility(IAuthenticationPolicy)
       if policy is None:
           return None
       return policy.authenticated_userid(request)

Using such wrappers, we strive to always hide the ZCA this way from
application developers: application developers should just never know
about the ZCA.  They call a function with some object germane to the
domain, it returns a result; they needn't understand components at
all.  A corollary that follows is that any reader of an application
that has been written using :mod:`repoze.bfg` needn't understand the
ZCA either.

Hiding the ZCA from application developers and code readers in this
way a form of enhancing "domain specificity".  No end user wants to
understand the minutiae of the mechanics of how a web framework does
its thing.  People want to deal in concepts that are closer to the
domain they're working in: for example, web developers want to know
about *users*, not *utilities*.  :mod:`repoze.bfg` uses the ZCA as an
implementation detail, not as a feature which is exposed to end users.

However, unlike application developers, BFG *framework developers*,
including people who want to override :mod:`repoze.bfg` functionality
via preordained framework plugpoints like traversal or view lookup
*must* understand the ZCA.

:mod:`repoze.bfg` framework developers were so concerned about
conceptual load issues of the ZCA API for framework developers that a
`replacement <http://svn.repoze.org/repoze.component/trunk>`_ named
:mod:`repoze.component` was actually developed.  Though this package
is fully functional and well-tested, and its API is much nicer than
the ZCA API, work on it was largely abandoned and it is not used in
:mod:`repoze.bfg`.  We continued to use the ZCA within
:mod:`repoze.bfg` because it ultimately proved a better fit.

.. note:: We continued using ZCA rather than disusing it in favor of
   :mod:`repoze.component` largely because the ZCA concept of
   interfaces provides for use of an interface hierarchy, which is
   useful in a lot of scenarios (such as context type inheritance).
   Coming up with a marker type that was something like an interface
   that allowed for this functionality seemed like it was just
   reinventing the wheel.

Making framework developers and extenders understand the ZCA is a
tradeoff.  We (the :mod:`repoze.bfg` developers) like the features
that the ZCA gives us, and we have long-ago borne the weight of
understanding what it does and how it works.  The authors of
:mod:`repoze.bfg` understand the ZCA deeply and can read code that
uses it as easily as any other code.

We recognize that developers who my want to extend the framework are
not as comfortable with the :term:`Zope Component Architecture` (and
ZCML) as the original developers are with it.  So, for the purposes of
being kind to third-party :mod:`repoze.bfg` framework developers in,
we've turned the component registry used in BFG into something that is
accessible using the plain old dictionary API (like the
:mod:`repoze.component` API).  example in the problem section above
was:

.. code-block:: python
   :linenos:

   from repoze.bfg.interfaces import ISettings
   from zope.component import getUtility
   settings = getUtility(ISettings)

In a better world, we might be able to spell this as:

.. code-block:: python
   :linenos:

   from repoze.bfg.threadlocal import get_registry

   registry = get_registry()
   settings = registry['settings']

In this world, we've removed the need to understand utilities and
interfaces.  We *haven't* removed the need to understand the concept
of a *registry*, but for the purposes of this example, it's simply a
dictionary.  We haven't killed off the concept of a thread local
either.  Let's kill off thread locals, pretending to want to do this
in some code that has access to the :term:`request`:

.. code-block:: python
   :linenos:

   registry = request.registry
   settings = registry['settings']

In *this* world, we've reduced the conceptual problem to understanding
attributes and the dictionary API.  Every Python programmer knows
these things, even framework programmers!  Future versions of
:mod:`repoze.bfg` will try to make use of more domain specific APIs
such as this.  While :mod:`repoze.bfg` still uses some suboptimal
unnamed utility registrations and other superfluous ZCA API usages,
future versions of it will where possible disuse these things in favor
of straight dictionary assignments and lookups, as demonstrated above,
to be kinder to new developers and extenders.  We'll continue to seek
ways to reduce framework extender cognitive load.

Rationale
+++++++++

Here are the main rationales for BFG's design decision to use the ZCA:

- Pedigree.  A nontrivial part of the answer to this question is
  "pedigree".  Much of the design of :mod:`repoze.bfg` is stolen
  directly from :term:`Zope`.  Zope uses the ZCA to do a number of
  tricks.  :mod:`repoze.bfg` mimics these tricks apeishly, and,
  because the ZCA works pretty well for that set of tricks,
  :mod:`repoze.bfg` uses it for the same purposes.  For example, the
  way that BFG maps a :term:`request` to a :term:`view callable` is
  lifted almost entirely from Zope.  The ZCA plays an important role
  in the particulars of how this request to view mapping is done.

- Features.  The ZCA essentially provides what can be considered
  something like a "superdictionary", which allows for more complex
  lookups than retrieving a value based on a single key.  Some of this
  lookup capability is very useful for end users, such as being able
  to register a view that is only found when the context is some class
  of object, or when the context implements some :term:`interface`.

- Singularity.  There's only one "place" where "application
  configuration" lives in a BFG application: in a component registry.
  The component registry answers questions made to it by the framework
  at runtime based on the configuration of *an application*.  Note:
  "an application" is not the same as "a process", multiple
  independently configured copies of the same BFG application are
  capable of running in the same process space.

- Composability.  A ZCA registry can be populated imperatively, or
  there's an existing mechanism to populate a registry via the use of
  a configuration file (ZCML).  We didn't need to write a frontend
  from scratch to make use of configuration-file-driven registry
  population.

- Pluggability.  Use of the ZCA allows for framework extensibility via
  a well-defined and widely understood plugin architecture.  As long
  as framework developers and extenders understand the ZCA, it's
  possible to extend BFG almost arbitrarily.  For example, it's
  relatively easy to build a ZCML directive that registers several
  views "all at once", allowing app developers to use that ZCML
  directive as a "macro" in code that they write.  This is somewhat of
  a differentiating feature from other (non-Zope) frameworks.

- Testability.  Judicious use of the ZCA in framework code makes
  testing that code slightly easier.  Instead of using monkeypatching
  or other facilities to register mock objects for testing, we inject
  dependencies via ZCA registrations and then use lookups in the code
  find our mock objects.

- Speed.  The ZCA is very fast for a specific set of complex lookup
  scenarios that BFG uses, having been optimized through the years for
  just these purposes.  The ZCA contains optional C code for this
  purpose which demonstrably has no (or very few) bugs.

- Ecosystem.  Many existing Zope packages can be used in
  :mod:`repoze.bfg` with few (or no) changes due to our use of the ZCA
  and :term:`ZCML`.

Conclusion
++++++++++

If you only *develop applications* using :mod:`repoze.bfg`, there's
just basically nothing to think about here.  You just should never
need to understand the ZCA or even know about its presence: use
documented APIs instead.  If you're an application developer who
doesn't read API documentation because its unmanly, but instead uses
raw source code, and considers everything an API, and you've pained
yourself into a conceptual corner as a result of needing to wrestle
with some ZCA-using internals, it's hard to have a lot of sympathy for
you.  You'll either need to get familiar with how we're using the ZCA
or you'll need to use only the documented APIs; that's why we document
'em.

If you *extend* or *develop* :mod:`repoze.bfg` (create new ZCML
directives, use some of the more obscure "ZCML hooks" as described in
:ref:`hooks_chapter`, or work on the :mod:`repoze.bfg` core code), you
will be faced with needing to understand at least some ZCA concepts.
The ZCA API is pretty quirky: we've tried to make it at least slightly
nicer by disusing it for common registrations and lookups such as
unnamed utilities.  Some places it's used unabashedly, and will be
forever.  We know it's a bit quirky, but it's also useful and
fundamentally understandable if you take the time to do some reading
about it.

.. _zcml_encouragement:

BFG "Encourages Use of ZCML"
----------------------------

:term:`ZCML` is a configuration language that can be used to configure
the :term:`Zope Component Architecture` registry that BFG uses as its
application configuration.

Quick answer: well, it doesn't *really* encourage the use of ZCML.
Application developers can use the ``bfg_view`` decorator for the most
common form of configuration.  But, yes, a BFG application currently
does need to possess a ZCML file for it to begin executing
successfully even if its only contents are a ``<scan>`` directive that
kicks off the location of decorated views.

In any case, in the interest of completeness and in the spirit of
providing a lowest common denominator, BFG 1.2 will include a
completely imperative mode for all configuration.  You will be able to
make "single file" apps in this mode, which should help people who
need to see everything done completely imperatively.  For example, the
very most basic :mod:`repoze.bfg` "helloworld" program will become
something like::

  from webob import Response
  from  wsgiref import simple_server
  from repoze.bfg.registry import Registry
  from repoze.bfg.router import Router

  def helloworld_view(request):
      return Response(hello')

  if __name__ == '__main__':
      reg = Registry()
      reg.view(helloworld_view)
      app = Router(reg)
      simple_server.make_server('', 8080, app).serve_forever()

In this mode, no ZCML will be required for end users.  Hopefully this
mode will allow people who are used to doing everything imperatively
feel more comfortable.

BFG Uses ZCML; ZCML is XML and I Don't Like XML
-----------------------------------------------

:term:`ZCML` is a configuration language in the XML syntax.  It
contains elements that are mostly singleton tags that are called
*declarations*.  For an example:

.. code-block:: xml
   :linenos:

   <route
      view=".views.my_view"
      path="/"
      name="root"
      />

This declaration associates a :term:`view` with a route pattern.

We've tried to make the most common usages of :mod:`repoze.bfg`
palatable for XML-haters.  For example, the ``bfg_view`` decorator
function allows you to replace ``<view>`` statements in a ZCML file
with decorators attached to functions or methods.  In the future, BFG
will contain a mode that makes configuration completely imperative as
described in

However, currently, there are times when a BFG application developer
will be required to interact with ZCML, and thus XML.  Alas, it is
what it is.  All configuration formats suck in one way or another; I
personally don't think any of our lives would be markedly better if
the format were YAML, JSON, or INI.  It's all just plumbing that you
mostly cut and paste.

As described in :term:`zcml_encouragement`, in BFG 1.2, there will be
mode of configuration which is completely imperative (completely
Python-driven).  At this point, no :mod:`repoze.bfg` developer will
need to interact with ZCML/XML, they'll just be able to use Python.

.. _model_traversal_confusion:

BFG Uses "Model" To Represent A Node In The Graph of Objects Traversed
----------------------------------------------------------------------

The :mod:`repoze.bfg` documentation refers to the graph being
traversed when :term:`traversal` is used as a "model graph".  Some of
the :mod:`repoze.bfg` APIs also use the word "model" in them when
referring to a node in this graph (e.g. ``repoze.bfg.url.model_url``).

This confuses people who write applications that always use ORM
packages such as SQLAlchemy, which has a different notion of the
definition of a "model".  In a relational database, and when using the
API of common ORM packages, the model is almost certainly not a
directed acyclic graph (as may be the case in many graph databases).
Often model objects must be explicitly manufactured by an ORM as a
result of some query performed by a :term:`view`.  As a result, it can
be unnatural to think of the nodes traversed as "model" objects if you
develop your application using traversal and a relational database.
When you develop such applications, the things that :mod:`repoze.bfg`
refers to as "models" in such an application may just be stand-ins
that perform a query and generate some wrapper *for* an ORM "model"
(or set of ORM models).  The graph *might* be composed completely of
"model" objects (as defined by the ORM) but it also might not be. 

The naming impedance mismatch between the way the term "model" is used
to refer to a node in a graph in :mod:`repoze.bfg` and the way the
term "model" is used by packages like SQLAlchemy is unfortunate.  For
the purpose of avoiding confusion, if we had it to do all over again,
we might refer to the graph that :mod:`repoze.bfg` traverses a "node
graph" or "object graph" rather than a "model graph", but since we've
baked the name into the API, it's a little late.  Sorry.

In our defense, many :mod:`repoze.bfg` applications (especially ones
which use :term:`ZODB`) do indeed traverse a graph full of model
nodes.  Each node in the graph is a separate persistent object that is
stored within a database.  This was the use case considered when
coming up with the "model" terminology.

I Can't Figure Out How "BFG" Is Related to "Repoze"
---------------------------------------------------

When the `Repoze project <http://repoze.org>`_ was first started,
:mod:`repoze.bfg` did not exist.  The `website <http://repoze.org>`_
for the project had (and still has, of this writing) a tagline of
"Plumbing Zope into the WSGI Pipeline", and contained descriptions of
:term:`WSGI` middleware that were inspired by Zope features, and
applications that help :term:`Zope` to run within a WSGI environment.
The original intent was to create a "namespace" of packages
("repoze.*") that contained software that formed a decomposition of
Zope features into more WSGI-friendly components.  It was never the
intention of the Repoze project to actually create another web
framework.

However, due to an early naming mistake, the software composing the
BFG framework framework wwas added to this set of packages as
:mod:`repoze.bfg`.  While BFG uses Zope technology, it is otherwise
unrelated to the original goals of "Repoze" as stated on the
repoze.org website.  If we had it to do all over again, the BFG
package would be named simply "bfg".  But we don't.

At this point, therefore, the name "Repoze" should be considered
basically just a "brand".  Its presence in the name of a package means
nothing except that it has an origin as a piece of software developed
by a member of the Repoze community.

BFG Does Traversal, And I Don't Like Traversal
----------------------------------------------

In :mod:`repoze.bfg`, :term:`traversal` is the act of resolving a URL
path to a :term:`model` object in an object graph.  Some people are
uncomfortable with this notion, and believe it is wrong.

This is understandable.  The people who believe it is wrong almost
invariably have all of their data in a relational database.
Relational databases aren't naturally hierarchical, so "traversing"
one like a graph is not possible.  This problem is related to
:ref:`model_traversal_confusion`.

Folks who deem traversal unilaterally "wrong" are neglecting to take
into account that many persistence mechanisms *are* hierarchical.
Examples include a filesystem, an LDAP database, a :term:`ZODB` (or
another type of graph) database, an XML document, and the Python
module namespace.  It is often convenient to model the frontend to a
hierarchical data store as a graph, using traversal to apply views to
objects that either *are* the nodes in the graph being traversed (such
as in the case of ZODB) or at least ones which stand in for them (such
as in the case of wrappers for files from the filesystem).

Also, many website structures are naturally hierarchical, even if the
data which drives them isn't.  For example, newspaper websites are
often extremely hierarchical: sections within sections within
sections, ad infinitum.  If you want your URLs to indicate this
structure, and the structure is indefinite (the number of nested
sections can be "N" instead of some fixed number), traversal is an
excellent way to model this, even if the backend is a relational
database.  In this situation, the graph being traversed is actually
less a "model graph" than a site structure.

But the point is ultimately moot.  If you use :mod:`repoze.bfg`, and
you don't want to model your application in terms of traversal, you
needn't use it at all.  Instead, use :term:`URL dispatch` to map URL
paths to views.

BFG Does URL Dispatch, And I Don't Like URL Dispatch
----------------------------------------------------

In :mod:`repoze.bfg`, :term:`url dispatch` is the act of resolving a
URL path to a :term:`view` callable by performing pattern matching
against some set of ordered route definitions.  The route definitions
are examined in order: the first pattern which matches is used to
associate the URL with a view callable.

Some people are uncomfortable with this notion, and believe it is
wrong.  These are usually people who are steeped deeply in
:term:`Zope`.  Zope does not provide any mechanism except
:term:`traversal` to map code to URLs.  This is mainly because Zope
effectively requires use of :term:`ZODB`, which is a hierarchical
object store.  Zope also supports relational databases, but typically
the code that calls into the database lives somewhere in the ZODB
object graph (or at least is a :term:`view` related to a node in the
object graph), and traversal is required to reach this code.

I'll argue that URL dispatch is ultimately useful, even if you want to
use traversal as well.  You can actully *combine* URL dispatch and
traversal in :mod:`repoze.bfg` (see :ref:`hybrid_chapter`).  One
example of such a usage: if you want to emulate something like Zope
2's "Zope Management Interface" UI on top of your model graph (or any
administrative interface), you can register a route like ``<route
name="manage" path="manage/*traverse"/>`` and then associate
"management" views in your code by using the ``route_name`` argument
to a ``view`` configuration, e.g. ``<view view=".some.callable"
for=".some.Model" route_name="manage"/>``.  If you wire things up this
way someone then walks up to for example, ``/manage/ob1/ob2``, they
might be presented with a management interface, but walking up to
``/ob1/ob2`` would present them with the default object view.  There
are other tricks you can pull in these hybrid configurations if you're
clever (and maybe masochistic) too.

Also, if you are a URL dispatch hater, if you should ever be asked to
write an application that must use some legacy relational database
structure, you might find that using URL dispatch comes in handy for
one-off associations between views and URL paths.  Sometimes it's just
pointless to add a node to the object graph that effectively
represents the entry point for some bit of code.  You can just use a
route and be done with it.  If a route matches, a view associated with
the route will be called; if no route matches, :mod:`repoze.bfg` falls
back to using traversal.

But the point is ultimately moot.  If you use :mod:`repoze.bfg`, and
you really don't want to use URL dispatch, you needn't use it at all.
Instead, use :term:`traversal` exclusively to map URL paths to views,
just like you do in :term:`Zope`.

BFG Views Do Not Accept Arbitrary Keyword Arguments
---------------------------------------------------

Many web frameworks (Zope, TurboGears, Pylons, Django) allow for their
variant of a :term:`view callable` to accept arbitrary keyword or
positional arguments, which are "filled in" using values present in
the ``request.POST`` or ``request.GET`` dictionaries or by values
present in the "route match dictionary".  For example, a Django view
will accept positional arguments which match information in an
associated "urlconf" such as ``r'^polls/(?P<poll_id>\d+)/$``:

.. code-block:: python
   :linenos:

   def aview(request, poll_id):
       return HttpResponse(poll_id)

Zope, likewise allows you to add arbitrary keyword and positional
arguments to any method of a model object found via traversal:

.. code-block:: python
   :linenos:

   class MyZopeObject(Persistent):
        def aview(self, a, b, c=None):
            return '%s %s %c' % (a, b, c)

When this method is called as the result of being the published
callable, the Zope request object's GET and POST namespaces are
searched for keys which match the names of the positional and keyword
arguments in the request, and the method is called (if possible) with
its argument list filled with values mentioned therein.  TurboGears
and Pylons operate similarly.

:mod:`repoze.bfg` has neither of these features.  :mod:`repoze.bfg`
view callables always accept only ``context`` and ``request`` (or just
``request``), and no other arguments.  The rationale: this argument
specification matching done aggressively can be costly, and
:mod:`repoze.bfg` has performance as one of its main goals, so we've
decided to make people obtain information by interrogating the request
object for it in the view body instead of providing magic to do
unpacking into the view argument list.  The feature itself also just
seems a bit like a gimmick.  Getting the arguments you wnt explicitly
from the request via getitem is not really very hard; it's certainly
never a bottleneck for the author when he writes web apps.

It is possible to replicate the Zope-like behavior in a view callable
decorator, however, should you badly want something like it back.  No
such decorator currently exists.  If you'd like to create one, Google
for "zope mapply" and adapt the function you'll find to a decorator
that pulls the argument mapping information out of the
``request.params`` dictionary.

A similar feature could be implemented to provide the Django-like
behavior as a decorator by wrapping the view with a decorator that
looks in ``request.matchdict``.

It's possible at some point that :mod:`repoze.bfg` will grow some form
of argument matching feature (it would be simple to make it an
always-on optional feature that has no cost unless you actually use
it) for, but curently it has none.

BFG Provides Too Few "Rails"
----------------------------

:mod:`repoze.bfg` has a relatively parsimonious feature set.  It is
not a particularly "opinionated" web framework.  This is by design.

:mod:`repoze.bfg` contains no built in ORM nor any particular database
bindings.  It contains no prebaked REST helper functionality.  It
contains no form generation framework.  It contains no sessioning
library.  It does not help with internationalization of content.  It
has no adminstrative web user interface.  It has no built in text
indexing.  And so on.

:mod:`repoze.bfg` developers put opinionated functionality in
applications (and superframeworks) which we build on top of
:mod:`repoze.bfg` such as `KARL <http://www.karlproject.org/>`_.  BFG
is a reasonable platform on which to *build* a system that wants to be
more opinionated.  It's likely that such systems will emerge that are
built on BFG from various sources.

BFG Provides Too Many "Rails"
-----------------------------

:mod:`repoze.bfg` provides some features that other web frameworks do
not.  Most notably it has machinery which resolves a URL first to a
:term:`context` before calling a view (which has the capability to
accept the context in its argument list), and a declarative
authorization system that makes use of this feature.  Most other web
frameworks besides :term:`Zope`, from which the pattern was stolen,
have no equivalent core feature.

We consider this an important feature for a particular class of
applications (CMS-style applications, which the authors are often
commissioned to write) that usually use :term:`traversal` against a
persistent model graph.  The model graph contains security
declarations (as :term:`ACL` objects).

Having context-sensitive declarative security for individual objects
in the model graph is simply required for this class of application.
Other frameworks save for Zope just do not have this feature.  This is
the one of the primary reasons that BFG was actually written.

If you don't like this, it doesn't mean you can't use
:mod:`repoze.bfg`.  Just ignore this feature and avoid configuring an
authorization or authentication policy and using ACLs.  You can build
"Pylons-style" applications using :mod:`repoze.bfg` that use their own
security model via decorators or plain-old-imperative logic in view
code.

BFG Is Too Big
--------------

"OMG!  The :mod:`repoze.bfg` compressed tarball is, like, 1MB!  It
must be enormous!"

No.  We just ship it with test code and helper templates.  Here's a
breakdown of what's included in subdirectories of the package tree:

docs/

  2.3MB

repoze/bfg/tests

  548KB

repoze/bfg/paster_templates

  372KB

repoze/bfg (except for ``repoze/bfg/tests and repoze/bfg/paster_templates``)

  513K

In other words, the actual BFG code is about 10% of the total size of
the tarball omitting docs, helper templates used for package
generation, and test code.

Of the approximately 13K lines of Python code in the package, the code
that actually has a chance of executing during normal operation,
excluding tests and paster template Python files, accounts for
approximately 3K lines of Python code.  This is comparable to Pylons,
which ships with a little over 2K lines of Python code, excluding
tests.

BFG Has Too Many Dependencies
-----------------------------

This is true.  The total number of packages (at the time of this
writing) that :mod:`repoze.bfg` depends upon transitively is 17.  This
is a lot more than zero dependencies: a metric which some
"microframeworks" (and Django) boast of.

The :mod:`zope.component` and :mod:`zope.configuration` packages on
which :mod:`repoze.bfg` depends have transitive dependencies on
several other packages (:mod:`zope.schema`, :mod:`zope.i18n`,
:mod:`zope.event`, :mod:`zope.interface`, :mod:`zope.deprecation`,
:mod:`zope.i18nmessageid`).  We'd prefer that these packages have
fewer packages as transitive dependencies, and that much of the
functionality of these packages was moved into a smaller *number* of
packages.  We've been working with the Zope community to try to
collapse (or at least untangle) some of these dependencies.
:mod:`repoze.bfg` also has its own dependencies, such as
:mod:`martian`, :term:`Paste`, :term:`Chameleon`, :term:`WebOb` and
several other repoze packages.

It should be noted that :mod:`repoze.bfg` is positively lithe compared
to :term:`Zope` or :term:`Grok` which have, in their most common
configurations, roughly 118 dependencies. :mod:`repoze.bfg` has a
number of package dependencies comparable to other similar frameworks
such as Pylons.  We try not to reinvent too many wheels (at least the
ones that don't need reinventing), and this comes at a cost.  The cost
is some number of dependencies.

However, "number of packages" is just not a terribly great metric to
measure complexity.  For example, the :mod:`zope.event` package on
which :mod:`repoze.bfg` depends has a grand total of four lines of
code.  As noted above, we're continually trying to agitate for a
collapsing of packages like this.

BFG "Cheats" To Obtain Speed
----------------------------

Complaints have been lodged by other web framework authors at various
times that :mod:`repoze.bfg` "cheats" to gain performance.  One
claimed cheating mechanism is our use (transitively) of the C
extensions provided by :mod:`zope.interface` to do fast lookups.
Another claimed cheating mechanism is the religious avoidance of
extraneous function calls.

If there's such a thing as cheating to get better performance, we want
to cheat as much as possible.  This is otherwise known as
optimization.

BFG Gets Its Terminology Wrong ("MVC")
--------------------------------------

"I'm a MVC web framework user, and I'm confused.  BFG calls the
controller a view!  And it doesn't have any controllers."

People very much want to give web applications the same properties as
common desktop GUI platforms by using similar terminology, and to
provide some frame of reference for how various components in the
common web framework might hang together.  But in the opinion of the
author, "MVC" doesn't match the web very well in general. Quoting from
the `Model-View-Controller Wikipedia entry
<http://en.wikipedia.org/wiki/Model–view–controller>`_::

  Though MVC comes in different flavors, control flow is generally as
  follows:

    The user interacts with the user interface in some way (for
    example, presses a mouse button).

    The controller handles the input event from the user interface,
    often via a registered handler or callback and converts the event
    into appropriate user action, understandable for the model.

    The controller notifies the model of the user action, possibly  
    resulting in a change in the model's state. (For example, the
    controller updates the user's shopping cart.)[5]

    A view queries the model in order to generate an appropriate
    user interface (for example, the view lists the shopping cart's     
    contents). Note that the view gets its own data from the model.

    The controller may (in some implementations) issue a general
    instruction to the view to render itself. In others, the view is
    automatically notified by the model of changes in state
    (Observer) which require a screen update.

    The user interface waits for further user interactions, which
    restarts the cycle.

To be honest, it seems as if someone edited this Wikipedia definition,
torturously couching concepts in the most generic terms possible in
order to account for the use of the term "MVC" by current web
frameworks.  I doubt such a broad definition would ever be agreed to
by the original authors of the MVC pattern.  But *even so*, it seems
most "MVC" web frameworks fail to meet even this falsely generic
definition.

For example, do your templates (views) always query models directly as
is claimed in "note that the view gets its own data from the model"?
Probaby not.  My "controllers" tend to do this, massaging the data for
easier use by the "view" (template). What do you do when your
"controller" returns JSON? Do your controllers use a template to
generate JSON? If not, what's the "view" then?  Most MVC-style GUI web
frameworks have some sort of event system hooked up that lets the view
detect when the model changes.  The web just has no such facility in
its current form: it's pull-only.

So, in the interest of not mistaking desire with reality, and instead
of trying to jam the square peg that is the web into the round hole of
"MVC", we just punt and say there are two things: the model, and the
view. The model stores the data, the view presents it.  The templates
are really just an implementation detail of any given view: a view
doesn't need a template to return a response.  There's no
"controller": it just doesn't exist.  This seems to us like a more
reasonable model, given the current constraints of the web.

Other Topics
------------

We'll be trying to cover the following in this document as time allows:

- BFG View Lookup and Registration Is "Complex"

- BFG Template Lookup Is "Complex"

Other challenges are encouraged to be sent to the `Repoze-Dev
<http://lists.repoze.org/listinfo/repoze-dev>`_ maillist.  We'll try
to address them by considering a design change, or at very least via
exposition here.
