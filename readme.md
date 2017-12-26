LogTrace
========

[![Build Status](https://travis-ci.org/paul-wolf/logtrace.svg?branch=master)](https://travis-ci.org/paul-wolf/logtrace)

Aggregate messages to produce a log entry representing a single event or procedure.

```
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
```

You get a single log entry like this:

```
[05/Jan/2018 11:11:00] DEBUG [21, .30s] Let's get started; [65, .132s] Later, something else happens; [75, .330s] And finally...
```

The purpose of this module is to easily asssociate log messages
together that belong together.

Install
-------

	pip install logtrace

If your log level is `logging.INFO` and you call `logtrace.emit_debug()`, nothing is sent to the

What LogTrace is *not*: This is *not* a logging framework. LogTrace uses the standard Python `logging` module. All your configuration to `logging` is going to be used by LogTrace. All your handlers are going to be act exactly as before. If you use a framework like Django, you use it just like you do now. No changes whatever are required to your logging configuration. 

We also provide other features like

* Easily generate a UUID for the logged event.

* Timings for each message.

* Frame information for each part message, like lineno

* Any logging mechanism can be used, not just standard Python logging.

* Pass structured data (json).

* Enable log messages to be parsed

We wanted to provide something that works in perfect harmony with the
existing Python logging module without unnecessary duplication of
features and no external dependencies (outside the PSL).

```
    LogTrace(logger=None,      # we'll emit output here
             delimiter="; ",   # delimiter between messages
             tag='',           # add a non-unique label 
             unique_id=False,  # create a uuid to identify the log?
             level=logging.DEBUG  # what log level? 
            )
```

`logger`: the standard logger returned from `import logging; logger = logging.getLogger(__name__)`. You can create a `LogTrace()` without a logger in which case it creates one called "logtrace". 
`delimiter`: the character(s) used between messages
`tag`: This is a convenience to tell LogTrace() to use hash+tag at the start of every entry after calling `.emit()` for easy of searching.
`unique_id`: generate a uuid to associate with the final message output.
`level`: 


Testing
-------

	pip install pytest
 	pytest logtrace/test.py --verbose


Performance
-----------

