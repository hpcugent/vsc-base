# -*- coding: utf-8 -*-
#
# Copyright 2015-2015 Ghent University
#
# This file is part of vsc-base,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/vsc-base
#
# vsc-base is free software: you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License as
# published by the Free Software Foundation, either version 2 of
# the License, or (at your option) any later version.
#
# vsc-base is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public License
# along with vsc-base. If not, see <http://www.gnu.org/licenses/>.
#
"""
Unit tests for exceptions module.

@author: Kenneth Hoste (Ghent University)
"""
import logging
import os
import re
import tempfile
from unittest import TestLoader, main

from vsc.utils.exceptions import LoggedException, get_callers_logger
from vsc.utils.fancylogger import getLogger, logToFile, logToScreen, getRootLoggerName, setLogFormat
from vsc.utils.testing import EnhancedTestCase


def raise_loggedexception(msg, *args, **kwargs):
    """Utility function: just raise a LoggedException."""
    raise LoggedException(msg, *args, **kwargs)


class ExceptionsTest(EnhancedTestCase):
    """Tests for exceptions module."""

    def test_loggedexception_defaultlogger(self):
        """Test LoggedException custom exception class."""
        fd, tmplog = tempfile.mkstemp()
        os.close(fd)

        # set log format, for each regex searching
        setLogFormat("%(name)s :: %(message)s")

        # if no logger is available, and no logger is specified, use default 'root' fancylogger
        logToFile(tmplog, enable=True)
        self.assertErrorRegex(LoggedException, 'BOOM', raise_loggedexception, 'BOOM')
        logToFile(tmplog, enable=False)

        log_re = re.compile("^%s :: BOOM \(at .*:[0-9]+ in raise_loggedexception\)$" % getRootLoggerName(), re.M)
        logtxt = open(tmplog, 'r').read()
        self.assertTrue(log_re.match(logtxt), "%s matches %s" % (log_re.pattern, logtxt))

        # test formatting of message
        self.assertErrorRegex(LoggedException, 'BOOMBAF', raise_loggedexception, 'BOOM%s', 'BAF')

        # test log message that contains '%s' without any formatting arguments being passed
        # test formatting of message
        self.assertErrorRegex(LoggedException, "BOOM '%s'", raise_loggedexception, "BOOM '%s'")

        os.remove(tmplog)

    def test_loggedexception_specifiedlogger(self):
        """Test LoggedException custom exception class."""
        fd, tmplog = tempfile.mkstemp()
        os.close(fd)

        # set log format, for each regex searching
        setLogFormat("%(name)s :: %(message)s")

        logger1 = getLogger('testlogger_one')
        logger2 = getLogger('testlogger_two')

        # if logger is specified, it should be used
        logToFile(tmplog, enable=True)
        self.assertErrorRegex(LoggedException, 'BOOM', raise_loggedexception, 'BOOM', logger=logger1)
        logToFile(tmplog, enable=False)

        log_re = re.compile("^runpy.testlogger_one :: BOOM \(at .*:[0-9]+ in raise_loggedexception\)$", re.M)
        logtxt = open(tmplog, 'r').read()
        self.assertTrue(log_re.match(logtxt), "%s matches %s" % (log_re.pattern, logtxt))

        os.remove(tmplog)

    def test_loggedexception_callerlogger(self):
        """Test LoggedException custom exception class."""
        fd, tmplog = tempfile.mkstemp()
        os.close(fd)

        # set log format, for each regex searching
        setLogFormat("%(name)s :: %(message)s")

        logger = getLogger('testlogger_local')

        # if no logger is specified, logger available in calling context should be used
        logToFile(tmplog, enable=True)
        self.assertErrorRegex(LoggedException, 'BOOM', raise_loggedexception, 'BOOM')
        logToFile(tmplog, enable=False)

        log_re = re.compile("^runpy.testlogger_local :: BOOM \(at .*:[0-9]+ in raise_loggedexception\)$")
        logtxt = open(tmplog, 'r').read()
        self.assertTrue(log_re.match(logtxt), "%s matches %s" % (log_re.pattern, logtxt))

        os.remove(tmplog)

    def test_loggedexception_location(self):
        """Test inclusion of location information in log message for LoggedException."""
        class TestException(LoggedException):
            LOC_INFO_TOP_PKG_NAMES = None

        def raise_testexception(msg, *args, **kwargs):
            """Utility function: just raise a TestException."""
            raise TestException(msg, *args, **kwargs)

        fd, tmplog = tempfile.mkstemp()
        os.close(fd)

        # set log format, for each regex searching
        setLogFormat("%(name)s :: %(message)s")

        # if no logger is available, and no logger is specified, use default 'root' fancylogger
        logToFile(tmplog, enable=True)
        self.assertErrorRegex(LoggedException, 'BOOM', raise_testexception, 'BOOM')
        logToFile(tmplog, enable=False)

        log_re = re.compile("^%s :: BOOM$" % getRootLoggerName(), re.M)
        logtxt = open(tmplog, 'r').read()
        self.assertTrue(log_re.match(logtxt), "%s matches %s" % (log_re.pattern, logtxt))

        f = open(tmplog, 'w')
        f.write('')
        f.close()
        TestException.LOC_INFO_TOP_PKG_NAMES = ['test']

        # if no logger is specified, logger available in calling context should be used
        logToFile(tmplog, enable=True)
        self.assertErrorRegex(LoggedException, 'BOOM', raise_testexception, 'BOOM')
        logToFile(tmplog, enable=False)

        log_re = re.compile("^%s :: BOOM \(at test.*[0-9]+ in raise_testexception\)$" % getRootLoggerName())
        logtxt = open(tmplog, 'r').read()
        self.assertTrue(log_re.match(logtxt), "%s matches %s" % (log_re.pattern, logtxt))

        os.remove(tmplog)

    def test_get_callers_logger(self):
        """Test get_callers_logger function."""
        # returns None if no logger is available
        self.assertEqual(get_callers_logger(), None)

        # find defined logger in caller's context
        logger = getLogger('foo')
        self.assertEqual(logger, get_callers_logger())

        # also works when logger is 'higher up'
        class Test(object):
            """Dummy test class"""
            def foo(self, logger=None):
                """Dummy test method, returns logger from calling context."""
                return get_callers_logger()

        test = Test()
        self.assertEqual(logger, test.foo())

        # closest logger to caller is preferred
        logger2 = getLogger(test.__class__.__name__)
        self.assertEqual(logger2, test.foo(logger=logger2))

def suite():
    """ returns all the testcases in this module """
    return TestLoader().loadTestsFromTestCase(ExceptionsTest)

if __name__ == '__main__':
    """Use this __main__ block to help write and test unittests"""
    main()
