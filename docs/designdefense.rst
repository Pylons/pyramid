Defending BFG's Design
======================

From time to time, challenges to various aspects of :mod:`repoze.bfg`
design are lodged.  To give context to discussions that follow, we
detail some of the design decisions and trade-offs here.  In some
cases, we acknowledge that the framework can be made better and we
describe future steps which will be taken to improve it; in some cases
we just file the challenge as "noted", as obviously you can't please
everyone all of the time.

BFG Uses A Zope Component Architecture ("ZCA") Registry
-------------------------------------------------------

:mod:`repoze.bfg` uses a :term:`Zope Component Architecture` (ZCA)
"component registry" as its :term:`application registry` under the
hood.  This is a point of some contention.  :mod:`repoze.bfg` is of a
:term:`Zope` pedigree, so it was natural for its developers to use a
ZCA registry at its inception.  However, we understand that using a
ZCA registry has issues and consequences, which we've attempted to
address as best we can.  Here's an introspection about
:mod:`repoze.bfg` use of a ZCA registry, and the trade-offs its usage
involves.

Problems
++++++++

The "global" API that may be used to access data in a ZCA "component
registry" is not particularly pretty or intuitive, and sometimes it's
just plain obtuse.  Likewise, the conceptual load on a casual source
code reader of code that uses the ZCA global API is somewhat high.
Consider a ZCA neophyte reading the code that performs a typical
"unnamed utility" lookup using the :func:`zope.component.getUtility`
global API:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from repoze.bfg.interfaces import ISettings
   from zope.component import getUtility
   settings = getUtility(ISettings)

After this code runs, ``settings`` will be a Python dictionary.  But
it's unlikely that any "civilian" would know that just by reading the
code.  There are a number of comprehension issues with the bit of code
above that are obvious.

First, what's a "utility"?  Well, for the purposes of this discussion,
and for the purpose of the code above, it's just not very important.
If you really want to know, you can read `this
<http://www.muthukadan.net/docs/zca.html#utility>`_.  However, still,
readers of such code need to understand the concept in order to parse
it.  This is problem number one.

Second, what's this ``ISettings`` thing?  It's an :term:`interface`.
Is that important here?  Not really, we're just using it as a "key"
for some lookup based on its identity as a marker: it represents an
object that has the dictionary API, but that's not very important in
this context.  That's problem number two.

Third of all, what does the ``getUtility`` function do?  It's
performing a lookup for the ``ISettings`` "utility" that should
return.. well, a utility.  Note how we've already built up a
dependency on the understanding of an :term:`interface` and the
concept of "utility" to answer this question: a bad sign so far.  Note
also that the answer is circular, a *really* bad sign.

Fourth, where does ``getUtility`` look to get the data?  Well, the
"component registry" of course.  What's a component registry?  Problem
number four.

Fifth, assuming you buy that there's some magical registry hanging
around, where *is* this registry?  *Homina homina*... "around"?
That's sort of the best answer in this context (a more specific answer
would require knowledge of internals).  Can there be more than one
registry?  Yes.  So *which* registry does it find the registration in?
Well, the "current" registry of course.  In terms of
:mod:`repoze.bfg`, the current registry is a thread local variable.
Using an API that consults a thread local makes understanding how it
works non-local.

You've now bought in to the fact that there's a registry that is just
"hanging around".  But how does the registry get populated?  Why,
:term:`ZCML` of course.  Sometimes.  Or via imperative code.  In this
particular case, however, the registration of ``ISettings`` is made by
the framework itself "under the hood": it's not present in any ZCML
nor was it performed imperatively.  This is extremely hard to
comprehend.  Problem number six.

Clearly there's some amount of cognitive load here that needs to be
borne by a reader of code that extends the :mod:`repoze.bfg` framework
due to its use of the ZCA, even if he or she is already an expert
Python programmer and whom is an expert in the domain of web
applications.  This is suboptimal.

Ameliorations
+++++++++++++

First, the primary amelioration: :mod:`repoze.bfg` *does not expect
application developers to understand ZCA concepts or any of its APIs*.
If an *application* developer needs to understand a ZCA concept or API
during the creation of a :mod:`repoze.bfg` application, we've failed
on some axis.

Instead, the framework hides the presence of the ZCA registry behind
special-purpose API functions that *do* use ZCA APIs.  Take for
example the ``repoze.bfg.security.authenticated_userid`` function,
which returns the userid present in the current request or ``None`` if
no userid is present in the current request.  The application
developer calls it like so:

