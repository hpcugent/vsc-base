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

NAGIOS_EXIT_OK = (0, 'OK')
NAGIOS_EXIT_WARNING = (1, 'WARNING')
NAGIOS_EXIT_CRITICAL = (2, 'CRITICAL')
NAGIOS_EXIT_UNKNOWN = (3, 'UNKNOWN')


def _real_exit(message, code):
    """Prints the code and message and exitas accordingly.

    @type message: string
    @type exit_code: int

    @param message: Useful message for nagios
    @param exit_code: the, ah, erm, exit code of the application using the nagios utility
    """
    (exit_code, text) = code
    print "%s %s" % (text, message)
    log.info("Nagios report %s: %s" % (text, message))
    sys.exit(exit_code)


def ok_exit(message):
    """Prints OK message and exits the program with an OK exit code."""
    _real_exit(message, NAGIOS_EXIT_OK)


def warning_exit(message):
    """Prints WARNING message and exits the program with an WARNING exit code."""
    _real_exit(message, NAGIOS_EXIT_WARNING)


def unknown_exit(message):
    """Prints UNKNOWN message and exits the program with an UNKNOWN exit code."""
    _real_exit(message, NAGIOS_EXIT_UNKNOWN)


def critical_exit(message):
    """Prints CRITICAL message and exits the program with an CRITICAL exit code."""
    _real_exit(message, NAGIOS_EXIT_CRITICAL)


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
            unknown_exit("%s nagios pickled file unavailable (%s)" % (self.header, self.filename))

        (timestamp, ((nagios_exit_code, nagios_exit_string), nagios_message)) = nagios_cache.load(0)
        nagios_cache.close()

        if self.threshold < 0 or time.time() - timestamp < self.threshold:
            self.log.info("Nagios check cache file %s contents delivered: %s" % (self.filename, nagios_message))
            print "%s %s" % (nagios_exit_string, nagios_message)
            sys.exit(nagios_exit_code)
        else:
            unknown_exit("%s pickled file too old (timestamp = %s)" % (self.header, time.ctime(timestamp)))

    def cache(self, nagios_exit, nagios_message):
        """Store the result in the cache file with a timestamp.

        @type nagios_exit: one of NAGIOS_EXIT_OK, NAGIOS_EXIT_WARNING, NAGIOS_EXIT_CRTITCAL or NAGIOS_EXIT_UNKNOWN
        @type nagios_message: string

        @param nagios_exit_code: a valid nagios exit code.
        @param nagios_message: the message to print out when the actual check runs.
        """
        try:
            nagios_cache = FileCache(self.filename)
            nagios_cache.update(0, (nagios_exit, nagios_message), 0)  # always update
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


class NagiosResult(object):
    '''Class representing the results of an Icinga/Nagios check.

    It will contain a field with the message to be printed.  And the
    rest of its fields will be the performance data, including
    thresholds for each aspect.

    It provides an C{__str__} method, so that when the results are
    printed, they are rendered correctly and we don't wonder why
    Icinga is doing weird things with its plots.

    For example:

    >>> n = NagiosResult('msg', a=1)
    >>> print n
    msg | a=1;;;
    >>> n = NagiosResult('msg', a=1, a_critical=2, a_warning=3)
    >>> print n
    msg | a=1;3;2;
    >>> n = NagiosResult('msg')
    >>> print n
    msg
    >>> n.a = 5
    >>> print n
    msg | a=5;;;

    For more information about performance data and output strings in
    Nagios checks, please refer to
    U{http://docs.icinga.org/latest/en/perfdata.html}
    '''

    def __init__(self, message, **kwargs):
        '''Class constructor.  Takes a message and an optional
        dictionary with each relevant metric and (perhaps) its
        critical and warning thresholds

        @type message: string
        @type kwargs: dict

        @param message: Output of the check.
        @param kwargs: Each value is a number or a string which is
        expected to be a number plus a unit.  Each key is the name of
        a performance datum, optionally with the suffixes "_critical"
        and "_warning" for marking the respective thresholds.
        '''
        self.__dict__ = kwargs
        self.message = message

    def __str__(self):
        '''Turns the result object into a string suitable for being
        printed by an Icinga check'''
        s = self.message

        d = dict()

        for key, value in self.__dict__.iteritems():
            if key == 'message':
                continue
            if key.endswith('_critical'):
                l = key[:-len('_critical')]
                f = d.get(l, dict())
                f['critical'] = value
                d[l] = f
            elif key.endswith('_warning'):
                l = key[:-len('_warning')]
                f = d.get(l, dict())
                f['warning'] = value
                d[l] = f
            else:
                f = d.get(key, dict())
                f['value'] = value
                #print "Key is ", key, "f is", f
                d[key] = f

        if not d:
            return self.message
        perf = ["%s=%s;%s;%s;" % (k, v.get('value', ''), v.get('warning', ''), v.get('critical', ''))
                for k, v in d.iteritems() ]

        return "%s | %s" % (self.message, ' '.join(perf))

if __name__ == '__main__':
    import doctest
    doctest.testmod()
