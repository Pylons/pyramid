Errata for "The repoze.bfg Web Framework, Version 1.2" Printed Edition
======================================================================

pp. 350
-------

The sentence:

  Note in the call to SessionDataManager that '3600' represents the
  disuse timeout (5 minutes == 3600 seconds), and '5' represents a
  write granularity time (the session will be marked as active at most
  every five seconds).

Should read:

  Note in the call to SessionDataManager that '3600' represents the
  disuse timeout (60 minutes == 3600 seconds), and '5' represents a
  write granularity time (the session will be marked as active at most
  every five seconds).
