Author Introduction
===================

This is the "author introduction", wherein, I, the author put stuff
that goes nowhere else.

The Genesis of :mod:`repoze.bfg`
--------------------------------

I wrote :mod:`repoze.bfg` after many years of writing applications
using :term:`Zope`.  Zope provided me with a lot of mileage: it wasn't
until almost a decade of succesfully creating applications using Zope
that I decided to write a different web framework.  Although
:mod:`repoze.bfg` takes inspiration from a variety of web frameworks,
it owes more of its design ethos to Zope than any other.

The "Repoze" brand existed before :mod:`repoze.bfg`.  One of the first
packages developed as part of the Repoze brand was a package named
:mod:`repoze.zope2`.  This was a package that allowed Zope 2
applications to run under a :term:`WSGI` server without modification.
Zope 2 did not have reasonable WSGI support at the time.

During the development of the :mod:`repoze.zope2` package, I found
that replicating the Zope 2 "publisher" -- the machinery that maps
URLs to code -- was time-consuming and fiddly.  Zope 2 had evolved
over many years, and emulating all of its edge cases was extremely
difficult.  I finished the :mod:`repoze.zope2` package, and it
emulates the normal Zope 2 publisher pretty well.  But during its
development, it became clear that Zope 2 had simply begun to exceed my
tolerance for complexity, and I began to look around for simpler
options.

I considered the using Zope 3 application server machinery, but it
turned out that it had become more indirect than the Zope 2 machinery
it aimed to replace, which didn't fulfill the goal of simplification.
I also considered using Django and Pylons, but neither of those
frameworks offer much along the axes of traversal, contextual
declarative security, or application extensibility; these were
features I had become accustomed to as a Zope developer.

I decided that in the long term, creating a simpler, legacy-free
framework that retained features I had become accustomed to when
developing Zope applications was a more reasonable idea than
continuing to use any Zope publisher or living with the limitations
and unfamiliarities of a different framework.  The result is what is
now :mod:`repoze.bfg`.

Thanks
------

This book is dedicated to my grandmother, Dorothy Phillips.

Thanks to the following people for providing expertise, resources, and
software.  Without the help of these folks, neither this book nor the
software which it details would exist: Paul Everitt, Tres Seaver,
Andrew Sawyers, Malthe Borch, Carlos de la Guardia, Georg Brandl,
Simon Oram of Electrosoup, Ian Bicking of the Open Planning Project,
Jim Fulton of Zope Corporation, Tom Moroz of the Open Society
Institute, and Todd Koym of Environmental Health Sciences.

Special thanks to Guido van Rossum and Tim Peters for Python.

Special thanks also to Tricia for putting up with me.

