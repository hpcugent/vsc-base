#
# Copyright 2013 Ghent University
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
Unit tests for fancylogger.

@author: Kenneth Hoste (Ghent University)
"""
import logging
import os
import re
import tempfile
from unittest import TestCase, TestLoader

import vsc.utils.fancylogger as fancylogger
from vsc.utils.fancylogger import FancyLogger

MSG = "This is a test log message."
# message format: '<date> <time> <type> <source location> <message>'
MSGRE_TPL = r"\d\d\d\d-\d\d-\d\d+\s+\d\d:\d\d:\d\d,\d\d\d\s+%%s.*%s" % MSG

class FancyLoggerTest(TestCase):
    """Tests for fancylogger"""

    logfn = None

    @classmethod
    def setUpClass(cls):
        """Set up log file for tests."""
        (handle, fn) = tempfile.mkstemp()
        cls.logfn = fn
        fancylogger.logToFile(cls.logfn)

    def assertErrorRegex(self, error, regex, call, *args):
        """ convenience method to match regex with the error message """
        try:
            call(*args)
            self.assertTrue(False)  # this will fail when no exception is thrown at all
        except error, err:
            res = re.search(regex, str(err))
            if not res:
                print "err: %s" % err
            self.assertTrue(res)

    def test_log_types(self):
        """Test the several types of logging."""
        logtypes = {
                    'critical': (fancylogger.CRITICAL, (lambda l,m: l.critical(m))),
                    'debug': (fancylogger.DEBUG, (lambda l,m: l.debug(m))),
                    'error': (fancylogger.ERROR, (lambda l,m: l.error(m))),
                    'exception': (fancylogger.EXCEPTION, (lambda l,m: l.exception(m))),
                    'fatal': (fancylogger.FATAL, (lambda l,m: l.fatal(m))),
                    'info': (fancylogger.INFO, (lambda l,m: l.info(m))),
                    'warning': (fancylogger.WARNING, (lambda l,m: l.warning(m))),
                    'warn': (fancylogger.WARN, (lambda l,m: l.warn(m))),
                   }
        for logtype, (loglevel, logf) in sorted(logtypes.items()):

                # log message
                logger = fancylogger.getLogger('%s_test' % logtype)
                logger.setLevel(loglevel)
                logf(logger, MSG)

                # check whether expected message got logged with expected format
                logmsgtype = logtype.upper()
                if logmsgtype == 'EXCEPTION':
                    logmsgtype = 'ERROR'
                if logmsgtype == 'FATAL':
                    logmsgtype = 'CRITICAL'

                msgre = re.compile(MSGRE_TPL % logmsgtype)
                txt = open(self.logfn, 'r').read()

                self.assertTrue(msgre.search(txt))

    def test_uft8_decoding(self):
        """Test UTF8 decoding."""

        non_utf8_msg = "This non-UTF8 character '\x80' should be handled properly."
        logger = fancylogger.getLogger('utf8_test')
        logger.setLevel(fancylogger.DEBUG)
        logger.critical(non_utf8_msg)
        logger.debug(non_utf8_msg)
        logger.error(non_utf8_msg)
        logger.exception(non_utf8_msg)
        logger.fatal(non_utf8_msg)
        logger.info(non_utf8_msg)
        logger.warning(non_utf8_msg)
        logger.warn(non_utf8_msg)
        self.assertErrorRegex(Exception, non_utf8_msg, logger.raiseException, non_utf8_msg)

    def test_deprecated(self):
        """Test deprecated log function."""

        # log message
        logger = fancylogger.getLogger('deprecated_test')

        max_ver = "1.0"
        prefix_tpl = r"\d\d\d\d-\d\d-\d\d\s+\d\d:\d\d:\d\d,\d\d\d\s+"

        # test whether deprecation works
        msgre_tpl_error = r"DEPRECATED\s*\(since v%s\).*%s" % (max_ver, MSG)
        self.assertErrorRegex(Exception, msgre_tpl_error, logger.deprecated, MSG, "1.1", max_ver)

        # test whether deprecated warning works
        logger.deprecated(MSG, "0.9", max_ver)
        msgre_tpl_warning = r"%sWARNING.*DEPRECATED\s*\(since v%s\).*%s" % (prefix_tpl, max_ver, MSG)
        msgre_warning = re.compile(msgre_tpl_warning)
        txt = open(self.logfn, 'r').read()
        self.assertTrue(msgre_warning.search(txt))

        # test handling of non-UTF8 chars
        msg = MSG + "\x81"
        msgre_tpl_error = r"DEPRECATED\s*\(since v%s\).*%s" % (max_ver, msg)
        self.assertErrorRegex(Exception, msgre_tpl_error, logger.deprecated, msg, "1.1", max_ver)
        logger.deprecated(msg, "0.9", max_ver)
        txt = open(self.logfn, 'r').read()
        self.assertTrue(msgre_warning.search(txt))

    @classmethod
    def tearDownClass(cls):
        """Clean up the mess."""
        print "contents of log file:"
        print open(cls.logfn, 'r').read().split('\n')
        os.remove(cls.logfn)


def suite():
    """ returns all the testcases in this module """
    return TestLoader().loadTestsFromTestCase(FancyLoggerTest)
