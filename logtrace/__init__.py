# -*- coding: utf-8 -*-

# Copyright (c) 2017-2018, Paul Wolf.
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:

# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.

# 3. Neither the name of Yewleaf Ltd. nor the names of its contributors
# may be used to endorse or promote products derived from this software
# without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Original author: paul.wolf@yewleaf.com

import uuid
import time
import inspect
import logging

__version__ = '0.1.1'
__author__ = 'Paul Wolf'
__license__ = 'BSD'

# __all__ = (
#     'LogTrace',
# )

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
                 level=None, # default level if you want to use emit()
                 verbosity='v'):
        self.uid = None
        self.verbosity = verbosity
        self.data = {}
        if logger:
            self.logger = logger
        else:
            self.logger = logging.getLogger(__name__)
        self.delimiter = delimiter
        if level:
            self.level = level
        else:
            self.level = self.logger.getEffectiveLevel()

        self.event_log = []

        if tag:  # prepend log record tag
            if not tag[0] == '#':
                tag = '#' + tag
            self.event_log.append(tag)
        if unique_id:
            self.uid = uuid.uuid4()
        self.clean = False

        self.emit_funcs = {
            logging.DEBUG: self.logger.debug,
            logging.INFO: self.logger.info,            
            logging.WARNING: self.logger.warning,            
            logging.ERROR: self.logger.error,
            logging.CRITICAL: self.logger.critical,
        }
        
        self.start = time.time()

    def clear(self):
        self.event_log = []
        self.start = time.time()
        
    def get_uid(self):
        if not self.uid:
            self.uid = uuid.uuid4()
        return self.uid

    def set_uid(self, uid):
        """
        Accepts a string or uuid. Adds it to self.uid as a uuid. 
        We want to not care which it is. Any string can be used for this. 
        """
        if not (isinstance(uid, uuid.UUID) or isinstance(uid, str)):
            uid = str(uid)
        self.uid = uid

    def _add_message(self, msg, backup=1):
        """Append msg to logs only if log level is effective."""
        if not self.logger.getEffectiveLevel() >= self.logger.level:
            print("WARNING, not adding message, effective level: {}, level={}".format(self.logger.getEffectiveLevel(), self.logger.level))
            return

        f = inspect.currentframe()
        for __ in range(backup):
            f = f.f_back
            i = inspect.getframeinfo(f)
        if self.verbosity == 'v':
            msg = "[{0}, {1:.4f}s] {2}".format(i.lineno, time.time() - self.start, msg)
        elif self.verbosity == 'vv':
            msg = "[{0}:{1}, {2:.4f}s] {3}".format(i.function,
                                                   i.lineno, time.time() - self.start, msg)
        elif self.verbosity == 'vvv':
            msg = "[{0}.{1}:{2}, {3:.4f}s] {4}".format(i.filename, i.function,
                                                      i.lineno, time.time() - self.start, msg)
        self.event_log.append(msg)

    def _add_data(self, data):
        """Update self.data with new data, be careful with key duplicates. """
        self.data.update(data)

    def add(self, msg=None, data=None, backup=2):
        if msg:
            self._add_message(msg, backup)
        if data:
            self._add_data(data)

    def build_message(self):
        msg = self.delimiter.join(self.event_log)
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
        for the actually relevant calling frame

        """
        if not self.logger.getEffectiveLevel() >= self.logger.level:
            return
        
        if not delimiter:
            delimiter = self.delimiter

        if msg:
            self.add(msg, backup=backup)

        extra = {}

        if not emit_func:
            emit_func = self.emit_funcs[self.level]

        emit_func(self.build_message(), extra=extra)

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



