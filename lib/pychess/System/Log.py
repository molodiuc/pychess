from __future__ import print_function
from __future__ import absolute_import

import os
import sys
import time
import logging

from .prefix import addUserDataPrefix

newName = time.strftime("%Y-%m-%d_%H-%M-%S") + ".log"
logformat = "%(asctime)s.%(msecs)03d %(task)s %(levelname)s: %(message)s"

# delay=True argument prevents creating empty .log files
fh = logging.FileHandler(addUserDataPrefix(newName), delay=True)
fh.setFormatter(logging.Formatter(fmt=logformat, datefmt='%H:%M:%S'))

logger = logging.getLogger()
logger.addHandler(fh)


class ExtraAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        kwargs["extra"] = kwargs.get("extra", {"task": "Default"})
        return msg, kwargs

log = ExtraAdapter(logger, {})

    
class LogPipe:
    def __init__ (self, to, flag=""):
        self.to = to
        self.flag = flag
        # Needed for blunders/arena with python3
        self.errors= to.errors
        self.encoding = to.encoding
    
    def write (self, data):
        try:
            self.to.write(data)
            self.flush()
        except IOError:
            if self.flag == "stdout":
                # Certainly hope we never end up here
                pass
            else:
                log.error("Could not write data '%s' to pipe '%s'" % (data, repr(self.to)))
        if log:
            for line in data.splitlines():
                if line:
                    log.debug (line, extra={"task": self.flag})
    
    def flush (self):
        self.to.flush()
    
    def fileno (self):
        return self.to.fileno()

sys.stdout = LogPipe(sys.stdout, "stdout")
sys.stderr = LogPipe(sys.stderr, "stdout")
