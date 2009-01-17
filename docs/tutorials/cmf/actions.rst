.. _actions_chapter:

=======
Actions
=======

In CMF, the "actions tool" along with "action providers" create an
extensible mechanism to show links in the CMF management UI that
invoke a particular behavior or which show a particular template.

:mod:`repoze.bfg` itself has no such concept, and no package provides
a direct replacement.  Actions are such a generic concept that it's
simple to reimplement action-like navigation in a different way within
any given application.  For example, a module-scope global dictionary
which has keys that are action names, and values which are tuples of
(permission, link).  Take that concept and expand on it, and you'll
have some passable actions tool replacement within a single application.

The `repoze.bfg.viewgroup
<http://svn.repoze.org/repoze.bfg.viewgroup/trunk/>`_ package provides
some functionality for creating "view groups".  Each view in a
viewgroup can provide some snippet of HTML (e.g. a single "tab"), and
individual views (tabs) within the group which cannot be displayed to
the user due to the user's lack of permissions will be omitted from
the rendered output.

The :term:`repoze.lemonade` package provides "list item" support that
may be used to construct action lists.

