#!/usr/bin/env python
##
# Copyright 2012 Ghent University
# Copyright 2012 Andy Georges
#
# This file is part of VSC-tools,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/VSC-tools
#
# VSC-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# VSC-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VSC-tools. If not, see <http://www.gnu.org/licenses/>.
##
""" This module provides functionality to cache and report results of script executions that can readily be
interpreted by nagios/icinga.

- simple exit messages that can directly be picked up by an icingna check
    - ok
    - warning
    - critical
    - unknown
- NagiosReporter class that provides cache functionality, writing and reading the nagios/icinga result string to a
  pickle file.
"""

import os
import pwd
import stat
import sys
import time

from vsc import fancylogger
from vsc.utils.cache import FileCache

log = fancylogger.getLogger(__name__)

NAGIOS_EXIT_OK = 0
NAGIOS_EXIT_WARNING = 1
NAGIOS_EXIT_CRITICAL = 2
NAGIOS_EXIT_UNKNOWN = 3


def _real_exit(kind, message, exit_code):
    """Prints the kind and message and exitas accordingly.

    @type kind: string
    @type message: string
    @type exit_code: int

    @param kind: Prefix to the nagios exit message
    @param message: Useful message for nagios
    @param exit_code: the, ah, erm, exit code of the application using the nagios utility
    """
    print "%s %s" % (kind, message)
    log.info("Nagios report %s: %s" % (kind, message))
    sys.exit(exit_code)


def ok_exit(message):
    """Prints OK message and exits the program with an OK exit code."""
    _real_exit("OK", message, NAGIOS_EXIT_OK)


def warning_exit(message):
    """Prints WARNING message and exits the program with an WARNING exit code."""
    _real_exit("WARNING", message, NAGIOS_EXIT_WARNING)


def unknown_exit(message):
    """Prints UNKNOWN message and exits the program with an UNKNOWN exit code."""
    _real_exit("UNKNOWN", message, NAGIOS_EXIT_UNKNOWN)


def critical_exit(message):
    """Prints CRITICAL message and exits the program with an CRITICAL exit code."""
    _real_exit("CRITICAL", message, NAGIOS_EXIT_CRITICAL)


class NagiosReporter(object):
    """Reporting class for Nagios/Icinga reports.

    Can cache the result in a pickle file and print the result out at some later point.
    """

    def __init__(self, header, filename, threshold):
        """Initialisation.

        @type header: string
        @type filename: string
        @type threshold: positive integer

        @param header: application specific part of the message, used to denote what program/script is using the
                       reporter.
        @param filename: the filename of the pickle cache file
        @param threshold: Seconds to determines how old the pickle data may be
                         before reporting an unknown result. This can be used to check if the script that uses the
                         reporter has run the last time and succeeded in writing the cache data. If the threshold <= 0,
                         this feature is not used.
        """
        self.header = header
        self.filename = filename
        self.threshold = threshold

        self.nagios_username = "nagios"

        self.log = fancylogger.getLogger(self.__class__.__name__)

    def report_and_exit(self):
        """Unpickles the cache file, prints the data and exits accordingly.

        If the cache data is too old (now - cache timestamp > self.threshold), a critical exit is produced.
        """
        try:
            nagios_cache = FileCache(self.filename)
        except:
            self.log.critical("Error opening file %s for reading" % (self.filename))
            unknown_exit("nagios pickled file unavailable (%s)" % (self.header, self.filename))

        (timestamp, (nagios_exit_code, nagios_message)) = nagios_cache.load(0)
        nagios_cache.close()

        if self.threshold < 0 or time.time() - timestamp < self.threshold:
            self.log.info("Nagios check cache file %s contents delivered: %s" % (self.filename, nagios_message))
            print "%s" % (nagios_message)
            sys.exit(nagios_exit_code)
        else:
            unknown_exit("pickled file too old (timestamp = %s)" % (self.header, time.ctime(timestamp)))

    def cache(self, nagios_exit_code, nagios_message):
        """Store the result in the cache file with a timestamp.

        @type nagios_exit_code: integer
        @type nagios_message: string

        @param nagios_exit_code: a valid nagios exit code.
        @param nagios_message: the message to print out when the actual check runs.
        """
        try:
            nagios_cache = FileCache(self.filename)
            nagios_cache.update(0, (nagios_exit_code, nagios_message), 0)  # always update
            nagios_cache.close()
            self.log.info("Wrote nagios check cache file %s at about %s" % (self.filename, time.ctime(time.time())))
        except:
            # raising an error is ok, since we usually do this as the very last thing in the script
            self.log.raiseException("Cannot save to the nagios pickled file (%s)" % (self.filename))

        try:
            p = pwd.getpwnam(self.nagios_username)
            os.chmod(self.filename, stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IWGRP)
            os.chown(self.filename, p.pw_uid, p.pw_gid)
        except:
            self.log.raiseException("Cannot chown the nagios check file %s to the nagios user" % (self.filename))

        return True
