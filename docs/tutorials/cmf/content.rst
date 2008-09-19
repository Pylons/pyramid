.. _content_types_chapter:

=============
Content Types
=============

In CMF, a content type is defined as a bag of settings (the type
information, controlled within the "types tool"), as well as factory
code which generates an instance of that content.  It is possible to
construct and enumerate content types using APIs defined on the types
tool.

:mod:`repoze.bfg` itself has no such concept, but an addon package named
:term:`repoze.lemonade` has a barebones replacement.

Factory Type Information
------------------------

A factory type information object in CMF allows you to associate a
title, a description, an internationalization domain, an icon, an
initial view name, a factory, and a number of security settings with a
type name.  Each type information object knows how to manufacture
content objects that match its type.

:mod:`repoze.bfg` certainly enforces none of these concepts in any
particular way, but :term:`repoze.lemonade` does.

``repoze.lemonade`` Content
+++++++++++++++++++++++++++

:term:`repoze.lemonade` provides a reasonably handy directive and set
of helper functions which allow you to:

#. Associate a interface with a factory function, making it into a
   "content type".

#. Enumerate all interfaces associated with factory functions.

.. note:: Using this pattern is often plain silly, as it's usually
          just as easy to actually import a class implementation and
          create an instance directly using its constructor.  But it
          can be useful in cases where you want to address some set of
          constructors uniformly without doing direct imports in the
          code which performs the construction, or if you need to make
          content construction uniform across a diverse set of model
          types, or if you need to enumerate some set of information
          about "content" types.  It's left as an exercise to the
          reader to determine under which circumstances using this
          pattern is an appropriate thing to do.  Hint: not very
          often, unless you're doing the indirection solely to aid
          content-agnostic unit tests or if you need to get an
          enumerated subset of content type information to aid in UI
          generation.  That said, this *is* a tutorial about how to
          get CMF-like features in :mod:`repoze.bfg`, so we'll assume
          the pattern is useful to readers.

See the `repoze.lemonade package
<http://svn.repoze.org/repoze.lemonade/trunk>`_ for more information,
particularly its documentation for "content".