.. ignore-next-block
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

       registry = request.registry # the ZCA component registry
       policy = registry.queryUtility(IAuthenticationPolicy)
       if policy is None:
           return None
       return policy.authenticated_userid(request)

Using such wrappers, we strive to always hide the ZCA API from
application developers.  Application developers should just never know
about the ZCA API: they should call a Python function with some object
germane to the domain as an argument, and it should returns a result.
A corollary that follows is that any reader of an application that has
been written using :mod:`repoze.bfg` needn't understand the ZCA API
either.

Hiding the ZCA API from application developers and code readers is a
form of enhancing "domain specificity".  No application developer
wants to need to understand the minutiae of the mechanics of how a web
framework does its thing.  People want to deal in concepts that are
closer to the domain they're working in: for example, web developers
want to know about *users*, not *utilities*.  :mod:`repoze.bfg` uses
the ZCA as an implementation detail, not as a feature which is exposed
to end users.

However, unlike application developers, *framework developers*,
including people who want to override :mod:`repoze.bfg` functionality
via preordained framework plugpoints like traversal or view lookup
*must* understand the ZCA registry API.

:mod:`repoze.bfg` framework developers were so concerned about
conceptual load issues of the ZCA registry API for framework
developers that a `replacement registry implementation
<http://svn.repoze.org/repoze.component/trunk>`_ named
:mod:`repoze.component` was actually developed.  Though this package
has a registry implementation which is fully functional and
well-tested, and its API is much nicer than the ZCA registry API, work
on it was largely abandoned and it is not used in :mod:`repoze.bfg`.
We continued to use a ZCA registry within :mod:`repoze.bfg` because it
ultimately proved a better fit.

.. note:: We continued using ZCA registry rather than disusing it in
   favor of using the registry implementation in
   :mod:`repoze.component` largely because the ZCA concept of
   interfaces provides for use of an interface hierarchy, which is
   useful in a lot of scenarios (such as context type inheritance).
   Coming up with a marker type that was something like an interface
   that allowed for this functionality seemed like it was just
   reinventing the wheel.

Making framework developers and extenders understand the ZCA registry
API is a trade-off.  We (the :mod:`repoze.bfg` developers) like the
features that the ZCA registry gives us, and we have long-ago borne
the weight of understanding what it does and how it works.  The
authors of :mod:`repoze.bfg` understand the ZCA deeply and can read
code that uses it as easily as any other code.

But we recognize that developers who my want to extend the framework
are not as comfortable with the ZCA registry API as the original
developers are with it.  So, for the purposes of being kind to
third-party :mod:`repoze.bfg` framework developers in, we've drawn
some lines in the sand.

#) In all "core" code, We've made use of ZCA global API functions such
   as ``zope.component.getUtility`` and ``zope.component.getAdapter``
   the exception instead of the rule.  So instead of:

   .. code-block:: python
      :linenos:

      from repoze.bfg.interfaces import IAuthenticationPolicy
      from zope.component import getUtility
      policy = getUtility(IAuthenticationPolicy)

   :mod:`repoze.bfg` code will usually do:

   .. code-block:: python
      :linenos:

      from repoze.bfg.interfaces import IAuthenticationPolicy
      from repoze.bfg.threadlocal import get_current_registry
      registry = get_current_registry()
      policy = registry.getUtility(IAuthenticationPolicy)

   While the latter is more verbose, it also arguably makes it more
   obvious what's going on.  All of the :mod:`repoze.bfg` core code uses
   this pattern rather than the ZCA global API.

#) We've turned the component registry used by :mod:`repoze.bfg` into
   something that is accessible using the plain old dictionary API
   (like the :mod:`repoze.component` API).  For example, the snippet
   of code in the problem section above was:

   .. code-block:: python
      :linenos:

      from repoze.bfg.interfaces import ISettings
      from zope.component import getUtility
      settings = getUtility(ISettings)

   In a better world, we might be able to spell this as:

   .. code-block:: python
      :linenos:

      from repoze.bfg.threadlocal import get_current_registry

      registry = get_current_registry()
      settings = registry['settings']

   In this world, we've removed the need to understand utilities and
   interfaces, because we've disused them in favor of a plain dictionary
   lookup.  We *haven't* removed the need to understand the concept of a
   *registry*, but for the purposes of this example, it's simply a
   dictionary.  We haven't killed off the concept of a thread local
   either.  Let's kill off thread locals, pretending to want to do this
   in some code that has access to the :term:`request`:

   .. code-block:: python
      :linenos:

      registry = request.registry
      settings = registry['settings']

   In *this* world, we've reduced the conceptual problem to understanding
   attributes and the dictionary API.  Every Python programmer knows
   these things, even framework programmers.

