.. index::
   single: Bicking, Ian
   single: WebOb

.. _webob_chapter:

Request and Response Objects
============================

.. note:: This chapter is adapted from a portion of the :term:`WebOb`
   documentation, originally written by Ian Bicking.

:mod:`repoze.bfg` uses the :term:`WebOb` package to supply
:term:`request` and :term:`response` object implementations.  The
:term:`request` object that is passed to a :mod:`repoze.bfg`
:term:`view` is an instance of the :class:`repoze.bfg.Request` class,
which is a subclass of :class:`webob.Request`.  The :term:`response`
returned from a :mod:`repoze.bfg` :term:`view` :term:`renderer` is an
instance of the :mod:`webob.Response` class.  Users can also return an
instance of :mod:`webob.Response` directly from a view as necessary.

WebOb is a project separate from :mod:`repoze.bfg` with a separate set
of authors and a fully separate `set of documentation
<http://pythonpaste.org/webob/>`_.

.. warning:: The following information is only an overview of the
   request and response objects provided by :term:`WebOb`.  See the
   `reference documentation
   <http://pythonpaste.org/webob/reference.html>`_ for more detailed
   API reference information.  All methods in the :term:`WebOb`
   documentation work against :mod:`repoze.bfg` requests and
   responses.

WebOb provides objects for HTTP requests and responses.  Specifically
it does this by wrapping the `WSGI <http://wsgi.org>`_ request
environment and response status/headers/app_iter(body).

The request and response objects provide many conveniences for parsing
HTTP request and forming HTTP responses.  Both objects are read/write:
as a result, WebOb is also a nice way to create HTTP requests and
parse HTTP responses; however, we won't cover that use case in this
document.  The `reference documentation
<http://pythonpaste.org/webob/reference.html>`_ shows many examples of
creating requests.

.. index::
   single: request object
   single: request attributes

Request
~~~~~~~

The request object is a wrapper around the `WSGI environ dictionary
<http://www.python.org/dev/peps/pep-0333/#environ-variables>`_.  This
dictionary contains keys for each header, keys that describe the
request (including the path and query string), a file-like object for
the request body, and a variety of custom keys.  You can always access
the environ with ``req.environ``.

Some of the most important/interesting attributes of a request
object:

``req.method``:
    The request method, e.g., ``'GET'``, ``'POST'``

``req.GET``:
    A :term:`multidict` with all the variables in the query
    string.

``req.POST``:
    A :term:`multidict` with all the variables in the request
    body.  This only has variables if the request was a ``POST`` and
    it is a form submission.  

``req.params``:
    A :term:`multidict` with a combination of everything in
    ``req.GET`` and ``req.POST``.

``req.body``:
    The contents of the body of the request.  This contains the entire
    request body as a string.  This is useful when the request is a
    ``POST`` that is *not* a form submission, or a request like a
    ``PUT``.  You can also get ``req.body_file`` for a file-like
    object.

``req.cookies``:
    A simple dictionary of all the cookies.

``req.headers``:
    A dictionary of all the headers.  This dictionary is case-insensitive.

``req.urlvars`` and ``req.urlargs``:
    ``req.urlvars`` are the keyword parameters associated with the
    request URL.  ``req.urlargs`` are the positional parameters.
    These are set by products like `Routes
    <http://routes.groovie.org/>`_ and `Selector
    <http://lukearno.com/projects/selector/>`_.

Also, for standard HTTP request headers there are usually attributes,
for instance: ``req.accept_language``, ``req.content_length``,
``req.user_agent``, as an example.  These properties expose the
*parsed* form of each header, for whatever parsing makes sense.  For
instance, ``req.if_modified_since`` returns a `datetime
<http://python.org/doc/current/lib/datetime-datetime.html>`_ object
(or None if the header is was not provided).  Details are in the
`Request reference
<http://pythonpaste.org/webob/class-webob.Request.html>`_.

.. index::
   single: request attributes (special)

.. _special_request_attributes:

Special Attributes Added to the Request by :mod:`repoze.bfg`
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

In addition to the standard :term:`WebOb` attributes,
:mod:`repoze.bfg` adds the following special attributes to every
request.

``req.context``
  The :term:`context` will be available as the ``context`` attribute
  of the :term:`request` object.  It will be the context object
  implied by the current request.  See :ref:`traversal_chapter` for
  information about context objects.

``req.registry``
  The :term:`application registry` will be available as
  the ``registry`` attribute of the :term:`request` object.  See
  :ref:`zca_chapter` for more information about the application
  registry.

