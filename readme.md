LogTrace
========

Aggregate messages to produce a log entry representing a single event or procedure.

```
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

## Testing

	pip install pytest
 	pytest strgen/test.py --verbose


