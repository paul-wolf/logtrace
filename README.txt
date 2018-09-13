LogTrace
========

|Build Status|

Aggregate messages to produce a log entry representing a single event or
procedure. The purpose of this module is to easily asssociate log
messages together that belong together.

::

    import logging
    from logtrace import LogTrace

    logger = logging.getLogger(__name__)
    trace = LogTrace(logger=logger)

    trace.add("Let's get started")
    ...
    trace.add("Later, something else happens")
    ...
    trace.add("And finally...")

    trace.emit()

You get a single log entry like this:

::

    [05/Jan/2018 11:11:00] DEBUG [21, .30s] Let's get started; [65, .132s] Later, something else happens; [75, .330s] And finally...

Install
-------

::

    pip install logtrace

Note that this only suppports Python 3. Let me know if anyone wants
support for Python 2. There are no dependencies outside the Python
Standard Library for this module.

Example
-------

Logs can be hard to read because you have cases where you log
information as you go through a procedure. These log entries get
scattered with all the other logs from other processes. You end up
having to search for related entries possibly implanting identifying
information in each one to tie them together. ``LogTrace`` fixes this
problem by letting you collect logs and then output once. Take the
example of a token authentication procedure where transient tokens are
required to be authenticated. You want to record the following events:

-  Check the HTTP header info with the token
-  What table are we going to use to check the token?
-  Did the token service authenticate the token?
-  Is the token in a local cache?
-  Successfully authenticated?

The following records five separate instances where you would have
called ``logger.info()`` with a line number and the time in seconds
since constructing the ``LogTrace`` object ``[<lineno>, <secs>s]``:

::

    [12:12:54] INFO [132, 0.0006s] auth header: [b'Token', b'2c59999137******************************']; [132, 0.0007s] authenticate key, model: <class 'tastypie.models.ApiKey'>; [132, 0.1057s] token renewal for API call confirmed; [132, 0.1078s] got key from token table: paul; [163, 0.1079s] Successfully authenticated

Details
-------

We respect logging levels. So, the overhead of using LogTrace is minimal
if your log level is not effective. If your log level is
``logging.INFO`` and you call ``logtrace.emit_debug()``, almost all
overhead is avoided minus some function call overhead and one or two
conditional expressions.

What LogTrace is *not*: This is *not* a logging framework. LogTrace uses
the standard Python ``logging`` module. All your configuration to
``logging`` is going to be used by LogTrace. All your handlers are going
to act exactly as before. If you use a framework like Django, you use it
just like you do now. No changes whatever are required to your logging
configuration.

We also provide other features like

-  Easily generate a UUID for the logged event.

-  Timing for each message since LogTrace was created.

-  Frame information for each part message, like filename, function,
   lineno

-  Any logging mechanism can be used, not just standard Python logging.

-  Pass structured data (JSON).

We wanted to provide something that works in perfect harmony with the
existing Python logging module without unnecessary duplication of
features and no external dependencies (outside the PSL).

::

        LogTrace(logger=None,      # we'll emit output here
                 delimiter="; ",   # delimiter between messages
                 tag='',           # add a non-unique label 
                 unique_id=False,  # create a uuid to identify the log?
                 verbosity='v'     # level of output for frame information
                )

-  ``logger``: the standard logger returned from
   ``import logging; logger = logging.getLogger(__name__)``. You can
   create a ``LogTrace()`` without a logger in which case it creates
   with the value of ``__name__``.

-  ``delimiter``: the character(s) used between messages

-  ``tag``: This is a convenience to tell LogTrace() to use hash+tag at
   the start of every entry after calling ``.emit()`` for ease of
   searching.

-  ``unique_id``: generate a uuid to associate with the final message
   output.

-  ``verbosity``: v, vv, vvv for three levels of verbosity when adding
   frame information

``LogTrace.get_uid()``: return the unique id. If one has not been set
during construction of the LogTrace, a uuid is generated. Otherwise, it
returns the existing one.

``LogTrace.set_uid(uid)``: Set a unique id. This can be done by
constructing ``LogTrace()`` with ``unique_id=True``. This takes normally
either a uuid or str argument.

``LogTrace.add(msg, data, backup)``: Add a message to the list. This
will get frame information for the call depending on the verbosity
level.

``LogTrace.emit_string()``: return a string that is the final log
message.

``LogTrace.emit()``: call ``logger.debug(message)``

``LogTrace.emit_error()``: call ``logger.error(message)``

``LogTrace.emit_info()``: call ``logger.info(message)``

``LogTrace.emit_debug()``: call ``logger.debug(message)``

``LogTrace.emit_warning()``: call ``logger.warning(message)``

``LogTrace.emit_critical()``: call ``logger.critical(message)``

When the ``LogTrace`` is created, ``time.time()`` is recorded. Whenever
``LogTrace.add()`` is called, the start time is subtracted from the
current time when the message is added. The final message prints the
number of seconds since creating.

You probably want to avoid including ``LogTrace.add()`` in loops. You
also probably want to create it as a local, not a module-level variable.
Pass it as a method argument rather than using a module level instance.
If you do want to re-use a ``LogTrace`` and clear messages, you can call
``LogTrace.clear()``. But be aware the uid might need to be reset
depending on your application requirements.

Extra Data
----------

``LogTrace.add()`` has an optional parameter ``data`` that takes a
dictionary. We keep a dict in the object and ``update()`` it whenever
the ``data`` parameter is used. This doesn’t do anything within
``LogTrace`` itself other than maintain the ``data`` member variable.
But you can accumulate data and later ship the data to a service like
AWS S3 or whatever, like this:

::

    logger.info(trace.emit_string(), extra=trace.data)

This would be useful if you are using a logging handler that ships the
``logging.LogRecord`` as JSON to some service like a document oriented
data store, Elasticsearch, etc.

Testing
-------

::

    pip install pytest
    cd logtrace
    pytest test.py --verbose

or

::

    python3 logtrace/test.py

Performance
-----------

``LogTrace()`` appends to a list of strings everytime you call
``add()``. But it firstly calls ``inspect.getFrameInfo()`` and builds
the string with that information. When ``emit()`` is called, it
concatenates all the strings in the list separated by ``delimiter`` and
then calls ``logger.info()`` or whatever method is appropriate. If the
effective level is not the current level for the method, then the list
will be empty and it won’t do the call to the ``logger`` method.

Acknowledgements
----------------

Thanks to

.. @metazet: https://github.com/metazet

For important fixes.

.. |Build Status| image:: https://travis-ci.org/paul-wolf/logtrace.svg?branch=master
   :target: https://travis-ci.org/paul-wolf/logtrace
