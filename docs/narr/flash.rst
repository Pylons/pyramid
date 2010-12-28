.. _flash_chapter:

Flash Messages
==============

"Flash messages" are simply a queue of message strings stored in the
:term:`session`.  To use flash messaging, you must enable a :term:`session
factory` as described in :ref:`using_the_default_session_factory` or
:ref:`using_alternate_session_factories`.

Flash messaging has two main uses: to display a status message only once to
the user after performing an internal redirect, and to allow generic code to
log messages for single-time display without having direct access to an HTML
template. The user interface consists of a number of methods of the
:term:`session` object.

Using the ``session.flash`` Method
----------------------------------

To add a message to a flash message queue, use a session object's ``flash``
method:

.. code-block:: python
   :linenos:

   request.session.flash('mymessage')

The ``.flash`` method appends a message to a flash queue, creating the queue
if necessary. 

``.flash`` accepts three arguments:

.. method:: flash(message, queue='', allow_duplicate=True)

The ``message`` argument is required.  It represents a message you wish to
later display to a user.  It is usually a string but the ``message`` you
provide is not modified in any way.

The ``queue`` argument allows you to choose a queue to which to append the
message you provide.  This can be used to push different kinds of messages
into flash storage for later display in different places on a page.  You can
pass any name for your queue, but it must be a string. The default value is
the empty string, which chooses the default queue. Each queue is independent,
and can be popped by ``pop_flash`` or examined via ``peek_flash`` separately.
``queue`` defaults to the empty string.  The empty string represents the
default flash message queue.

.. code-block:: python

   request.session.flash(msg, 'myappsqueue')

The ``allow_duplicate`` argument, which defaults to ``True``.  If this is
``False``, if you attempt to add a message to a queue which is already
present in the queue, it will not be added.

Using the ``session.pop_flash`` Method
--------------------------------------

Once one or more messages has been added to a flash queue by the
``session.flash`` API, the ``session.pop_flash`` API can be used to pop that
queue and return it for use.

To pop a particular queue of messages from the flash object, use the session
object's ``pop_flash`` method.

.. code-block:: python
   :linenos:

   >>> request.session.flash('info message')
   >>> request.session.pop_flash()
   ['info message']

Calling ``session.pop_flash()`` again like above without a corresponding call
to ``session.flash`` will return an empty list, because the queue has already
been popped.

.. code-block:: python
   :linenos:

   >>> request.session.flash('info message')
   >>> request.session.pop_flash()
   ['info message']
   >>> request.session.pop_flash()
   []

The object returned from ``pop_flash`` is a list.

Using the ``session.pop_flash`` Method
--------------------------------------

Once one or more messages has been added to a flash queue by the
``session.flash`` API, the ``session.peek_flash`` API can be used to "peek"
at that queue.  Unlike ``session.pop_flash``, the queue is not popped from
flash storage.

.. code-block:: python
   :linenos:

   >>> request.session.flash('info message')
   >>> request.session.peek_flash()
   ['info message']
   >>> request.session.peek_flash()
   ['info message']
   >>> request.session.pop_flash()
   ['info message']
   >>> request.session.peek_flash()
   []
