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
:mod:`repoze.bfg`.

Making framework developers and extenders understand the ZCA is a
tradeoff.  We (the :mod:`repoze.bfg` developers) like the features
that the ZCA gives us, and we have long-ago borne the weight of
understanding what it does and how it works.  The authors of
:mod:`repoze.bfg` understand the ZCA deeply and can read code that
uses it as easily as any other code.

However, we do recognize that other developers who my want to extend
the framework are not as comfortable with ZCA we are with it.  So, for
the purposes of being kind to framework developers who may be dismayed
by some of the more flagrant uses of the ZCA API in :mod:`repoze.bfg`,
we've turned the component registry used in BFG into something that is
accessible using the plain old dictionary API (like the
:mod:`repoze.component` API).  Our example in the problem section
above was:

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

We continued using ZCA rather than disusing it in favor of
:mod:`repoze.component` largely because the ZCA concept of interfaces
provides for use of an interface hierarchy, which is useful in a lot
of scenarios (such as context type inheritance).  Coming up with a
marker type that was something like an interface that allowed for this
functionality seemed like it was just reinventing the wheel.

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

BFG "Encourages Use of ZCML"
----------------------------

:term:`ZCML` is a configuration language that can be used to configure
the :term:`Zope Component Architecture` registry that BFG uses as its
application configuration.

Quick answer: well, no, it doesn't.. not really.  You can use the
``bfg_view`` decorator for the most common form of configuration.
But, yes, your application currently does need to possess a ZCML file
for it to begin executing successfully even if its only contents are a
``<scan>`` directive that kicks off the location of decorated views.

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

In this mode, no ZCML will be required.  Hopefully this mode will
allow people who are used to doing everything imperatively feel more
comfortable.

Other Topics
------------

We'll be trying to cover the following in this document as time allows:

- BFG View Lookup and Registration Is "Complex"

- BFG Template Lookup Is "Complex"

- BFG Views Do Not Accept Arbitrary Keyword Arguments

- BFG Does Traversal, And I Don't Like Traversal

- BFG Does URL Dispatch, And I Don't Like URL Dispatch

Other challenges are encouraged to be sent to the `Repoze-Dev
<http://lists.repoze.org/listinfo/repoze-dev>`_ maillist.  We'll try
to address them by considering a design change, or at very least via
exposition here.
