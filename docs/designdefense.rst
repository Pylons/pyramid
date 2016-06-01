.. _design_defense:

Defending Pyramid's Design
==========================

From time to time, challenges to various aspects of :app:`Pyramid` design are
lodged.  To give context to discussions that follow, we detail some of the
design decisions and trade-offs here.  In some cases, we acknowledge that the
framework can be made better and we describe future steps which will be taken
to improve it.  In others we just file the challenge as noted, as obviously you
can't please everyone all of the time.

Pyramid Provides More Than One Way to Do It
-------------------------------------------

A canon of Python popular culture is "TIOOWTDI" ("there is only one way to do
it", a slighting, tongue-in-cheek reference to Perl's "TIMTOWTDI", which is an
acronym for "there is more than one way to do it").

:app:`Pyramid` is, for better or worse, a "TIMTOWTDI" system.  For example, it
includes more than one way to resolve a URL to a :term:`view callable`: via
:term:`url dispatch` or :term:`traversal`. Multiple methods of configuration
exist: :term:`imperative configuration`, :term:`configuration decoration`, and
:term:`ZCML` (optionally via :term:`pyramid_zcml`). It works with multiple
different kinds of persistence and templating systems. And so on. However, the
existence of most of these overlapping ways to do things are not without reason
and purpose: we have a number of audiences to serve, and we believe that
TIMTOWTDI at the web framework level actually *prevents* a much more insidious
and harmful set of duplication at higher levels in the Python web community.

:app:`Pyramid` began its life as :mod:`repoze.bfg`, written by a team of people
with many years of prior :term:`Zope` experience.  The idea of
:term:`traversal` and the way :term:`view lookup` works was stolen entirely
from Zope.  The authorization subsystem provided by :app:`Pyramid` is a
derivative of Zope's.  The idea that an application can be *extended* without
forking is also a Zope derivative.

Implementations of these features were *required* to allow the :app:`Pyramid`
authors to build the bread-and-butter CMS-type systems for customers in the way
in which they were accustomed. No other system, save for Zope itself, had such
features, and Zope itself was beginning to show signs of its age. We were
becoming hampered by consequences of its early design mistakes. Zope's lack of
documentation was also difficult to work around. It was hard to hire smart
people to work on Zope applications because there was no comprehensive
documentation set which explained "it all" in one consumable place, and it was
too large and self-inconsistent to document properly. Before :mod:`repoze.bfg`
went under development, its authors obviously looked around for other
frameworks that fit the bill. But no non-Zope framework did. So we embarked on
building :mod:`repoze.bfg`.

As the result of our research, however, it became apparent that, despite the
fact that no *one* framework had all the features we required, lots of existing
frameworks had good, and sometimes very compelling ideas. In particular,
:term:`URL dispatch` is a more direct mechanism to map URLs to code.

So, although we couldn't find a framework, save for Zope, that fit our needs,
and while we incorporated a lot of Zope ideas into BFG, we also emulated the
features we found compelling in other frameworks (such as :term:`url
dispatch`). After the initial public release of BFG, as time went on, features
were added to support people allergic to various Zope-isms in the system, such
as the ability to configure the application using :term:`imperative
configuration` and :term:`configuration decoration`, rather than solely using
:term:`ZCML`, and the elimination of the required use of :term:`interface`
objects. It soon became clear that we had a system that was very generic, and
was beginning to appeal to non-Zope users as well as ex-Zope users.

As the result of this generalization, it became obvious BFG shared 90% of its
feature set with the feature set of Pylons 1, and thus had a very similar
target market. Because they were so similar, choosing between the two systems
was an exercise in frustration for an otherwise non-partisan developer. It was
also strange for the Pylons and BFG development communities to be in
competition for the same set of users, given how similar the two frameworks
were. So the Pylons and BFG teams began to work together to form a plan to
merge. The features missing from BFG (notably :term:`view handler` classes,
flash messaging, and other minor missing bits), were added to provide
familiarity to ex-Pylons users. The result is :app:`Pyramid`.