While :mod:`repoze.bfg` still uses some suboptimal unnamed utility
registrations, future versions of it will where possible disuse these
things in favor of straight dictionary assignments and lookups, as
demonstrated above, to be kinder to new framework developers.  We'll
continue to seek ways to reduce framework developer cognitive load.

Rationale
+++++++++

Here are the main rationales involved in the :mod:`repoze.bfg`
decision to use the ZCA registry:

- Pedigree.  A nontrivial part of the answer to this question is
  "pedigree".  Much of the design of :mod:`repoze.bfg` is stolen
  directly from :term:`Zope`.  Zope uses the ZCA registry to do a
  number of tricks.  :mod:`repoze.bfg` mimics these tricks, and,
  because the ZCA registry works well for that set of tricks,
  :mod:`repoze.bfg` uses it for the same purposes.  For example, the
  way that :mod:`repoze.bfg` maps a :term:`request` to a :term:`view
  callable` is lifted almost entirely from Zope.  The ZCA registry
  plays an important role in the particulars of how this request to
  view mapping is done.

- Features.  The ZCA component registry essentially provides what can
  be considered something like a "superdictionary", which allows for
  more complex lookups than retrieving a value based on a single key.
  Some of this lookup capability is very useful for end users, such as
  being able to register a view that is only found when the context is
  some class of object, or when the context implements some
  :term:`interface`.

- Singularity.  There's only one "place" where "application
  configuration" lives in a :mod:`repoze.bfg` application: in a
  component registry.  The component registry answers questions made
  to it by the framework at runtime based on the configuration of *an
  application*.  Note: "an application" is not the same as "a
  process", multiple independently configured copies of the same
  :mod:`repoze.bfg` application are capable of running in the same
  process space.

- Composability.  A ZCA component registry can be populated
  imperatively, or there's an existing mechanism to populate a
  registry via the use of a configuration file (ZCML).  We didn't need
  to write a frontend from scratch to make use of
  configuration-file-driven registry population.

- Pluggability.  Use of the ZCA registry allows for framework
  extensibility via a well-defined and widely understood plugin
  architecture.  As long as framework developers and extenders
  understand the ZCA registry, it's possible to extend
  :mod:`repoze.bfg` almost arbitrarily.  For example, it's relatively
  easy to build a ZCML directive that registers several views "all at
  once", allowing app developers to use that ZCML directive as a
  "macro" in code that they write.  This is somewhat of a
  differentiating feature from other (non-Zope) frameworks.

- Testability.  Judicious use of the ZCA registry in framework code
  makes testing that code slightly easier.  Instead of using
  monkeypatching or other facilities to register mock objects for
  testing, we inject dependencies via ZCA registrations and then use
  lookups in the code find our mock objects.

- Speed.  The ZCA registry is very fast for a specific set of complex
  lookup scenarios that :mod:`repoze.bfg` uses, having been optimized
  through the years for just these purposes.  The ZCA registry
  contains optional C code for this purpose which demonstrably has no
  (or very few) bugs.

- Ecosystem.  Many existing Zope packages can be used in
  :mod:`repoze.bfg` with few (or no) changes due to our use of the ZCA
  registry and :term:`ZCML`.

Conclusion
++++++++++

If you only *develop applications* using :mod:`repoze.bfg`, there's
not much to complain about here.  You just should never need to
understand the ZCA registry or even know about its presence: use
documented :mod:`repoze.bfg` APIs instead.  However, you may be an
application developer who doesn't read API documentation because it's
unmanly. Instead you read the raw source code, and because you haven't
read the documentation, you don't know what functions, classes, and
methods even *form* the :mod:`repoze.bfg` API.  As a result, you've
now written code that uses internals and you've pained yourself into a
conceptual corner as a result of needing to wrestle with some
ZCA-using implementation detail.  If this is you, it's extremely hard
to have a lot of sympathy for you.  You'll either need to get familiar
with how we're using the ZCA registry or you'll need to use only the
documented APIs; that's why we document them as APIs.

If you *extend* or *develop* :mod:`repoze.bfg` (create new ZCML
directives, use some of the more obscure "ZCML hooks" as described in
:ref:`hooks_chapter`, or work on the :mod:`repoze.bfg` core code), you
will be faced with needing to understand at least some ZCA concepts.
The ZCA registry API is quirky: we've tried to make it at least
slightly nicer by disusing it for common registrations and lookups
such as unnamed utilities.  Some places it's used unabashedly, and
will be forever.  We know it's quirky, but it's also useful and
fundamentally understandable if you take the time to do some reading
about it.