``req.root``
  The :term:`root` object will be available as the ``root`` attribute
  of the :term:`request` object.  It will be the model object at which
  traversal started (the root).  See :ref:`traversal_chapter` for
  information about root objects.

``req.subpath``
  The traversal :term:`subpath` will be available as the ``subpath``
  attribute of the :term:`request` object.  It will be a sequence
  containing zero or more elements (which will be Unicode objects).
  See :ref:`traversal_chapter` for information about the subpath.

``req.traversed``
  The "traversal path" will be available as the ``traversed`` attribute of the
  :term:`request` object.  It will be a sequence representing the
  ordered set of names that were used to traverse to the
  :term:`context`, not including the view name or subpath.  If there
  is a virtual root associated with the request, the virtual root path is
  included within the traversal path.  See :ref:`traversal_chapter`
  for more information.

``req.view_name``
  The :term:`view name` will be available as the ``view_name``
  attribute of the :term:`request` object.  It will be a single string
  (possibly the empty string if we're rendering a default view).
  See :ref:`traversal_chapter` for information about view names.

``req.virtual_root``
  The :term:`virtual root` will be available as the ``virtual_root``
  attribute of the :term:`request` object.  It will be the virtual
  root object implied by the current request.  See
  :ref:`vhosting_chapter` for more information about virtual roots.

``req.virtual_root_path``
  The :term:`virtual root` *path* will be available as the
  ``virtual_root_path`` attribute of the :term:`request` object.  It
  will be a sequence representing the ordered set of names that were
  used to traverse to the virtual root object.  See
  :ref:`vhosting_chapter` for more information about virtual roots.

.. index::
   single: request URLs

URLs
++++

In addition to these attributes, there are several ways to get the URL
of the request.  I'll show various values for an example URL
``http://localhost/app/?id=10``, where the application is mounted at
``http://localhost/app``.

``req.url``:
    The full request URL, with query string, e.g.,
    ``http://localhost/app/?id=10``

``req.application_url``:
    The URL of the application (just the SCRIPT_NAME portion of the
    path, not PATH_INFO).  E.g., ``http://localhost/app``

``req.host_url``:
    The URL with the host, e.g., ``http://localhost``

``req.relative_url(url, to_application=False)``:
    Gives a URL, relative to the current URL.  If ``to_application``
    is True, then resolves it relative to ``req.application_url``.

.. index::
   single: request methods

Methods
+++++++

There are `several methods
<http://pythonpaste.org/webob/class-webob.Request.html#__init__>`_ but
only a few you'll use often:

``Request.blank(base_url)``:
    Creates a new request with blank information, based at the given
    URL.  This can be useful for subrequests and artificial requests.
    You can also use ``req.copy()`` to copy an existing request, or
    for subrequests ``req.copy_get()`` which copies the request but
    always turns it into a GET (which is safer to share for
    subrequests).

``req.get_response(wsgi_application)``:
    This method calls the given WSGI application with this request,
    and returns a `Response`_ object.  You can also use this for
    subrequests or testing.

.. index::
   single: request (and unicode)
   single: unicode (and the request)

Unicode
+++++++

Many of the properties in the request object will return unicode
values if the request encoding/charset is provided.  The client *can*
indicate the charset with something like ``Content-Type:
application/x-www-form-urlencoded; charset=utf8``, but browsers seldom
set this.  You can set the charset with ``req.charset = 'utf8'``, or
during instantiation with ``Request(environ, charset='utf8')``.  If
you subclass ``Request`` you can also set ``charset`` as a class-level
attribute.

If it is set, then ``req.POST``, ``req.GET``, ``req.params``, and
``req.cookies`` will contain unicode strings.  Each has a
corresponding ``req.str_*`` (like ``req.str_POST``) that is always
``str`` and never unicode.

.. index::
   single: response object

Response
~~~~~~~~

The response object looks a lot like the request object, though with
some differences.  The request object wraps a single ``environ``
object; the response object has three fundamental parts (based on
WSGI):

``response.status``:
    The response code plus message, like ``'200 OK'``.  To set the
    code without the reason, use ``response.status_int = 200``.

``response.headerlist``:
    A list of all the headers, like ``[('Content-Type',
    'text/html')]``.  There's a case-insensitive :term:`multidict`
    in ``response.headers`` that also allows you to access
    these same headers.

``response.app_iter``:
    An iterable (such as a list or generator) that will produce the
    content of the response.  This is also accessible as
    ``response.body`` (a string), ``response.unicode_body`` (a
    unicode object, informed by ``response.charset``), and
    ``response.body_file`` (a file-like object; writing to it appends
    to ``app_iter``).

Everything else in the object derives from this underlying state.
Here's the highlights:

``response.content_type``:
    The content type *not* including the ``charset`` parameter.
    Typical use: ``response.content_type = 'text/html'``.  You can
    subclass ``Response`` and add a class-level attribute
    ``default_content_type`` to set this automatically on
    instantiation.

``response.charset``:
    The ``charset`` parameter of the content-type, it also informs
    encoding in ``response.unicode_body``.
    ``response.content_type_params`` is a dictionary of all the
    parameters.

``response.request``:
    This optional attribute can point to the request object associated
    with this response object.

``response.set_cookie(key, value, max_age=None, path='/', ...)``: 
    Set a cookie.  The keyword arguments control the various cookie
    parameters.  The ``max_age`` argument is the length for the cookie
    to live in seconds (you may also use a timedelta object).  The
    ``Expires`` key will also be set based on the value of
    ``max_age``.

``response.delete_cookie(key, path='/', domain=None)``:
    Delete a cookie from the client.  This sets ``max_age`` to 0 and
    the cookie value to ``''``.

``response.cache_expires(seconds=0)``:
    This makes this response cacheable for the given number of seconds,
    or if ``seconds`` is 0 then the response is uncacheable (this also
    sets the ``Expires`` header).

``response(environ, start_response)``: 
    The response object is a WSGI application.  As an application, it
    acts according to how you create it.  It *can* do conditional
    responses if you pass ``conditional_response=True`` when
    instantiating (or set that attribute later).  It can also do HEAD
    and Range requests.

.. index::
   single: response headers

Headers
+++++++

Like the request, most HTTP response headers are available as
properties.  These are parsed, so you can do things like
``response.last_modified = os.path.getmtime(filename)``.

The details are available in the `extracted Response documentation
<http://pythonpaste.org/webob/class-webob.Response.html>`_.

.. index::
   single: response (creating)

Instantiating the Response
++++++++++++++++++++++++++

Of course most of the time you just want to *make* a response.  
Generally any attribute of the response can be passed in as a keyword
argument to the class; e.g.:

.. code-block:: python

  from webob import Response

  response = Response(body='hello world!', content_type='text/plain')

The status defaults to ``'200 OK'``.  The content_type does not
default to anything, though if you subclass ``Response`` and set
``default_content_type`` you can override this behavior.

.. index::
   single: response exceptions

Exceptions
++++++++++

To facilitate error responses like 404 Not Found, the module
``webob.exc`` contains classes for each kind of error response.  These
include boring but appropriate error bodies.

Each class is named ``webob.exc.HTTP*``, where ``*`` is the reason for
the error.  For instance, ``webob.exc.HTTPNotFound``.  It subclasses
``Response``, so you can manipulate the instances in the same way.  A
typical example is:

.. ignore-next-block
.. code-block:: python

    from webob.exc import HTTPNotFound
    from webob.exc import HTTPMovedPermanently

    response = HTTPNotFound('There is no such resource')
    # or:
    response = HTTPMovedPermanently(location=new_url)

These are not exceptions unless you are using Python 2.5+, because
they are new-style classes which are not allowed as exceptions until
Python 2.5.  To get an exception object use ``response.exception``.
You can use this like:

.. code-block:: python
   :linenos:

   from webob.exc import HTTPException
   from webob.exc import HTTPNotFound

   def aview(request):
       try:
           # ... stuff ...
           raise HTTPNotFound('No such resource').exception
       except HTTPException, e:
           return request.get_response(e)

The exceptions are still WSGI applications, but you cannot set
attributes like ``content_type``, ``charset``, etc. on these exception
objects.

.. index::
   single: multidict (WebOb)

Multidict
~~~~~~~~~

Several parts of WebOb use a "multidict"; this is a dictionary where a
key can have multiple values.  The quintessential example is a query
string like ``?pref=red&pref=blue``; the ``pref`` variable has two
values: ``red`` and ``blue``.

In a multidict, when you do ``request.GET['pref']`` you'll get back
only ``'blue'`` (the last value of ``pref``).  Sometimes returning a
string, and sometimes returning a list, is the cause of frequent
exceptions.  If you want *all* the values back, use
``request.GET.getall('pref')``.  If you want to be sure there is *one
and only one* value, use ``request.GET.getone('pref')``, which will
raise an exception if there is zero or more than one value for
``pref``.

When you use operations like ``request.GET.items()`` you'll get back
something like ``[('pref', 'red'), ('pref', 'blue')]``.  All the
key/value pairs will show up.  Similarly ``request.GET.keys()``
returns ``['pref', 'pref']``.  Multidict is a view on a list of
tuples; all the keys are ordered, and all the values are ordered.

