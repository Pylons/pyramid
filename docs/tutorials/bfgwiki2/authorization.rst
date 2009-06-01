====================
Adding Authorization
====================

Our application currently allows anyone with access to the server to
view, edit, and add pages to our wiki.  For purposes of demonstration
we'll change our application to allow people whom possess a specific
username (`editor`) to add and edit wiki pages but we'll continue
allowing anyone with access to the server to view pages.
:mod:`repoze.bfg` provides facilities for *authorization* and
*authentication*.  We'll make use of both features to provide security
to our application.

XXX not finished

