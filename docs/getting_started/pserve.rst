===================================
Application Running With ``pserve``
===================================


Three Cool Things About ``pserve``
----------------------------------

1. *Multiple .ini files*. You might have some settings in
   development mode or some in production mode. Maybe you are writing an
   add-on that needs to be wired-up by other people.

2. *Choice of WSGI server*. ``pserve`` itself isn't a WSGI server.
   Instead, it loads the server you want from the configuration file.

3. *Friends of pserve*. With the ``pserve``/``.ini`` approach you
   also get other commands that help during development: ``pshell``,
   ``proutes``, ``pviews``, ``prequest``, etc.
