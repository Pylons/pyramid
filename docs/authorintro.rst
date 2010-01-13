Author Introduction
===================

Welcome to "The :mod:`repoze.bfg` Web Application Framework".  In this
introduction, I'll describe the audience for this book, I'll provide
some context regarding the genesis of :mod:`repoze.bfg`, and I'll
thank some important people.

I hope you enjoy both this book and the software it documents.  I've
had a blast writing both.

Audience
--------

This book is aimed primarily at a reader that has the following
attributes:

- At least a moderate amount of :term:`Python` experience.

- A familiarity with web protocols such as HTTP and CGI.

If you fit into both of these categories, you're in the direct target
audience for this book.  But don't worry, even if you have no
experience with Python or the web, both are easy to pick up "on the
fly".

Python is an *excellent* language in which to write applications;
becoming productive in Python is almost mind-blowingly easy.  If you
already have experience in another language such as Java, Visual
Basic, Perl, Ruby, or even C/C++, learning Python will be a snap; it
should take you no longer than a couple of days to become modestly
productive.  If you don't have previous programming experience, it
will be slightly harder, and it will take a little longer, but you'd
be hard-pressed to find a better "first language."

Web technology familiarity is assumed in various places within the
book.  For example, the book describes various interactions in terms
of the HTTP protocol, but it does not describe how the HTTP protocol
works in detail.  Like any good framework, though, :mod:`repoze.bfg`
shields you from needing to know the gory details of web protocols
such as HTTP, and you can usually skip such descriptions without
becoming "blocked," although you may lack some fundamental
understanding of how it works "under the hood" as a result.

The Genesis of :mod:`repoze.bfg`
--------------------------------

I wrote :mod:`repoze.bfg` after many years of writing applications
using :term:`Zope`.  Zope provided me with a lot of mileage: it wasn't
until almost a decade of succesfully creating applications using Zope
that I decided to write a different web framework.  Although
:mod:`repoze.bfg` takes inspiration from a variety of web frameworks,
it owes more of its core design to Zope than any other.

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

It is immodest to say so, but I believe :mod:`repoze.bfg` has turned
out to be the very best Python web framework available today, bar
none.  It combines all the "good parts" from other web frameworks into
a cohesive whole that is reliable, down-to-earth, flexible, speedy,
and well-documented.

Thanks
------

This book is dedicated to my grandmother, Dorothy Phillips, who gave
me my first typewriter, and my mother, Donelle Duffy, who bought me my
first computer (a VIC-20).

Thanks to the following people for providing expertise, resources, and
software.  Without the help of these folks, neither this book nor the
software which it details would exist: Paul Everitt, Tres Seaver,
Andrew Sawyers, Malthe Borch, Carlos de la Guardia, Georg Brandl,
Simon Oram of Electrosoup, Ian Bicking of the Open Planning Project,
Jim Fulton of Zope Corporation, Tom Moroz of the Open Society
Institute, and Todd Koym of Environmental Health Sciences.

Special thanks to Guido van Rossum and Tim Peters for Python.

Special thanks also to Tricia for putting up with me.