The Python web framework space is currently notoriously balkanized. We're truly
hoping that the amalgamation of components in :app:`Pyramid` will appeal to at
least two currently very distinct sets of users: Pylons and BFG users. By
unifying the best concepts from Pylons and BFG into a single codebase, and
leaving the bad concepts from their ancestors behind, we'll be able to
consolidate our efforts better, share more code, and promote our efforts as a
unit rather than competing pointlessly. We hope to be able to shortcut the pack
mentality which results in a *much larger* duplication of effort, represented
by competing but incredibly similar applications and libraries, each built upon
a specific low level stack that is incompatible with the other. We'll also
shrink the choice of credible Python web frameworks down by at least one. We're
also hoping to attract users from other communities (such as Zope's and
TurboGears') by providing the features they require, while allowing enough
flexibility to do things in a familiar fashion. Some overlap of functionality
to achieve these goals is expected and unavoidable, at least if we aim to
prevent pointless duplication at higher levels. If we've done our job well
enough, the various audiences will be able to coexist and cooperate rather than
firing at each other across some imaginary web framework DMZ.

Pyramid Uses a Zope Component Architecture ("ZCA") Registry
-----------------------------------------------------------

:app:`Pyramid` uses a :term:`Zope Component Architecture` (ZCA) "component
registry" as its :term:`application registry` under the hood.  This is a
point of some contention.  :app:`Pyramid` is of a :term:`Zope` pedigree, so
it was natural for its developers to use a ZCA registry at its inception.
However, we understand that using a ZCA registry has issues and consequences,
which we've attempted to address as best we can.  Here's an introspection
about :app:`Pyramid` use of a ZCA registry, and the trade-offs its usage
involves.

Problems
++++++++

The global API that may be used to access data in a ZCA component registry
is not particularly pretty or intuitive, and sometimes it's just plain
obtuse.  Likewise, the conceptual load on a casual source code reader of code
that uses the ZCA global API is somewhat high.  Consider a ZCA neophyte
reading the code that performs a typical "unnamed utility" lookup using the
:func:`zope.component.getUtility` global API:

.. code-block:: python
   :linenos:

   from pyramid.interfaces import ISettings
   from zope.component import getUtility
   settings = getUtility(ISettings)

After this code runs, ``settings`` will be a Python dictionary.  But it's
unlikely that any civilian would know that just by reading the code.  There
are a number of comprehension issues with the bit of code above that are
obvious.

First, what's a "utility"?  Well, for the purposes of this discussion, and
for the purpose of the code above, it's just not very important.  If you
really want to know, you can read `this
<http://muthukadan.net/docs/zca.html#utility>`_.  However, still, readers
of such code need to understand the concept in order to parse it.  This is
problem number one.

Second, what's this ``ISettings`` thing?  It's an :term:`interface`.  Is that
important here?  Not really, we're just using it as a key for some lookup
based on its identity as a marker: it represents an object that has the
dictionary API, but that's not very important in this context.  That's
problem number two.

Third of all, what does the ``getUtility`` function do?  It's performing a
lookup for the ``ISettings`` "utility" that should return... well, a utility.
Note how we've already built up a dependency on the understanding of an
:term:`interface` and the concept of "utility" to answer this question: a bad
sign so far.  Note also that the answer is circular, a *really* bad sign.

Fourth, where does ``getUtility`` look to get the data?  Well, the "component
registry" of course.  What's a component registry?  Problem number four.

Fifth, assuming you buy that there's some magical registry hanging around,
where *is* this registry?  *Homina homina*... "around"?  That's sort of the
best answer in this context (a more specific answer would require knowledge of
internals).  Can there be more than one registry?  Yes.  So in *which* registry
does it find the registration?  Well, the "current" registry of course.  In
terms of :app:`Pyramid`, the current registry is a thread local variable.
Using an API that consults a thread local makes understanding how it works
non-local.

You've now bought in to the fact that there's a registry that is just hanging
around.  But how does the registry get populated?  Why, via code that calls
directives like ``config.add_view``.  In this particular case, however, the
registration of ``ISettings`` is made by the framework itself under the hood:
it's not present in any user configuration.  This is extremely hard to
comprehend.  Problem number six.

Clearly there's some amount of cognitive load here that needs to be borne by a
reader of code that extends the :app:`Pyramid` framework due to its use of the
ZCA, even if they are already an expert Python programmer and an expert in the
domain of web applications.  This is suboptimal.

Ameliorations
+++++++++++++

First, the primary amelioration: :app:`Pyramid` *does not expect application
developers to understand ZCA concepts or any of its APIs*.  If an *application*
developer needs to understand a ZCA concept or API during the creation of a
:app:`Pyramid` application, we've failed on some axis.

Instead the framework hides the presence of the ZCA registry behind
special-purpose API functions that *do* use ZCA APIs.  Take for example the
``pyramid.security.authenticated_userid`` function, which returns the userid
present in the current request or ``None`` if no userid is present in the
current request.  The application developer calls it like so:

.. code-block:: python
   :linenos:

   from pyramid.security import authenticated_userid
   userid = authenticated_userid(request)

They now have the current user id.

Under its hood however, the implementation of ``authenticated_userid`` is this:

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

Using such wrappers, we strive to always hide the ZCA API from application
developers.  Application developers should just never know about the ZCA API;
they should call a Python function with some object germane to the domain as an
argument, and it should return a result.  A corollary that follows is that any
reader of an application that has been written using :app:`Pyramid` needn't
understand the ZCA API either.

Hiding the ZCA API from application developers and code readers is a form of
enhancing domain specificity.  No application developer wants to need to
understand the small, detailed mechanics of how a web framework does its thing.
People want to deal in concepts that are closer to the domain they're working
in. For example, web developers want to know about *users*, not *utilities*.
:app:`Pyramid` uses the ZCA as an implementation detail, not as a feature which
is exposed to end users.

However, unlike application developers, *framework developers*, including
people who want to override :app:`Pyramid` functionality via preordained
framework plugpoints like traversal or view lookup, *must* understand the ZCA
registry API.

:app:`Pyramid` framework developers were so concerned about conceptual load
issues of the ZCA registry API that a `replacement registry implementation
<https://github.com/repoze/repoze.component>`_ named :mod:`repoze.component`
was actually developed.  Though this package has a registry implementation
which is fully functional and well-tested, and its API is much nicer than the
ZCA registry API, work on it was largely abandoned, and it is not used in
:app:`Pyramid`.  We continued to use a ZCA registry within :app:`Pyramid`
because it ultimately proved a better fit.

.. note::

   We continued using ZCA registry rather than disusing it in favor of using
   the registry implementation in :mod:`repoze.component` largely because the
   ZCA concept of interfaces provides for use of an interface hierarchy, which
   is useful in a lot of scenarios (such as context type inheritance).  Coming
   up with a marker type that was something like an interface that allowed for
   this functionality seemed like it was just reinventing the wheel.

Making framework developers and extenders understand the ZCA registry API is a
trade-off.  We (the :app:`Pyramid` developers) like the features that the ZCA
registry gives us, and we have long-ago borne the weight of understanding what
it does and how it works.  The authors of :app:`Pyramid` understand the ZCA
deeply and can read code that uses it as easily as any other code.

But we recognize that developers who might want to extend the framework are not
as comfortable with the ZCA registry API as the original developers.  So for
the purpose of being kind to third-party :app:`Pyramid` framework developers,
we've drawn some lines in the sand.

In all core code, we've made use of ZCA global API functions, such as
``zope.component.getUtility`` and ``zope.component.getAdapter``, the exception
instead of the rule.  So instead of:

.. code-block:: python
   :linenos:

   from pyramid.interfaces import IAuthenticationPolicy
   from zope.component import getUtility
   policy = getUtility(IAuthenticationPolicy)

:app:`Pyramid` code will usually do:

.. code-block:: python
   :linenos:

   from pyramid.interfaces import IAuthenticationPolicy
   from pyramid.threadlocal import get_current_registry
   registry = get_current_registry()
   policy = registry.getUtility(IAuthenticationPolicy)

While the latter is more verbose, it also arguably makes it more obvious what's
going on.  All of the :app:`Pyramid` core code uses this pattern rather than
the ZCA global API.

Rationale
+++++++++

Here are the main rationales involved in the :app:`Pyramid` decision to use
the ZCA registry:

- History.  A nontrivial part of the answer to this question is "history".
  Much of the design of :app:`Pyramid` is stolen directly from :term:`Zope`.
  Zope uses the ZCA registry to do a number of tricks.  :app:`Pyramid` mimics
  these tricks, and, because the ZCA registry works well for that set of
  tricks, :app:`Pyramid` uses it for the same purposes.  For example, the way
  that :app:`Pyramid` maps a :term:`request` to a :term:`view callable` using
  :term:`traversal` is lifted almost entirely from Zope.  The ZCA registry
  plays an important role in the particulars of how this request to view
  mapping is done.

- Features.  The ZCA component registry essentially provides what can be
  considered something like a superdictionary, which allows for more complex
  lookups than retrieving a value based on a single key.  Some of this lookup
  capability is very useful for end users, such as being able to register a
  view that is only found when the context is some class of object, or when
  the context implements some :term:`interface`.

- Singularity.  There's only one place where "application configuration" lives
  in a :app:`Pyramid` application: in a component registry.  The component
  registry answers questions made to it by the framework at runtime based on
  the configuration of *an application*.  Note: "an application" is not the
  same as "a process"; multiple independently configured copies of the same
  :app:`Pyramid` application are capable of running in the same process space.

- Composability.  A ZCA component registry can be populated imperatively, or
  there's an existing mechanism to populate a registry via the use of a
  configuration file (ZCML, via the optional :term:`pyramid_zcml` package).
  We didn't need to write a frontend from scratch to make use of
  configuration-file-driven registry population.

- Pluggability.  Use of the ZCA registry allows for framework extensibility
  via a well-defined and widely understood plugin architecture.  As long as
  framework developers and extenders understand the ZCA registry, it's
  possible to extend :app:`Pyramid` almost arbitrarily.  For example, it's
  relatively easy to build a directive that registers several views all at
  once, allowing app developers to use that directive as a "macro" in code
  that they write.  This is somewhat of a differentiating feature from other
  (non-Zope) frameworks.

- Testability.  Judicious use of the ZCA registry in framework code makes
  testing that code slightly easier.  Instead of using monkeypatching or other
  facilities to register mock objects for testing, we inject dependencies via
  ZCA registrations, then use lookups in the code to find our mock objects.

- Speed.  The ZCA registry is very fast for a specific set of complex lookup
  scenarios that :app:`Pyramid` uses, having been optimized through the years
  for just these purposes.  The ZCA registry contains optional C code for
  this purpose which demonstrably has no (or very few) bugs.

- Ecosystem.  Many existing Zope packages can be used in :app:`Pyramid` with
  few (or no) changes due to our use of the ZCA registry.

Conclusion
++++++++++

If you only *develop applications* using :app:`Pyramid`, there's not much to
complain about here.  You just should never need to understand the ZCA registry
API; use documented :app:`Pyramid` APIs instead.  However, you may be an
application developer who doesn't read API documentation. Instead you
read the raw source code, and because you haven't read the API documentation,
you don't know what functions, classes, and methods even *form* the
:app:`Pyramid` API.  As a result, you've now written code that uses internals,
and you've painted yourself into a conceptual corner, needing to wrestle with
some ZCA-using implementation detail.  If this is you, it's extremely hard to
have a lot of sympathy for you.  You'll either need to get familiar with how
we're using the ZCA registry or you'll need to use only the documented APIs;
that's why we document them as APIs.

If you *extend* or *develop* :app:`Pyramid` (create new directives, use some
of the more obscure hooks as described in :ref:`hooks_chapter`, or work on
the :app:`Pyramid` core code), you will be faced with needing to understand
at least some ZCA concepts.  In some places it's used unabashedly, and will
be forever.  We know it's quirky, but it's also useful and fundamentally
understandable if you take the time to do some reading about it.


.. _zcml_encouragement:

Pyramid "Encourages Use of ZCML"
--------------------------------

:term:`ZCML` is a configuration language that can be used to configure the
:term:`Zope Component Architecture` registry that :app:`Pyramid` uses for
application configuration.  Often people claim that Pyramid "needs ZCML".

It doesn't.  In :app:`Pyramid` 1.0, ZCML doesn't ship as part of the core;
instead it ships in the :term:`pyramid_zcml` add-on package, which is
completely optional.  No ZCML is required at all to use :app:`Pyramid`, nor
any other sort of frameworky declarative frontend to application
configuration.


Pyramid Does Traversal, and I Don't Like Traversal
--------------------------------------------------

In :app:`Pyramid`, :term:`traversal` is the act of resolving a URL path to a
:term:`resource` object in a resource tree.  Some people are uncomfortable with
this notion, and believe it is wrong. Thankfully if you use :app:`Pyramid` and
you don't want to model your application in terms of a resource tree, you
needn't use it at all. Instead use :term:`URL dispatch` to map URL paths to
views.

The idea that some folks believe traversal is unilaterally wrong is
understandable.  The people who believe it is wrong almost invariably have
all of their data in a relational database.  Relational databases aren't
naturally hierarchical, so traversing one like a tree is not possible.

However, folks who deem traversal unilaterally wrong are neglecting to take
into account that many persistence mechanisms *are* hierarchical.  Examples
include a filesystem, an LDAP database, a :term:`ZODB` (or another type of
graph) database, an XML document, and the Python module namespace.  It is
often convenient to model the frontend to a hierarchical data store as a
graph, using traversal to apply views to objects that either *are* the
resources in the tree being traversed (such as in the case of ZODB) or at
least ones which stand in for them (such as in the case of wrappers for files
from the filesystem).

Also, many website structures are naturally hierarchical, even if the data
which drives them isn't.  For example, newspaper websites are often extremely
hierarchical: sections within sections within sections, ad infinitum.  If you
want your URLs to indicate this structure, and the structure is indefinite
(the number of nested sections can be "N" instead of some fixed number), a
resource tree is an excellent way to model this, even if the backend is a
relational database.  In this situation, the resource tree is just a site
structure.

Traversal also offers better composability of applications than URL dispatch,
because it doesn't rely on a fixed ordering of URL matching.  You can compose
a set of disparate functionality (and add to it later) around a mapping of
view to resource more predictably than trying to get the right ordering of
URL pattern matching.

But the point is ultimately moot.  If you don't want to use traversal, you
needn't.  Use URL dispatch instead.


Pyramid Does URL Dispatch, and I Don't Like URL Dispatch
--------------------------------------------------------

In :app:`Pyramid`, :term:`url dispatch` is the act of resolving a URL path to
a :term:`view` callable by performing pattern matching against some set of
ordered route definitions.  The route definitions are examined in order: the
first pattern which matches is used to associate the URL with a view
callable.

Some people are uncomfortable with this notion, and believe it is wrong.
These are usually people who are steeped deeply in :term:`Zope`.  Zope does
not provide any mechanism except :term:`traversal` to map code to URLs.  This
is mainly because Zope effectively requires use of :term:`ZODB`, which is a
hierarchical object store.  Zope also supports relational databases, but
typically the code that calls into the database lives somewhere in the ZODB
object graph (or at least is a :term:`view` related to a node in the object
graph), and traversal is required to reach this code.

I'll argue that URL dispatch is ultimately useful, even if you want to use
traversal as well.  You can actually *combine* URL dispatch and traversal in
:app:`Pyramid` (see :ref:`hybrid_chapter`).  One example of such a usage: if
you want to emulate something like Zope 2's "Zope Management Interface" UI on
top of your object graph (or any administrative interface), you can register a
route like ``config.add_route('manage', '/manage/*traverse')`` and then
associate "management" views in your code by using the ``route_name`` argument
to a ``view`` configuration, e.g., ``config.add_view('.some.callable',
context=".some.Resource", route_name='manage')``.  If you wire things up this
way, someone then walks up to, for example, ``/manage/ob1/ob2``, they might be
presented with a management interface, but walking up to ``/ob1/ob2`` would
present them with the default object view.  There are other tricks you can pull
in these hybrid configurations if you're clever (and maybe masochistic) too.

Also, if you are a URL dispatch hater, if you should ever be asked to write an
application that must use some legacy relational database structure, you might
find that using URL dispatch comes in handy for one-off associations between
views and URL paths.  Sometimes it's just pointless to add a node to the object
graph that effectively represents the entry point for some bit of code.  You
can just use a route and be done with it.  If a route matches, a view
associated with the route will be called. If no route matches, :app:`Pyramid`
falls back to using traversal.

But the point is ultimately moot.  If you use :app:`Pyramid`, and you really
don't want to use URL dispatch, you needn't use it at all.  Instead, use
:term:`traversal` exclusively to map URL paths to views, just like you do in
:term:`Zope`.


Pyramid Views Do Not Accept Arbitrary Keyword Arguments
-------------------------------------------------------

Many web frameworks (Zope, TurboGears, Pylons 1.X, Django) allow for their
variant of a :term:`view callable` to accept arbitrary keyword or positional
arguments, which are filled in using values present in the ``request.POST``,
``request.GET``, or route match dictionaries.  For example, a Django view will
accept positional arguments which match information in an associated "urlconf"
such as ``r'^polls/(?P<poll_id>\d+)/$``:

.. code-block:: python
   :linenos:

   def aview(request, poll_id):
       return HttpResponse(poll_id)

Zope likewise allows you to add arbitrary keyword and positional arguments to
any method of a resource object found via traversal:

.. code-block:: python
   :linenos:

   from persistent import Persistent

   class MyZopeObject(Persistent):
        def aview(self, a, b, c=None):
            return '%s %s %c' % (a, b, c)

When this method is called as the result of being the published callable, the
Zope request object's GET and POST namespaces are searched for keys which
match the names of the positional and keyword arguments in the request, and
the method is called (if possible) with its argument list filled with values
mentioned therein.  TurboGears and Pylons 1.X operate similarly.

Out of the box, :app:`Pyramid` is configured to have none of these features. By
default :app:`Pyramid` view callables always accept only ``request`` and no
other arguments. The rationale is, this argument specification matching when
done aggressively can be costly, and :app:`Pyramid` has performance as one of
its main goals. Therefore we've decided to make people, by default, obtain
information by interrogating the request object within the view callable body
instead of providing magic to do unpacking into the view argument list.

However, as of :app:`Pyramid` 1.0a9, user code can influence the way view
callables are expected to be called, making it possible to compose a system
out of view callables which are called with arbitrary arguments.  See
:ref:`using_a_view_mapper`.

Pyramid Provides Too Few "Rails"
--------------------------------

By design, :app:`Pyramid` is not a particularly opinionated web framework.
It has a relatively parsimonious feature set.  It contains no built in ORM
nor any particular database bindings.  It contains no form generation
framework.  It has no administrative web user interface.  It has no built in
text indexing.  It does not dictate how you arrange your code.

Such opinionated functionality exists in applications and frameworks built
*on top* of :app:`Pyramid`.  It's intended that higher-level systems emerge
built using :app:`Pyramid` as a base.

.. seealso::

    See also :ref:`apps_are_extensible`.

Pyramid Provides Too Many "Rails"
---------------------------------

:app:`Pyramid` provides some features that other web frameworks do not.
These are features meant for use cases that might not make sense to you if
you're building a simple bespoke web application:

- An optional way to map URLs to code using :term:`traversal` which implies a
  walk of a :term:`resource tree`.

- The ability to aggregate Pyramid application configuration from multiple
  sources using :meth:`pyramid.config.Configurator.include`.

- View and subscriber registrations made using :term:`interface` objects
  instead of class objects (e.g., :ref:`using_resource_interfaces`).

- A declarative :term:`authorization` system.

- Multiple separate I18N :term:`translation string` factories, each of which
  can name its own domain.

These features are important to the authors of :app:`Pyramid`.  The
:app:`Pyramid` authors are often commissioned to build CMS-style
applications.  Such applications are often frameworky because they have more
than one deployment.  Each deployment requires a slightly different
composition of sub-applications, and the framework and sub-applications often
need to be *extensible*.  Because the application has more than one
deployment, pluggability and extensibility is important, as maintaining
multiple forks of the application, one per deployment, is extremely
undesirable.  Because it's easier to extend a system that uses
:term:`traversal` from the outside than it is to do the same in a system that
uses :term:`URL dispatch`, each deployment uses a :term:`resource tree`
composed of a persistent tree of domain model objects, and uses
:term:`traversal` to map :term:`view callable` code to resources in the tree.
The resource tree contains very granular security declarations, as resources
are owned and accessible by different sets of users.  Interfaces are used to
make unit testing and implementation substitutability easier.

In a bespoke web application, usually there's a single canonical deployment,
and therefore no possibility of multiple code forks.  Extensibility is not
required; the code is just changed in place.  Security requirements are often
less granular.  Using the features listed above will often be overkill for such
an application.

If you don't like these features, it doesn't mean you can't or shouldn't use
:app:`Pyramid`.  They are all optional, and a lot of time has been spent making
sure you don't need to know about them up front.  You can build "Pylons 1.X
style" applications using :app:`Pyramid` that are purely bespoke by ignoring
the features above.  You may find these features handy later after building a
bespoke web application that suddenly becomes popular and requires
extensibility because it must be deployed in multiple locations.

Pyramid Is Too Big
------------------

"The :app:`Pyramid` compressed tarball is larger than 2MB.  It must beenormous!"

No.  We just ship it with docs, test code, and scaffolding.  Here's a breakdown
of what's included in subdirectories of the package tree:

docs/

  3.6MB

pyramid/tests/

  1.3MB

pyramid/scaffolds/

  133KB

pyramid/ (except for ``pyramid/tests`` and ``pyramid/scaffolds``)

  812KB

Of the approximately 34K lines of Python code in the package, the code
that actually has a chance of executing during normal operation, excluding
tests and scaffolding Python files, accounts for approximately 10K lines.


Pyramid Has Too Many Dependencies
---------------------------------

Over time, we've made lots of progress on reducing the number of packaging
dependencies Pyramid has had.  Pyramid 1.2 had 15 of them.  Pyramid 1.3 and 1.4
had 12 of them.  The current release as of this writing, Pyramid 1.5, has
only 7.  This number is unlikely to become any smaller.

A port to Python 3 completed in Pyramid 1.3 helped us shed a good number of
dependencies by forcing us to make better packaging decisions.  Removing
Chameleon and Mako templating system dependencies in the Pyramid core in 1.5
let us shed most of the remainder of them.


Pyramid "Cheats" to Obtain Speed
--------------------------------

Complaints have been lodged by other web framework authors at various times
that :app:`Pyramid` "cheats" to gain performance.  One claimed cheating
mechanism is our use (transitively) of the C extensions provided by
:mod:`zope.interface` to do fast lookups.  Another claimed cheating mechanism
is the religious avoidance of extraneous function calls.

If there's such a thing as cheating to get better performance, we want to cheat
as much as possible. We optimize :app:`Pyramid` aggressively. This comes at a
cost. The core code has sections that could be expressed with more readability.
As an amelioration, we've commented these sections liberally.


Pyramid Gets Its Terminology Wrong ("MVC")
------------------------------------------

"I'm a MVC web framework user, and I'm confused.  :app:`Pyramid` calls the
controller a view!  And it doesn't have any controllers."

If you are in this camp, you might have come to expect things about how your
existing "MVC" framework uses its terminology.  For example, you probably
expect that models are ORM models, controllers are classes that have methods
that map to URLs, and views are templates.  :app:`Pyramid` indeed has each of
these concepts, and each probably *works* almost exactly like your existing
"MVC" web framework. We just don't use the MVC terminology, as we can't square
its usage in the web framework space with historical reality.

People very much want to give web applications the same properties as common
desktop GUI platforms by using similar terminology, and to provide some frame
of reference for how various components in the common web framework might
hang together.  But in the opinion of the author, "MVC" doesn't match the web
very well in general. Quoting from the `Model-View-Controller Wikipedia entry
<https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93controller>`_:

    Though MVC comes in different flavors, control flow is generally as
    follows:

      The user interacts with the user interface in some way (for example,
      presses a mouse button).

      The controller handles the input event from the user interface, often via
      a registered handler or callback and converts the event into appropriate
      user action, understandable for the model.

      The controller notifies the model of the user action, possibly resulting
      in a change in the model's state. (For example, the controller updates the
      user's shopping cart.)[5]

      A view queries the model in order to generate an appropriate user
      interface (for example, the view lists the shopping cart's contents). Note
      that the view gets its own data from the model.

      The controller may (in some implementations) issue a general instruction
      to the view to render itself. In others, the view is automatically
      notified by the model of changes in state (Observer) which require a
      screen update.

      The user interface waits for further user interactions, which restarts the
      cycle.

To the author, it seems as if someone edited this Wikipedia definition,
tortuously couching concepts in the most generic terms possible in order to
account for the use of the term "MVC" by current web frameworks.  I doubt such
a broad definition would ever be agreed to by the original authors of the MVC
pattern.  But *even so*, it seems most MVC web frameworks fail to meet even
this falsely generic definition.

For example, do your templates (views) always query models directly as is
claimed in "note that the view gets its own data from the model"? Probably not.
My "controllers" tend to do this, massaging the data for easier use by the
"view" (template). What do you do when your "controller" returns JSON? Do your
controllers use a template to generate JSON? If not, what's the "view" then?
Most MVC-style GUI web frameworks have some sort of event system hooked up that
lets the view detect when the model changes. The web just has no such facility
in its current form; it's effectively pull-only.

So, in the interest of not mistaking desire with reality, and instead of trying
to jam the square peg that is the web into the round hole of "MVC", we just
punt and say there are two things: resources and views. The resource tree
represents a site structure, the view presents a resource. The templates are
really just an implementation detail of any given view. A view doesn't need a
template to return a response. There's no "controller"; it just doesn't exist.
The "model" is either represented by the resource tree or by a "domain model"
(like an SQLAlchemy model) that is separate from the framework entirely. This
seems to us like more reasonable terminology, given the current constraints of
the web.


.. _apps_are_extensible:

Pyramid Applications Are Extensible; I Don't Believe in Application Extensibility
---------------------------------------------------------------------------------

Any :app:`Pyramid` application written obeying certain constraints is
*extensible*. This feature is discussed in the :app:`Pyramid` documentation
chapters named :ref:`extending_chapter` and :ref:`advconfig_narr`. It is made
possible by the use of the :term:`Zope Component Architecture` within
:app:`Pyramid`.

"Extensible" in this context means:

- The behavior of an application can be overridden or extended in a particular
  *deployment* of the application without requiring that the deployer modify
  the source of the original application.

- The original developer is not required to anticipate any extensibility
  plug points at application creation time to allow fundamental application
  behavior to be overridden or extended.

- The original developer may optionally choose to anticipate an
  application-specific set of plug points, which may be hooked by a deployer.
  If they choose to use the facilities provided by the ZCA, the original
  developer does not need to think terribly hard about the mechanics of
  introducing such a plug point.

Many developers seem to believe that creating extensible applications is not
worth it. They instead suggest that modifying the source of a given application
for each deployment to override behavior is more reasonable. Much discussion
about version control branching and merging typically ensues.

It's clear that making every application extensible isn't required. The
majority of web applications only have a single deployment, and thus needn't be
extensible at all. However some web applications have multiple deployments, and
others have *many* deployments. For example, a generic content management
system (CMS) may have basic functionality that needs to be extended for a
particular deployment. That CMS may be deployed for many organizations at many
places. Some number of deployments of this CMS may be deployed centrally by a
third party and managed as a group. It's easier to be able to extend such a
system for each deployment via preordained plug points than it is to
continually keep each software branch of the system in sync with some upstream
source. The upstream developers may change code in such a way that your changes
to the same codebase conflict with theirs in fiddly, trivial ways. Merging such
changes repeatedly over the lifetime of a deployment can be difficult and time
consuming, and it's often useful to be able to modify an application for a
particular deployment in a less invasive way.

If you don't want to think about :app:`Pyramid` application extensibility at
all, you needn't. You can ignore extensibility entirely. However if you follow
the set of rules defined in :ref:`extending_chapter`, you don't need to *make*
your application extensible. Any application you write in the framework just
*is* automatically extensible at a basic level. The mechanisms that deployers
use to extend it will be necessarily coarse. Typically views, routes, and
resources will be capable of being overridden. But for most minor (and even
some major) customizations, these are often the only override plug points
necessary. If the application doesn't do exactly what the deployment requires,
it's often possible for a deployer to override a view, route, or resource, and
quickly make it do what they want it to do in ways *not necessarily anticipated
by the original developer*. Here are some example scenarios demonstrating the
benefits of such a feature.

- If a deployment needs a different styling, the deployer may override the main
  template and the CSS in a separate Python package which defines overrides.

- If a deployment needs an application page to do something differently, or to
  expose more or different information, the deployer may override the view that
  renders the page within a separate Python package.

- If a deployment needs an additional feature, the deployer may add a view to
  the override package.

As long as the fundamental design of the upstream package doesn't change, these
types of modifications often survive across many releases of the upstream
package without needing to be revisited.

Extending an application externally is not a panacea, and carries a set of
risks similar to branching and merging. Sometimes major changes upstream will
cause you to revisit and update some of your modifications. But you won't
regularly need to deal with meaningless textual merge conflicts that trivial
changes to upstream packages often entail when it comes time to update the
upstream package, because if you extend an application externally, there just
is no textual merge done. Your modifications will also, for whatever it's
worth, be contained in one, canonical, well-defined place.

Branching an application and continually merging in order to get new features
and bug fixes is clearly useful. You can do that with a :app:`Pyramid`
application just as usefully as you can do it with any application. But
deployment of an application written in :app:`Pyramid` makes it possible to
avoid the need for this even if the application doesn't define any plug points
ahead of time. It's possible that promoters of competing web frameworks dismiss
this feature in favor of branching and merging because applications written in
their framework of choice aren't extensible out of the box in a comparably
fundamental way.

While :app:`Pyramid` applications are fundamentally extensible even if you
don't write them with specific extensibility in mind, if you're moderately
adventurous, you can also take it a step further. If you learn more about the
:term:`Zope Component Architecture`, you can optionally use it to expose other
more domain-specific configuration plug points while developing an application.
The plug points you expose needn't be as coarse as the ones provided
automatically by :app:`Pyramid` itself. For example, you might compose your own
directive that configures a set of views for a pre-baked purpose (e.g.,
``restview`` or somesuch), allowing other people to refer to that directive
when they make declarations in the ``includeme`` of their customization
package. There is a cost for this: the developer of an application that defines
custom plug points for its deployers will need to understand the ZCA or they
will need to develop their own similar extensibility system.

Ultimately any argument about whether the extensibility features lent to
applications by :app:`Pyramid` are good or bad is mostly pointless. You needn't
take advantage of the extensibility features provided by a particular
:app:`Pyramid` application in order to affect a modification for a particular
set of its deployments. You can ignore the application's extensibility plug
points entirely, and use version control branching and merging to manage
application deployment modifications instead, as if you were deploying an
application written using any other web framework.


Zope 3 Enforces "TTW" Authorization Checks by Default; Pyramid Does Not
-----------------------------------------------------------------------

Challenge
+++++++++

:app:`Pyramid` performs automatic authorization checks only at :term:`view`
execution time. Zope 3 wraps context objects with a security proxy, which
causes Zope 3 also to do security checks during attribute access. I like this,
because it means:

#) When I use the security proxy machinery, I can have a view that
   conditionally displays certain HTML elements (like form fields) or
   prevents certain attributes from being modified depending on the
   permissions that the accessing user possesses with respect to a context
   object.

#) I want to also expose my resources via a REST API using Twisted Web. If
   Pyramid performed authorization based on attribute access via Zope3's
   security proxies, I could enforce my authorization policy in both
   :app:`Pyramid` and in the Twisted-based system the same way.

Defense
+++++++

:app:`Pyramid` was developed by folks familiar with Zope 2, which has a
"through the web" security model.  This TTW security model was the precursor
to Zope 3's security proxies.  Over time, as the :app:`Pyramid` developers
(working in Zope 2) created such sites, we found authorization checks during
code interpretation extremely useful in a minority of projects.  But much of
the time, TTW authorization checks usually slowed down the development
velocity of projects that had no delegation requirements.  In particular, if
we weren't allowing untrusted users to write arbitrary Python code to be
executed by our application, the burden of through the web security checks
proved too costly to justify.  We (collectively) haven't written an
application on top of which untrusted developers are allowed to write code in
many years, so it seemed to make sense to drop this model by default in a new
web framework.

And since we tend to use the same toolkit for all web applications, it's just
never been a concern to be able to use the same set of restricted-execution
code under two different web frameworks.

Justifications for disabling security proxies by default notwithstanding,
given that Zope 3 security proxies are viral by nature, the only requirement
to use one is to make sure you wrap a single object in a security proxy and
make sure to access that object normally when you want proxy security checks
to happen.  It is possible to override the :app:`Pyramid` traverser for a
given application (see :ref:`changing_the_traverser`).  To get Zope3-like
behavior, it is possible to plug in a different traverser which returns
Zope3-security-proxy-wrapped objects for each traversed object (including the
:term:`context` and the :term:`root`).  This would have the effect of
creating a more Zope3-like environment without much effort.


.. _http_exception_hierarchy:

Pyramid uses its own HTTP exception class hierarchy rather than :mod:`webob.exc`
--------------------------------------------------------------------------------

.. versionadded:: 1.1

The HTTP exception classes defined in :mod:`pyramid.httpexceptions` are very
much like the ones defined in :mod:`webob.exc`, (e.g.,
:class:`~pyramid.httpexceptions.HTTPNotFound` or
:class:`~pyramid.httpexceptions.HTTPForbidden`).  They have the same names and
largely the same behavior, and all have a very similar implementation, but not
the same identity.  Here's why they have a separate identity.

- Making them separate allows the HTTP exception classes to subclass
  :class:`pyramid.response.Response`.  This speeds up response generation
  slightly due to the way the Pyramid router works.  The same speed up could be
  gained by monkeypatching :class:`webob.response.Response`, but it's usually
  the case that monkeypatching turns out to be evil and wrong.

- Making them separate allows them to provide alternate ``__call__`` logic,
  which also speeds up response generation.

- Making them separate allows the exception classes to provide for the proper
  value of ``RequestClass`` (:class:`pyramid.request.Request`).

- Making them separate gives us freedom from thinking about backwards
  compatibility code present in :mod:`webob.exc` related to Python 2.4, which
  we no longer support in Pyramid 1.1+.

- We change the behavior of two classes
  (:class:`~pyramid.httpexceptions.HTTPNotFound` and
  :class:`~pyramid.httpexceptions.HTTPForbidden`) in the module so that they
  can be used by Pyramid internally for ``notfound`` and ``forbidden``
  exceptions.

- Making them separate allows us to influence the docstrings of the exception
  classes to provide Pyramid-specific documentation.

- Making them separate allows us to silence a stupid deprecation warning under
  Python 2.6 when the response objects are used as exceptions (related to
  ``self.message``).


.. _simpler_traversal_model:

Pyramid has simpler traversal machinery than does Zope
------------------------------------------------------

Zope's default traverser:

- Allows developers to mutate the traversal name stack while traversing (they
  can add and remove path elements).

- Attempts to use an adaptation to obtain the next element in the path from
  the currently traversed object, falling back to ``__bobo_traverse__``,
  ``__getitem__``, and eventually ``__getattr__``.

Zope's default traverser allows developers to mutate the traversal name stack
during traversal by mutating ``REQUEST['TraversalNameStack']``. Pyramid's
default traverser (``pyramid.traversal.ResourceTreeTraverser``) does not offer
a way to do this. It does not maintain a stack as a request attribute and, even
if it did, it does not pass the request to resource objects while it's
traversing. While it was handy at times, this feature was abused in frameworks
built atop Zope (like CMF and Plone), often making it difficult to tell exactly
what was happening when a traversal didn't match a view. I felt it was better
for folks that wanted the feature to make them replace the traverser rather
than build that particular honey pot in to the default traverser.

Zope uses multiple mechanisms to attempt to obtain the next element in the
resource tree based on a name.  It first tries an adaptation of the current
resource to ``ITraversable``, and if that fails, it falls back to attempting a
number of magic methods on the resource (``__bobo_traverse__``,
``__getitem__``, and ``__getattr__``).  My experience while both using Zope and
attempting to reimplement its publisher in ``repoze.zope2`` led me to believe
the following:

- The *default* traverser should be as simple as possible.  Zope's publisher
  is somewhat difficult to follow and replicate due to the fallbacks it tried
  when one traversal method failed.  It is also slow.

- The *entire traverser* should be replaceable, not just elements of the
  traversal machinery.  Pyramid has a few big components rather than a
  plethora of small ones.  If the entire traverser is replaceable, it's an
  antipattern to make portions of the default traverser replaceable.  Doing
  so is a "knobs on knobs" pattern, which is unfortunately somewhat endemic
  in Zope.  In a "knobs on knobs" pattern, a replaceable subcomponent of a
  larger component is made configurable using the same configuration
  mechanism that can be used to replace the larger component.  For example,
  in Zope, you can replace the default traverser by registering an adapter.
  But you can also (or alternately) control how the default traverser
  traverses by registering one or more adapters.  As a result of being able
  to either replace the larger component entirely or turn knobs on the
  default implementation of the larger component, no one understands when (or
  whether) they should ever override the larger component entrirely.  This
  results, over time, in a rusting together of the larger "replaceable"
  component and the framework itself because people come to depend on the
  availability of the default component in order just to turn its knobs. The
  default component effectively becomes part of the framework, which entirely
  subverts the goal of making it replaceable.  In Pyramid, typically if a
  component is replaceable, it will itself have no knobs (it will be solid
  state).  If you want to influence behavior controlled by that component,
  you will replace the component instead of turning knobs attached to the
  component.


.. _microframeworks_smaller_hello_world:

Microframeworks have smaller Hello World programs
-------------------------------------------------

Self-described "microframeworks" exist. `Bottle
<http://bottlepy.org/docs/dev/index.html>`_ and `Flask
<http://flask.pocoo.org/>`_ are two that are becoming popular. `Bobo
<http://bobo.digicool.com/en/latest/>`_ doesn't describe itself as a
microframework, but its intended user base is much the same. Many others exist.
We've even (only as a teaching tool, not as any sort of official project)
`created one using Pyramid <http://static.repoze.org/casts/videotags.html>`_.
The videos use BFG, a precursor to Pyramid, but the resulting code is
`available for Pyramid too <https://github.com/Pylons/groundhog>`_).
Microframeworks are small frameworks with one common feature: each allows its
users to create a fully functional application that lives in a single Python
file.

Some developers and microframework authors point out that Pyramid's "hello
world" single-file program is longer (by about five lines) than the equivalent
program in their favorite microframework. Guilty as charged.

This loss isn't for lack of trying. Pyramid is useful in the same circumstance
in which microframeworks claim dominance: single-file applications. But Pyramid
doesn't sacrifice its ability to credibly support larger applications in order
to achieve "hello world" lines of code parity with the current crop of
microframeworks. Pyramid's design instead tries to avoid some common pitfalls
associated with naive declarative configuration schemes. The subsections which
follow explain the rationale.


.. _you_dont_own_modulescope:

Application programmers don't control the module-scope codepath (import-time side-effects are evil)
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Imagine a directory structure with a set of Python files in it:

.. code-block:: text

    .
    |-- app.py
    |-- app2.py
    `-- config.py

The contents of ``app.py``:

.. code-block:: python
    :linenos:

    from config import decorator
    from config import L
    import pprint

    @decorator
    def foo():
        pass

    if __name__ == '__main__':
        import app2
        pprint.pprint(L)

The contents of ``app2.py``:

.. code-block:: python
    :linenos:

    import app

    @app.decorator
    def bar():
        pass

The contents of ``config.py``:

.. code-block:: python
    :linenos:

    L = []

    def decorator(func):
        L.append(func)
        return func

If we ``cd`` to the directory that holds these files, and we run
``python app.py``, given the directory structure and code above, what happens?
Presumably, our ``decorator`` decorator will be used twice, once by the
decorated function ``foo`` in ``app.py``, and once by the decorated function
``bar`` in ``app2.py``. Since each time the decorator is used, the list ``L``
in ``config.py`` is appended to, we'd expect a list with two elements to be
printed, right? Sadly, no:

.. code-block:: text

    [chrism@thinko]$ python app.py 
    [<function foo at 0x7f4ea41ab1b8>,
     <function foo at 0x7f4ea41ab230>,
     <function bar at 0x7f4ea41ab2a8>]

By visual inspection, that outcome (three different functions in the list)
seems impossible. We defined only two functions, and we decorated each of those
functions only once, so we believe that the ``decorator`` decorator will run
only twice. However, what we believe is in fact wrong, because the code at
module scope in our ``app.py`` module was *executed twice*. The code is
executed once when the script is run as ``__main__`` (via ``python app.py``),
and then it is executed again when ``app2.py`` imports the same file as
``app``.

What does this have to do with our comparison to microframeworks? Many
microframeworks in the current crop (e.g., Bottle and Flask) encourage you to
attach configuration decorators to objects defined at module scope. These
decorators execute arbitrarily complex registration code, which populates a
singleton registry that is a global which is in turn defined in external Python
module. This is analogous to the above example: the "global registry" in the
above example is the list ``L``.

Let's see what happens when we use the same pattern with the `Groundhog
<https://github.com/Pylons/groundhog>`_ microframework.  Replace the contents
of ``app.py`` above with this:

.. code-block:: python
    :linenos:

    from config import gh

    @gh.route('/foo/')
    def foo():
        return 'foo'

    if __name__ == '__main__':
        import app2
        pprint.pprint(L)

Replace the contents of ``app2.py`` above with this:

.. code-block:: python
    :linenos:

    import app

    @app.gh.route('/bar/')
    def bar():
        'return bar'

Replace the contents of ``config.py`` above with this:

.. code-block:: python
    :linenos:

    from groundhog import Groundhog
    gh = Groundhog('myapp', 'seekrit')

How many routes will be registered within the routing table of the "gh"
Groundhog application?  If you answered three, you are correct.  How many
would a casual reader (and any sane developer) expect to be registered?  If
you answered two, you are correct.  Will the double registration be a
problem?  With our Groundhog framework's ``route`` method backing this
application, not really.  It will slow the application down a little bit,
because it will need to miss twice for a route when it does not match.  Will
it be a problem with another framework, another application, or another
decorator?  Who knows.  You need to understand the application in its
totality, the framework in its totality, and the chronology of execution to
be able to predict what the impact of unintentional code double-execution
will be.

The encouragement to use decorators which perform population of an external
registry has an unintended consequence: the application developer now must
assert ownership of every code path that executes Python module scope code.
Module-scope code is presumed by the current crop of decorator-based
microframeworks to execute once and only once. If it executes more than once,
weird things will start to happen. It is up to the application developer to
maintain this invariant. Unfortunately, in reality this is an impossible task,
because Python programmers *do not own the module scope code path, and never
will*. Anyone who tries to sell you on the idea that they do so is simply
mistaken. Test runners that you may want to use to run your code's tests often
perform imports of arbitrary code in strange orders that manifest bugs like the
one demonstrated above. API documentation generation tools do the same. Some
people even think it's safe to use the Python ``reload`` command, or delete
objects from ``sys.modules``, each of which has hilarious effects when used
against code that has import-time side effects.

Global registry-mutating microframework programmers therefore will at some
point need to start reading the tea leaves about what *might* happen if module
scope code gets executed more than once, like we do in the previous paragraph.
When Python programmers assume they can use the module-scope code path to run
arbitrary code (especially code which populates an external registry), and this
assumption is challenged by reality, the application developer is often
required to undergo a painful, meticulous debugging process to find the root
cause of an inevitably obscure symptom. The solution is often to rearrange
application import ordering, or move an import statement from module-scope into
a function body. The rationale for doing so can never be expressed adequately
in the commit message which accompanies the fix, and can't be documented
succinctly enough for the benefit of the rest of the development team so that
the problem never happens again. It will happen again, especially if you are
working on a project with other people who haven't yet internalized the lessons
you learned while you stepped through module-scope code using ``pdb``. This is
a very poor situation in which to find yourself as an application developer:
you probably didn't even know you or your team signed up for the job, because
the documentation offered by decorator-based microframeworks don't warn you
about it.

Folks who have a large investment in eager decorator-based configuration that
populates an external data structure (such as microframework authors) may
argue that the set of circumstances I outlined above is anomalous and
contrived.  They will argue that it just will never happen.  If you never
intend your application to grow beyond one or two or three modules, that's
probably true.  However, as your codebase grows, and becomes spread across a
greater number of modules, the circumstances in which module-scope code will
be executed multiple times will become more and more likely to occur and less
and less predictable.  It's not responsible to claim that double-execution of
module-scope code will never happen.  It will; it's just a matter of luck,
time, and application complexity.

If microframework authors do admit that the circumstance isn't contrived,
they might then argue that real damage will never happen as the result of the
double-execution (or triple-execution, etc.) of module scope code.  You would
be wise to disbelieve this assertion.  The potential outcomes of multiple
execution are too numerous to predict because they involve delicate
relationships between application and framework code as well as chronology of
code execution.  It's literally impossible for a framework author to know
what will happen in all circumstances.  But even if given the gift of
omniscience for some limited set of circumstances, the framework author
almost certainly does not have the double-execution anomaly in mind when
coding new features.  They're thinking of adding a feature, not protecting
against problems that might be caused by the 1% multiple execution case.
However, any 1% case may cause 50% of your pain on a project, so it'd be nice
if it never occurred.

Responsible microframeworks actually offer a back-door way around the problem.
They allow you to disuse decorator-based configuration entirely. Instead of
requiring you to do the following:

.. code-block:: python
    :linenos:

    gh = Groundhog('myapp', 'seekrit')

    @gh.route('/foo/')
    def foo():
        return 'foo'

    if __name__ == '__main__':
        gh.run()

They allow you to disuse the decorator syntax and go almost all-imperative:

.. code-block:: python
    :linenos:

    def foo():
        return 'foo'

    gh = Groundhog('myapp', 'seekrit')

    if __name__ == '__main__':
        gh.add_route(foo, '/foo/')
        gh.run()

This is a generic mode of operation that is encouraged in the Pyramid
documentation. Some existing microframeworks (Flask, in particular) allow for
it as well.  None (other than Pyramid) *encourage* it.  If you never expect
your application to grow beyond two or three or four or ten modules, it
probably doesn't matter very much which mode you use.  If your application
grows large, however, imperative configuration can provide better
predictability.

.. note::

  Astute readers may notice that Pyramid has configuration decorators too. Aha!
  Don't these decorators have the same problems? No. These decorators do not
  populate an external Python module when they are executed. They only mutate
  the functions (and classes and methods) to which they're attached. These
  mutations must later be found during a scan process that has a predictable
  and structured import phase. Module-localized mutation is actually the
  best-case circumstance for double-imports. If a module only mutates itself
  and its contents at import time, if it is imported twice, that's OK, because
  each decorator invocation will always be mutating an independent copy of the
  object to which it's attached, not a shared resource like a registry in
  another module. This has the effect that double-registrations will never be
  performed.


.. _routes_need_ordering:

Routes need relative ordering
+++++++++++++++++++++++++++++

Consider the following simple `Groundhog
<https://github.com/Pylons/groundhog>`_ application:

.. code-block:: python
    :linenos:

    from groundhog import Groundhog
    app = Groundhog('myapp', 'seekrit')

    @app.route('/admin')
    def admin():
        return '<html>admin page</html>'

    @app.route('/:action')
    def do_action(action):
        if action == 'add':
           return '<html>add</html>'
        if action == 'delete':
           return '<html>delete</html>'
        return app.abort(404)

    if __name__ == '__main__':
        app.run()

If you run this application and visit the URL ``/admin``, you will see the
"admin" page. This is the intended result. However, what if you rearrange the
order of the function definitions in the file?

.. code-block:: python
    :linenos:

    from groundhog import Groundhog
    app = Groundhog('myapp', 'seekrit')

    @app.route('/:action')
    def do_action(action):
        if action == 'add':
           return '<html>add</html>'
        if action == 'delete':
           return '<html>delete</html>'
        return app.abort(404)

    @app.route('/admin')
    def admin():
        return '<html>admin page</html>'

    if __name__ == '__main__':
        app.run()

If you run this application and visit the URL ``/admin``, your app will now
return a 404 error. This is probably not what you intended. The reason you see
a 404 error when you rearrange function definition ordering is that routing
declarations expressed via our microframework's routing decorators have an
*ordering*, and that ordering matters.

In the first case, where we achieved the expected result, we first added a
route with the pattern ``/admin``, then we added a route with the pattern
``/:action`` by virtue of adding routing patterns via decorators at module
scope.  When a request with a ``PATH_INFO`` of ``/admin`` enters our
application, the web framework loops over each of our application's route
patterns in the order in which they were defined in our module.  As a result,
the view associated with the ``/admin`` routing pattern will be invoked because
it matches first. All is right with the world.

In the second case, where we did not achieve the expected result, we first
added a route with the pattern ``/:action``, then we added a route with the
pattern ``/admin``.  When a request with a ``PATH_INFO`` of ``/admin`` enters
our application, the web framework loops over each of our application's route
patterns in the order in which they were defined in our module.  As a result,
the view associated with the ``/:action`` routing pattern will be invoked
because it matches first. A 404 error is raised. This is not what we wanted; it
just happened due to the order in which we defined our view functions.

This is because Groundhog routes are added to the routing map in import order,
and matched in the same order when a request comes in. Bottle, like Groundhog,
as of this writing, matches routes in the order in which they're defined at
Python execution time. Flask, on the other hand, does not order route matching
based on import order. Instead it reorders the routes you add to your
application based on their "complexity". Other microframeworks have varying
strategies to do route ordering.

Your application may be small enough where route ordering will never cause an
issue. If your application becomes large enough, however, being able to specify
or predict that ordering as your application grows larger will be difficult.
At some point, you will likely need to start controlling route ordering more
explicitly, especially in applications that require extensibility.

If your microframework orders route matching based on complexity, you'll need
to understand what is meant by "complexity", and you'll need to attempt to
inject a "less complex" route to have it get matched before any "more complex"
one to ensure that it's tried first.

If your microframework orders its route matching based on relative
import/execution of function decorator definitions, you will need to ensure
that you execute all of these statements in the "right" order, and you'll need
to be cognizant of this import/execution ordering as you grow your application
or try to extend it. This is a difficult invariant to maintain for all but the
smallest applications.

In either case, your application must import the non-``__main__`` modules which
contain configuration decorations somehow for their configuration to be
executed. Does that make you a little uncomfortable? It should, because
:ref:`you_dont_own_modulescope`.

Pyramid uses neither decorator import time ordering nor does it attempt to
divine the relative complexity of one route to another as a means to define a
route match ordering. In Pyramid, you have to maintain relative route ordering
imperatively via the chronology of multiple executions of the
:meth:`pyramid.config.Configurator.add_route` method. The order in which you
repeatedly call ``add_route`` becomes the order of route matching.

If needing to maintain this imperative ordering truly bugs you, you can use
:term:`traversal` instead of route matching, which is a completely declarative
(and completely predictable) mechanism to map code to URLs. While URL dispatch
is easier to understand for small non-extensible applications, traversal is a
great fit for very large applications and applications that need to be
arbitrarily extensible.


.. _thread_local_nuisance:

"Stacked object proxies" are too clever / thread locals are a nuisance
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

Some microframeworks use the ``import`` statement to get a handle to an
object which *is not logically global*:

.. code-block:: python
    :linenos:

    from flask import request

    @app.route('/login', methods=['POST', 'GET'])
    def login():
        error = None
        if request.method == 'POST':
            if valid_login(request.form['username'],
                           request.form['password']):
                return log_the_user_in(request.form['username'])
            else:
                error = 'Invalid username/password'
        # this is executed if the request method was GET or the
        # credentials were invalid    

The `Pylons 1.X
<http://docs.pylonsproject.org/projects/pylons-webframework/en/latest/>`_
web framework uses a similar strategy.  It calls these things "Stacked Object
Proxies", so, for purposes of this discussion, I'll do so as well.

Import statements in Python (``import foo``, ``from bar import baz``) are
most frequently performed to obtain a reference to an object defined globally
within an external Python module.  However, in normal programs, they are
never used to obtain a reference to an object that has a lifetime measured by
the scope of the body of a function.  It would be absurd to try to import,
for example, a variable named ``i`` representing a loop counter defined in
the body of a function.  For example, we'd never try to import ``i`` from the
code below:

.. code-block::  python
   :linenos:

   def afunc():
       for i in range(10):
           print(i)

By its nature, the *request* object that is created as the result of a WSGI
server's call into a long-lived web framework cannot be global, because the
lifetime of a single request will be much shorter than the lifetime of the
process running the framework.  A request object created by a web framework
actually has more similarity to the ``i`` loop counter in our example above
than it has to any comparable importable object defined in the Python standard
library or in normal library code.

However, systems which use stacked object proxies promote locally scoped
objects, such as ``request``, out to module scope, for the purpose of being
able to offer users a nice spelling involving ``import``.  They, for what I
consider dubious reasons, would rather present to their users the canonical way
of getting at a ``request`` as ``from framework import request`` instead of a
saner ``from myframework.threadlocals import get_request; request =
get_request()``, even though the latter is more explicit.

It would be *most* explicit if the microframeworks did not use thread local
variables at all. Pyramid view functions are passed a request object. Many of
Pyramid's APIs require that an explicit request object be passed to them. It is
*possible* to retrieve the current Pyramid request as a threadlocal variable,
but it is an "in case of emergency, break glass" type of activity. This
explicitness makes Pyramid view functions more easily unit testable, as you
don't need to rely on the framework to manufacture suitable "dummy" request
(and other similarly-scoped) objects during test setup.  It also makes them
more likely to work on arbitrary systems, such as async servers, that do no
monkeypatching.


.. _explicitly_wsgi:

Explicitly WSGI
+++++++++++++++

Some microframeworks offer a ``run()`` method of an application object that
executes a default server configuration for easy execution.

Pyramid doesn't currently try to hide the fact that its router is a WSGI
application behind a convenience ``run()`` API.  It just tells people to
import a WSGI server and use it to serve up their Pyramid application as per
the documentation of that WSGI server.

The extra lines saved by abstracting away the serving step behind ``run()``
seems to have driven dubious second-order decisions related to its API in some
microframeworks. For example, Bottle contains a ``ServerAdapter`` subclass for
each type of WSGI server it supports via its ``app.run()`` mechanism. This
means that there exists code in ``bottle.py`` that depends on the following
modules: ``wsgiref``, ``flup``, ``paste``, ``cherrypy``, ``fapws``,
``tornado``, ``google.appengine``, ``twisted.web``, ``diesel``, ``gevent``,
``gunicorn``, ``eventlet``, and ``rocket``. You choose the kind of server you
want to run by passing its name into the ``run`` method. In theory, this sounds
great: I can try out Bottle on ``gunicorn`` just by passing in a name! However,
to fully test Bottle, all of these third-party systems must be installed and
functional. The Bottle developers must monitor changes to each of these
packages and make sure their code still interfaces properly with them. This
increases the number of packages required for testing greatly; this is a *lot*
of requirements. It is likely difficult to fully automate these tests due to
requirements conflicts and build issues.

As a result, for single-file apps, we currently don't bother to offer a
``run()`` shortcut. We tell folks to import their WSGI server of choice and run
it by hand. For the people who want a server abstraction layer, we suggest that
they use PasteDeploy.  In PasteDeploy-based systems, the onus for making sure
that the server can interface with a WSGI application is placed on the server
developer, not the web framework developer, making it more likely to be timely
and correct.

Wrapping up
+++++++++++

Here's a diagrammed version of the simplest pyramid application, where the
inlined comments take into account what we've discussed in the
:ref:`microframeworks_smaller_hello_world` section.

.. code-block:: python
   :linenos:

   from pyramid.response import Response # explicit response, no thread local
   from wsgiref.simple_server import make_server # explicitly WSGI

   def hello_world(request):  # accepts a request; no request thread local reqd
       # explicit response object means no response threadlocal
       return Response('Hello world!')

   if __name__ == '__main__':
       from pyramid.config import Configurator
       config = Configurator()       # no global application object
       config.add_view(hello_world)  # explicit non-decorator registration
       app = config.make_wsgi_app()  # explicitly WSGI
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()        # explicitly WSGI


Pyramid doesn't offer pluggable apps
------------------------------------

It is "Pyramidic" to compose multiple external sources into the same
configuration using :meth:`~pyramid.config.Configurator.include`.  Any
number of includes can be done to compose an application; includes can even
be done from within other includes.  Any directive can be used within an
include that can be used outside of one (such as
:meth:`~pyramid.config.Configurator.add_view`).

Pyramid has a conflict detection system that will throw an error if two
included externals try to add the same configuration in a conflicting way
(such as both externals trying to add a route using the same name, or both
externals trying to add a view with the same set of predicates).  It's awful
tempting to call this set of features something that can be used to compose a
system out of "pluggable applications".  But in reality, there are a number
of problems with claiming this:

- The terminology is strained. Pyramid really has no notion of a 
  plurality of "applications", just a way to compose configuration 
  from multiple sources to create a single WSGI application.  That 
  WSGI application may gain behavior by including or disincluding 
  configuration, but once it's all composed together, Pyramid 
  doesn't really provide any machinery which can be used to demarcate 
  the boundaries of one "application" (in the sense of configuration 
  from an external that adds routes, views, etc) from another. 

- Pyramid doesn't provide enough "rails" to make it possible to integrate
  truly honest-to-god, download-an-app-from-a-random-place
  and-plug-it-in-to-create-a-system "pluggable" applications.  Because
  Pyramid itself isn't opinionated (it doesn't mandate a particular kind of
  database, it offers multiple ways to map URLs to code, etc), it's unlikely
  that someone who creates something application-like will be able to
  casually redistribute it to J. Random Pyramid User and have it just work by
  asking him to config.include a function from the package.  This is
  particularly true of very high level components such as blogs, wikis,
  twitter clones, commenting systems, etc.  The integrator (the Pyramid
  developer who has downloaded a package advertised as a "pluggable app")
  will almost certainly have made different choices about e.g. what type of
  persistence system he's using, and for the integrator to appease the
  requirements of the "pluggable application", he may be required to set up a
  different database, make changes to his own code to prevent his application
  from shadowing the pluggable app (or vice versa), and any other number of
  arbitrary changes.

