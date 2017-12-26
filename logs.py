# -*- coding: utf-8 -*-
import uuid
import time
import socket
import inspect
import logging
import warnings

# logger = logging.getLogger(__name__)

__all__ = (
    'LogTrace',
)

def clean(s, chars):
    """Clean string s of characters in chars."""
    translation_table = dict.fromkeys(map(ord, chars), '_')
    return s.translate(translation_table)    

def parse(s, delimiter):
    """
    https://stackoverflow.com/questions/18092354/python-split-string-without-splitting-escaped-character/18092547#18092547

    https://www.balabit.com/documents/syslog-ng-ose-latest-guides/en/syslog-ng-ose-guide-admin/html/concepts-message-ietfsyslog.html

    """
    pass
    
class LogTrace(object):
    def __init__(self,
                 logger=None,  # we'll emit output here
                 delimiter="; ",  # delimiter between parts
                 tag='',  # add a label to the log entry, non-unique
                 unique_id=False,  # create a uuid to identify the log?
                 level=logging.DEBUG):
        self.uid = None
        self.data = {}
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger("logtrace")
        self.delimiter = delimiter
        self.level = level
        self.tag = tag
        self.event_log = []
        if tag:  # prepend log record tag
            self.event_log.append(tag)
        if unique_id:
            self.uid = uuid.uuid4()

        self.start = time.time()

    def get_uid(self):
        if not self.uid:
            self.uid = uuid.uuid4()
        return self.uid

    def set_uid(self, uid):
        """
        Accepts a string. Adds it to self.uid as a uuid
        """
        if isinstance(uid, uuid.UUID):
            uid = uuid.UUID(uid)
        self.uid = uid

    def _add_message(self, msg, backup=1):
        """Append msg to logs only if log level is effective."""
        if not self.logger.getEffectiveLevel() >= self.level:
            return

        f = inspect.currentframe()
        for __ in range(backup):
            f = f.f_back
            i = inspect.getframeinfo(f)
        msg = "[{0}, {1:.4f}s] {2}".format(i.lineno, time.time() - self.start, msg)

        self.event_log.append(msg)

    def _add_data(self, data):
        """Update self.data with new data, be careful with key duplicates. """
        self.data.update(data)

    def add(self, msg=None, data=None, backup=1):
        if msg:
            self._add_message(msg, backup)
        if data:
            self._add_data(data)

    def build_message(self):
        msg = delimiter.join(self.event_log)
        if self.clean:
            msg = msg.replace(delimiter, '_')

        if self.uid:
            msg = "uid={}{}{}".format(self.uid, self.delimiter, msg)
        return msg

    def emit_string(self, msg=None, delimiter=None, backup=2):
        """Return string of log record."""

        if not delimiter:
            delimiter = self.delimiter

        if msg:
            self.add(msg, backup=backup)

        return self.build_message()

    def emit(self, msg=None, delimiter=None, emit_func=None, backup=2):
        """Call emit function on self.logger which 
        defaults to logger.debug

        or call emit_func which should be something like:

            log.emit(emit_func=logger.error)

        backup: how many frames to go back in the stack 
        for the actually relevant caller

        """
        if not delimiter:
            delimiter = self.delimiter

        if msg:
            self.add(msg, backup=backup)

        extra = {}

        if not emit_func:
            self.logger.debug(self.build_message(), extra=extra)
        else:
            emit_func(self.build(), extra=extra)

    def emit_error(self, msg, delimiter=None):
        self.emit(msg, delimiter, emit_func=self.logger.error, backup=3)

    def emit_debug(self, msg, delimiter=None):
        self.emit(msg, delimiter, emit_func=self.logger.debug, backup=3)

    def emit_info(self, msg, delimiter=None):
        self.emit(msg, delimiter, emit_func=self.logger.info, backup=3)

    def emit_warning(self, msg, delimiter=None):
        self.emit(msg, delimiter, emit_func=self.logger.warning, backup=3)

    def emit_critical(self, msg, delimiter=None):
        self.emit(msg, delimiter, emit_func=self.logger.critical, backup=3)



