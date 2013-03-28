#!/usr/bin/python
##
#
# Copyright 2009-2011 Ghent University
#
# This file is part of the tools originally by the HPC team of
# Ghent University (http://ugent.be/hpc).
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
##
"""Utilities for locks."""
import sys

from lockfile import LockFailed, NotLocked, NotMyLock
from vsc.utils.fancylogger import getLogger
from vsc.utils.nagios import NAGIOS_EXIT_CRITICAL, NAGIOS_EXIT_WARNING, NagiosResult

logger = getLogger('vsc.utils.lock')


def lock_or_bork(lockfile, nagios_reporter):
    """Take the lock on the given lockfile.

    If the lock cannot be obtained:
        - log a critical error
        - store a critical failure in the nagios cache file
        - exit the script
    """
    try:
        lockfile.acquire()
    except LockFailed, err:
        logger.critical('Unable to obtain lock: lock failed')
        nagios_reporter.cache(NAGIOS_EXIT_CRITICAL, NagiosResult("script failed taking lock %s" % (lockfile.path)))
        sys.exit(1)
    except LockFileReadError, err:
        logger.critical("Unable to obtain lock: could not read previous lock file %s" % (lockfile.path))
        nagios_reporter.cache(NAGIOS_EXIT_CRITICAL, NagiosResult("script failed reading lockfile %s" % (lockfile.path)))
        sys.exit(1)


def release_or_bork(lockfile, nagios_reporter, nagios_result):
    """ Release the lock on the given lockfile.

    If the lock cannot be released:
        - log a critcal error
        - store a critical failure in the nagios cache file
        - exit the script
    """

    try:
        lockfile.release()
    except NotLocked, err:
        logger.critical('Lock release failed: was not locked.')
        nagios_reporter.cache(NAGIOS_EXIT_WARNING, nagios_result)
        sys.exit(1)
    except NotMyLock, err:
        logger.error('Lock release failed: not my lock')
        nagios_reporter.cache(NAGIOS_EXIT_WARNING, nagios_result)
        sys.exit(1)