For this reason, we claim that Pyramid has "extensible" applications, 
not pluggable applications.  Any Pyramid application can be extended 
without forking it as long as its configuration statements have been 
composed into things that can be pulled in via ``config.include``. 

It's also perfectly reasonable for a single developer or team to create a set
of interoperating components which can be enabled or disabled by using
config.include.  That developer or team will be able to provide the "rails"
(by way of making high-level choices about the technology used to create the
project, so there won't be any issues with plugging all of the components
together.  The problem only rears its head when the components need to be
distributed to *arbitrary* users.  Note that Django has a similar problem
with "pluggable applications" that need to work for arbitrary third parties,
even though they provide many, many more rails than does Pyramid.  Even the
rails they provide are not enough to make the "pluggable application" story
really work without local modification.

Truly pluggable applications need to be created at a much higher level than a
web framework, as no web framework can offer enough constraints to really
make them work out of the box.  They really need to plug into an application,
instead.  It would be a noble goal to build an application with Pyramid that
provides these constraints and which truly does offer a way to plug in
applications (Joomla, Plone, Drupal come to mind).

Pyramid Has Zope Things In It, So It's Too Complex
--------------------------------------------------

On occasion, someone will feel compelled to post a mailing list message that
reads something like this:

.. code-block:: text

   had a quick look at pyramid ... too complex to me and not really
   understand for which benefits.. I feel should consider whether it's time
   for me to step back to django .. I always hated zope (useless ?)
   complexity and I love simple way of thinking

(Paraphrased from a real email, actually.)

Let's take this criticism point-by-point.

Too Complex
+++++++++++

If you can understand this hello world program, you can use Pyramid:

.. code-block:: python
   :linenos:

   from wsgiref.simple_server import make_server
   from pyramid.config import Configurator
   from pyramid.response import Response

   def hello_world(request):
       return Response('Hello world!')

   if __name__ == '__main__':
       config = Configurator()
       config.add_view(hello_world)
       app = config.make_wsgi_app()
       server = make_server('0.0.0.0', 8080, app)
       server.serve_forever()

Pyramid has over 1200 pages of documentation (printed), covering topics from
the very basic to the most advanced. *Nothing* is left undocumented, quite
literally.  It also has an *awesome*, very helpful community.  Visit the
`#pyramid IRC channel on freenode.net
<https://webchat.freenode.net/?channels=pyramid>`_ and see.

Hate Zope
+++++++++

I'm sorry you feel that way.  The Zope brand has certainly taken its share of
lumps over the years, and has a reputation for being insular and mysterious.
But the word "Zope" is literally quite meaningless without qualification.
What *part* of Zope do you hate?  "Zope" is a brand, not a technology.

If it's Zope2-the-web-framework, Pyramid is not that.  The primary designers
and developers of Pyramid, if anyone, should know.  We wrote Pyramid's
predecessor (:mod:`repoze.bfg`), in part, because *we* knew that Zope 2 had
usability issues and limitations.  :mod:`repoze.bfg` (and now :app:`Pyramid`)
was written to address these issues.

If it's Zope3-the-web-framework, Pyramid is *definitely* not that.  Making
use of lots of Zope 3 technologies is territory already staked out by the
:term:`Grok` project.  Save for the obvious fact that they're both web
frameworks, :app:`Pyramid` is very, very different than Grok.  Grok exposes
lots of Zope technologies to end users.  On the other hand, if you need to
understand a Zope-only concept while using Pyramid, then we've failed on some
very basic axis.

If it's just the word Zope: this can only be guilt by association.  Because a
piece of software internally uses some package named ``zope.foo``, it doesn't
turn the piece of software that uses it into "Zope".  There is a lot of
*great* software written that has the word Zope in its name.  Zope is not
some sort of monolithic thing, and a lot of its software is usable
externally.  And while it's not really the job of this document to defend it,
Zope has been around for over 10 years and has an incredibly large, active
community.  If you don't believe this,
http://pypi-ranking.info/author is an eye-opening reality
check.

Love Simplicity
+++++++++++++++

Years of effort have gone into honing this package and its documentation to
make it as simple as humanly possible for developers to use.  Everything is a
tradeoff, of course, and people have their own ideas about what "simple" is.
You may have a style difference if you believe Pyramid is complex.  Its
developers obviously disagree.

Other Challenges
----------------

Other challenges are encouraged to be sent to the `Pylons-devel
<https://groups.google.com/forum/#!forum/pylons-devel>`_ maillist.  We'll try
to address them by considering a design change, or at very least via exposition
here.