BFG Uses Interfaces Too Liberally
---------------------------------

In this `TOPP Engineering blog entry
<http://www.coactivate.org/projects/topp-engineering/blog/2008/10/20/what-bothers-me-about-the-component-architecture/>`_,
Ian Bicking asserts that the way :mod:`repoze.bfg` uses a Zope
interface to represent an HTTP request method adds too much
indirection for not enough gain.  We agreed in general, and for this
reason, :mod:`repoze.bfg` version 1.1 added :term:`view predicate` and
:term:`route predicate` modifiers to view configuration.  Predicates
are request-specific (or :term:`context` -specific) matching narrowers
which don't use interfaces.  Instead, each predicate uses a
domain-specific string as a match value.

For example, to write a view configuration which matches only requests
with the ``POST`` HTTP request method, you might write a ``@bfg_view``
decorator which mentioned the ``request_method`` predicate:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view
   @bfg_view(name='post_view', request_method='POST', renderer='json')
   def post_view(request):
       return 'POSTed'

You might further narrow the matching scenario by adding an ``accept``
predicate that narrows matching to something that accepts a JSON
response:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view
   @bfg_view(name='post_view', request_method='POST', accept='application/json',
             renderer='json')
   def post_view(request):
       return 'POSTed'

Such a view would only match when the request indicated that HTTP
request method was ``POST`` and that the remote user agent passed
``application/json`` (or, for that matter, ``application/*``) in its
``Accept`` request header.

"Under the hood", these features make no use of interfaces.

For more information about predicates, see
:ref:`view_predicates_in_1dot1` and :ref:`route_predicates_in_1dot1`.

Many "prebaked" predicates exist.  However, use of only "prebaked"
predicates, however, doesn't entirely meet Ian's criterion.  He would
like to be able to match a request using a lambda or another function
which interrogates the request imperatively.  In version 1.2, we
acommodate this by allowing people to define "custom" view predicates:

.. code-block:: python
   :linenos:

   from repoze.bfg.view import bfg_view
   from webob import Response

   def subpath(context, request):
       return request.subpath and request.subpath[0] == 'abc'

   @bfg_view(custom_predicates=(subpath,))
   def aview(request):
       return Response('OK')

The above view will only match when the first element of the request's
:term:`subpath` is ``abc``.

.. _zcml_encouragement:

BFG "Encourages Use of ZCML"
----------------------------

:term:`ZCML` is a configuration language that can be used to configure
the :term:`Zope Component Architecture` registry that
:mod:`repoze.bfg` uses as its application configuration.

Quick answer: well, it doesn't *really* encourage the use of ZCML.  In
:mod:`repoze.bfg` 1.0 and 1.1, application developers could use
decorators for the most common form of configuration.  But, yes, a
:mod:`repoze.bfg` 1.0/1.1 application needed to possess a ZCML file
for it to begin executing successfully even if its only contents were
a ``<scan>`` directive that kicked off a scan to find decorated view
callables.

In the interest of completeness and in the spirit of providing a
lowest common denominator, :mod:`repoze.bfg` 1.2 includes a completely
imperative mode for all configuration.  You will be able to make
"single file" apps in this mode, which should help people who need to
see everything done completely imperatively.  For example, the very
most basic :mod:`repoze.bfg` "helloworld" program has become
something like:

.. code-block:: python
   :linenos:

   from webob import Response
   from paste.httpserver import serve
   from repoze.bfg.configuration import Configurator

   def hello_world(request):
       return Response('Hello world!')

   if __name__ == '__main__':
       config = Configurator()
       config.begin()
       config.add_view(hello_world)
       config.end()
       app = config.make_wsgi_app()
       serve(app)

In this mode, no ZCML is required for end users.  Hopefully this mode
will allow people who are used to doing everything imperatively feel
more comfortable.

BFG Uses ZCML; ZCML is XML and I Don't Like XML
-----------------------------------------------

:term:`ZCML` is a configuration language in the XML syntax.  Due to
the "imperative configuration" feature (new in :mod:`repoze.bfg` 1.2),
you don't need to use ZCML at all if you start a project from scratch.
But if you really do want to perform declarative configuration,
perhaps because you want to build an extensible application, you will
need to use and understand it.

:term:`ZCML` contains elements that are mostly singleton tags that are
called *declarations*.  For an example:

.. code-block:: xml
   :linenos:

   <route
      view=".views.my_view"
      path="/"
      name="root"
      />

This declaration associates a :term:`view` with a route pattern. 

All :mod:`repoze.bfg` declarations are singleton tags, unlike many
other XML configuration systems.  No XML *values* in ZCML are
meaningful; it's always just XML tags and attributes.  So in the very
common case it's not really very much different than an otherwise
"flat" configuration format like ``.ini``, except a developer can
*create* a directive that requires nesting (none of these exist in
:mod:`repoze.bfg` itself), and multiple "sections" can exist with the
same "name" (e.g. two ``<route>`` declarations) must be able to exist
simultaneously.

You might think some other configuration file format would be better.
But all configuration formats suck in one way or another.  I
personally don't think any of our lives would be markedly better if
the declarative configuration format used by :mod:`repoze.bfg` were
YAML, JSON, or INI.  It's all just plumbing that you mostly cut and
paste once you've progressed 30 minutes into your first project.
Folks who tend to agitate for another configuration file format are
folks that haven't yet spent that 30 minutes.

.. _model_traversal_confusion:

BFG Uses "Model" To Represent A Node In The Graph of Objects Traversed
----------------------------------------------------------------------

The :mod:`repoze.bfg` documentation refers to the graph being
traversed when :term:`traversal` is used as a "model graph".  Some of
the :mod:`repoze.bfg` APIs also use the word "model" in them when
referring to a node in this graph (e.g. ``repoze.bfg.url.model_url``).

A terminology overlap confuses people who write applications that
always use ORM packages such as SQLAlchemy, which has a different
notion of the definition of a "model".  When using the API of common
ORM packages, its conception of "model" is almost certainly not a
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
for the project had (and still has, of this writing) a tag line of
"Plumbing Zope into the WSGI Pipeline", and contained descriptions of
:term:`WSGI` middleware that were inspired by Zope features, and
applications that help :term:`Zope` to run within a WSGI environment.
The original intent was to create a "namespace" of packages
("repoze.*") that contained software that formed a decomposition of
Zope features into more WSGI-friendly components.  It was never the
intention of the Repoze project to actually create another web
framework.

However, as time progressed, the folks who ran the Repoze project
decided to create :mod:`repoze.bfg`, which *is* a web framework.  Due
to an early naming mistake, the software composing the framework was
named :mod:`repoze.bfg`.  This mistake was not corrected before the
software garnered a significant user base, and in the interest of
backwards compatibility, most likely never will be.  While
:mod:`repoze.bfg` uses Zope technology, it is otherwise unrelated to
the original goals of "Repoze" as stated on the repoze.org website.
If we had it to do all over again, the :mod:`repoze.bfg` package would
be named simply :mod:`bfg`.  But we don't have it to do all over
again.

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
use traversal as well.  You can actually *combine* URL dispatch and
traversal in :mod:`repoze.bfg` (see :ref:`hybrid_chapter`).  One
example of such a usage: if you want to emulate something like Zope
2's "Zope Management Interface" UI on top of your object graph (or any
administrative interface), you can register a route like ``<route
name="manage" path="manage/*traverse"/>`` and then associate
"management" views in your code by using the ``route_name`` argument
to a ``view`` configuration, e.g. ``<view view=".some.callable"
context=".some.Model" route_name="manage"/>``.  If you wire things up
this way someone then walks up to for example, ``/manage/ob1/ob2``,
they might be presented with a management interface, but walking up to
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

.. ignore-next-block
.. code-block:: python
   :linenos:

   from persistent import Persistent

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
seems a bit like a gimmick.  Getting the arguments you want explicitly
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
it) for, but currently it has none.

BFG Provides Too Few "Rails"
----------------------------

By design, :mod:`repoze.bfg` is not a particularly "opinionated" web
framework.  It has a relatively parsimonious feature set.  It contains
no built in ORM nor any particular database bindings.  It contains no
form generation framework or sessioning library.  It does not help
with internationalization of content.  It has no administrative web
user interface.  It has no built in text indexing.  It does not
dictate how you arrange your code.

Such opinionated functionality exists in applications and frameworks
built *on top* of :mod:`repoze.bfg`.  It's intended that higher-level
systems emerge built using :mod:`repoze.bfg` as a base.  See also
:ref:`apps_are_extensible`.

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
persistent object graph.  The object graph contains security
declarations as :term:`ACL` objects.

Having context-sensitive declarative security for individual objects
in the object graph is simply required for this class of application.
Other frameworks save for Zope just do not have this feature.  This is
one of the primary reasons that :mod:`repoze.bfg` was actually
written.

If you don't like this, it doesn't mean you can't use
:mod:`repoze.bfg`.  Just ignore this feature and avoid configuring an
authorization or authentication policy and using ACLs.  You can build
"Pylons-style" applications using :mod:`repoze.bfg` that use their own
security model via decorators or plain-old-imperative logic in view
code.

BFG Is Too Big
--------------

"The :mod:`repoze.bfg` compressed tarball is 1MB.  It must be
enormous!"

No.  We just ship it with test code and helper templates.  Here's a
breakdown of what's included in subdirectories of the package tree:

docs/

  2.2MB

repoze/bfg/tests

  580KB

repoze/bfg/paster_templates

  372KB

repoze/bfg (except for ``repoze/bfg/tests and repoze/bfg/paster_templates``)

  316K

The actual :mod:`repoze.bfg` runtime code is about 10% of the total
size of the tarball omitting docs, helper templates used for package
generation, and test code.  Of the approximately 13K lines of Python
code in the package, the code that actually has a chance of executing
during normal operation, excluding tests and paster template Python
files, accounts for approximately 3K lines of Python code.  This is
comparable to Pylons, which ships with a little over 2K lines of
Python code, excluding tests.

BFG Has Too Many Dependencies
-----------------------------

This is true.  At the time of this writing, the total number of Python
package distributions that :mod:`repoze.bfg` depends upon transitively
is 14 if you use Python 2.6, or 16, if you use Python 2.4 or 2.5.
This is a lot more than zero package distribution dependencies: a
metric which various Python microframeworks and Django boast.

The :mod:`zope.component` and :mod:`zope.configuration` packages on
which :mod:`repoze.bfg` depends have transitive dependencies on
several other packages (:mod:`zope.schema`, :mod:`zope.i18n`,
:mod:`zope.event`, :mod:`zope.interface`, :mod:`zope.deprecation`,
:mod:`zope.i18nmessageid`).  We've been working with the Zope
community to try to collapse and untangle some of these dependencies.
We'd prefer that these packages have fewer packages as transitive
dependencies, and that much of the functionality of these packages was
moved into a smaller *number* of packages.

:mod:`repoze.bfg` also has its own direct dependencies, such as
:term:`Paste`, :term:`Chameleon`, and :term:`WebOb`, and some of these
in turn have their own transitive dependencies.

It should be noted that :mod:`repoze.bfg` is positively lithe compared
to :term:`Grok`, a different Zope-based framework.  As of this
writing, in its default configuration, Grok has 126 package
distribution dependencies. The number of dependencies required by
:mod:`repoze.bfg` is many times fewer than Grok (or Zope itself, upon
which Grok is based).  :mod:`repoze.bfg` has a number of package
distribution dependencies comparable to similarly-targeted frameworks
such as Pylons.

We try not to reinvent too many wheels (at least the ones that don't
need reinventing), and this comes at the cost of some number of
dependencies.  However, "number of package distributions" is just not
a terribly great metric to measure complexity.  For example, the
:mod:`zope.event` distribution on which :mod:`repoze.bfg` depends has
a grand total of four lines of runtime code.  As noted above, we're
continually trying to agitate for a collapsing of these sorts of
packages into fewer distribution files.

BFG "Cheats" To Obtain Speed
----------------------------

Complaints have been lodged by other web framework authors at various
times that :mod:`repoze.bfg` "cheats" to gain performance.  One
claimed cheating mechanism is our use (transitively) of the C
extensions provided by :mod:`zope.interface` to do fast lookups.
Another claimed cheating mechanism is the religious avoidance of
extraneous function calls.

If there's such a thing as cheating to get better performance, we want
to cheat as much as possible.  We optimize :mod:`repoze.bfg`
aggressively.  This comes at a cost: the core code has sections that
could be expressed more readably.  As an amelioration, we've commented
these sections liberally.

BFG Gets Its Terminology Wrong ("MVC")
--------------------------------------

"I'm a MVC web framework user, and I'm confused.  :mod:`repoze.bfg`
calls the controller a view!  And it doesn't have any controllers."

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

To the author, it seems as if someone edited this Wikipedia
definition, tortuously couching concepts in the most generic terms
possible in order to account for the use of the term "MVC" by current
web frameworks.  I doubt such a broad definition would ever be agreed
to by the original authors of the MVC pattern.  But *even so*, it
seems most "MVC" web frameworks fail to meet even this falsely generic
definition.

For example, do your templates (views) always query models directly as
is claimed in "note that the view gets its own data from the model"?
Probably not.  My "controllers" tend to do this, massaging the data for
easier use by the "view" (template). What do you do when your
"controller" returns JSON? Do your controllers use a template to
generate JSON? If not, what's the "view" then?  Most MVC-style GUI web
frameworks have some sort of event system hooked up that lets the view
detect when the model changes.  The web just has no such facility in
its current form: it's effectively pull-only.

So, in the interest of not mistaking desire with reality, and instead
of trying to jam the square peg that is the web into the round hole of
"MVC", we just punt and say there are two things: the model, and the
view. The model stores the data, the view presents it.  The templates
are really just an implementation detail of any given view: a view
doesn't need a template to return a response.  There's no
"controller": it just doesn't exist.  This seems to us like a more
reasonable model, given the current constraints of the web.

.. _apps_are_extensible:

BFG Applications are Extensible; I Don't Believe In Application Extensibility
-----------------------------------------------------------------------------

Any :mod:`repoze.bfg` application written obeying certain constraints
is *extensible*. This feature is discussed in the :mod:`repoze.bfg`
documentation chapter named :ref:`extending_chapter`.  It is made
possible by the use of the :term:`Zope Component Architecture` and
:term:`ZCML` within :mod:`repoze.bfg`.

"Extensible", in this context, means:

- The behavior of an application can be overridden or extended in a
  particular *deployment* of the application without requiring that
  the deployer modify the source of the original application.

- The original developer is not required to anticipate any
  extensibility plugpoints at application creation time to allow
  fundamental application behavior to be overriden or extended.

- The original developer may optionally choose to anticipate an
  application-specific set of plugpoints, which will may be hooked by
  a deployer.  If he chooses to use the facilities provided by the
  ZCA, the original developer does not need to think terribly hard
  about the mechanics of introducing such a plugpoint.

Many developers seem to believe that creating extensible applications
is "not worth it".  They instead suggest that modifying the source of
a given application for each deployment to override behavior is more
reasonable.  Much discussion about version control branching and
merging typically ensues.

It's clear that making every application extensible isn't required.
The majority of web applications only have a single deployment, and
thus needn't be extensible at all.  However, some web applications
have multiple deployments, and some have *many* deployments.  For
example, a generic "content management" system (CMS) may have basic
functionality that needs to be extended for a particular deployment.
That CMS system may be deployed for many organizations at many places.
Some number of deployments of this CMS may be deployed centrally by a
third party and managed as a group.  It's useful to be able to extend
such a system for each deployment via preordained plugpoints than it
is to continually keep each software branch of the system in sync with
some upstream source: the upstream developers may change code in such
a way that your changes to the same codebase conflict with theirs in
fiddly, trivial ways.  Merging such changes repeatedly over the
lifetime of a deployment can be difficult and time consuming, and it's
often useful to be able to modify an application for a particular
deployment in a less invasive way.

If you don't want to think about :mod:`repoze.bfg` application
extensibility at all, you needn't.  You can ignore extensibility
entirely.  However, if you follow the set of rules defined in
:ref:`extending_chapter`, you don't need to *make* your application
extensible: any application you write in the framework just *is*
automatically extensible at a basic level.  The mechanisms that
deployers use to extend it will be necessarily coarse: typically,
views, routes, and resources will be capable of being overridden,
usually via :term:`ZCML`. But for most minor (and even some major)
customizations, these are often the only override plugpoints
necessary: if the application doesn't do exactly what the deployment
requires, it's often possible for a deployer to override a view,
route, or resource and quickly make it do what he or she wants it to
do in ways *not necessarily anticipated by the original developer*.
Here are some example scenarios demonstrating the benefits of such a
feature.

- If a deployment needs a different styling, the deployer may override
  the main template and the CSS in a separate Python package which
  defines overrides.

- If a deployment needs an application page to do something
  differently needs it to expose more or different information, the
  deployer may override the view that renders the page within a
  separate Python package.

- If a deployment needs an additional feature, the deployer may add a
  view to the override package.

As long as the fundamental design of the upstream package doesn't
change, these types of modifications often survive across many
releases of the upstream package without needing to be revisited.

Extending an application externally is not a panacea, and carries a
set of risks similar to branching and merging: sometimes major changes
upstream will cause you to need to revisit and update some of your
modifications.  But you won't regularly need to deal wth meaningless
textual merge conflicts that trivial changes to upstream packages
often entail when it comes time to update the upstream package,
because if you extend an application externally, there just is no
textual merge done.  Your modifications will also, for whatever its
worth, be contained in one, canonical, well-defined place.

Branching an application and continually merging in order to get new
features and bugfixes is clearly useful.  You can do that with a
:mod:`repoze.bfg` application just as usefully as you can do it with
any application.  But deployment of an application written in
:mod:`repoze.bfg` makes it possible to avoid the need for this even if
the application doesn't define any plugpoints ahead of time.  It's
possible that promoters of competing web frameworks dismiss this
feature in favor of branching and merging because applications written
in their framework of choice aren't extensible out of the box in a
comparably fundamental way.

While :mod:`repoze.bfg` application are fundamentally extensible even
if you don't write them with specific extensibility in mind, if you're
moderately adventurous, you can also take it a step further.  If you
learn more about the :term:`Zope Component Architecture`, you can
optionally use it to expose other more domain-specific configuration
plugpoints while developing an application.  The plugpoints you expose
needn't be as coarse as the ones provided automatically by
:mod:`repoze.bfg` itself.  For example, you might compose your own
:term:`ZCML` directive that configures a set of views for a prebaked
purpose (e.g. ``restview`` or somesuch) , allowing other people to
refer to that directive when they make declarations in the
``configure.zcml`` of their customization package.  There is a cost
for this: the developer of an application that defines custom
plugpoints for its deployers will need to understand the ZCA or he
will need to develop his own similar extensibility system.

Ultimately, any argument about whether the extensibility features lent
to applications by :mod:`repoze.bfg` are "good" or "bad" is somewhat
pointless. You needn't take advantage of the extensibility features
provided by a particular :mod:`repoze.bfg` application in order to
affect a modification for a particular set of its deployments.  You
can ignore the application's extensibility plugpoints entirely, and
instead use version control branching and merging to manage
application deployment modifications instead, as if you were deploying
an application written using any other web framework.

The Name BFG Is Not Safe For Work
---------------------------------

"Big Friendly Giant" is not safe for your work?  Where do you work? ;-)

The BFG API Isn't "Flat"
------------------------

The :mod:`repoze.bfg` API is organized in such a way that API imports
must come from submodules of the ``repoze.bfg`` namespace.  For
instance:

.. code-block:: python
   :linenos:

   from repoze.bfg.settings import get_settings
   from repoze.bfg.url import model_url

Some folks understandably don't want to think about the submodule
organization, and would rather be able to do:

.. ignore-next-block
.. code-block:: python
   :linenos:

   from repoze.bfg import get_settings
   from repoze.bfg import model_url

This would indeed be nice.  However, the ``repoze.bfg`` Python package
is a `namespace package <http://www.python.org/dev/peps/pep-0382/>`_.
The ``__init__.py`` of a namespace package cannot contain any
meaningful code such as imports from submodules which would let us
form a flatter API.  Sorry.

Though it makes the API slightly "thinkier", making the ``repoze.bfg``
package into a namespace package was an early design decision, which
we believe has paid off.  The primary goal is to make it possible to
move features *out* of the core ``repoze.bfg`` distribution and into
add-on distributions without breaking existing imports.  The
``repoze.bfg.lxml`` distribution is an example of such a package: this
functionality used to live in the core distribution, but we later
decided that a core dependency on ``lxml`` was unacceptable.  Because
``repoze.bfg`` is a namespace package, we were able to remove the
``repoze.bfg.lxml`` module from the core and create a distribution
named ``repoze.bfg.lxml`` which contains an eponymous package.  We
were then able, via our changelog, to inform people that might have
been depending on the feature that although it no longer shipped in
the core distribution, they could get it back *without changing any
code* by adding an ``install_requires`` line to their application
package's ``setup.py``.

Often new :mod:`repoze.bfg` features are released as add-on packages
in the ``repoze.bfg`` namespace.  Because ``repoze.bfg`` is a
namespace package, if we want to move one of these features *in* to
the core distribition at some point, we can do so without breaking
code which imports from the older package namespace.  This is
currently less useful than the ability to move features *out* of the
core distribution, as :mod:`setuptools` does not yet have any concept
of "obsoletes" metadata which we could add to the core distribution.
This means it's not yet possible to declaratively deprecate the older
non-core package in the eyes of tools like ``easy_install``, ``pip``
and ``buildout``.

Other Challenges
----------------

Other challenges are encouraged to be sent to the `Repoze-Dev
<http://lists.repoze.org/listinfo/repoze-dev>`_ maillist.  We'll try
to address them by considering a design change, or at very least via
exposition here.
