# -*- coding: utf-8 -*-
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
@author: Stijn De Weirdt (Ghent University)
"""
import os
import re
import sys
import tempfile
from unittest import TestCase, TestLoader, main

from vsc import fancylogger

MSG = "This is a test log message."
# message format: '<date> <time> <type> <source location> <message>'
MSGRE_TPL = r"%%s.*%s" % MSG

class FancyLoggerTest(TestCase):
    """Tests for fancylogger"""

    logfn = None
    handle = None
    fd = None

    def setUp(self):
        (self.fd, self.logfn) = tempfile.mkstemp()
        self.handle = os.fdopen(self.fd)

        # set the test log format
        fancylogger.setTestLogFormat()

        # make new logger
        fancylogger.logToFile(self.logfn)

        # disable default ones (with default format)
        fancylogger.disableDefaultHandlers()

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
        # truncate the logfile
        open(self.logfn, 'w')

        logtypes = {
                    'critical': lambda l, m: l.critical(m),
                    'debug': lambda l, m: l.debug(m),
                    'error': lambda l, m: l.error(m),
                    'exception': lambda l, m: l.exception(m),
                    'fatal': lambda l, m: l.fatal(m),
                    'info': lambda l, m: l.info(m),
                    'warning': lambda l, m: l.warning(m),
                    'warn': lambda l, m: l.warn(m),
                   }
        logfile = open(self.logfn, 'r')

        # we raise an exception here so the logger will be able to print a stacktrace later on
        try:
            raise Exception
        except:
            pass
        for logtype, logf in sorted(logtypes.items()):
                # log message
                logger = fancylogger.getLogger('%s_test' % logtype)
                log_up = logtype.upper()
                logger.setLevel(log_up)
                logf(logger, MSG)

                # check whether expected message got logged with expected format
                logmsgtype = log_up
                if logmsgtype == 'EXCEPTION':
                    msgre = re.compile(".*".join(['ERROR', MSG, '\nTraceback']))
                elif logmsgtype == 'FATAL':
                    msgre = re.compile(MSGRE_TPL % 'CRITICAL')
                else:
                    msgre = re.compile(MSGRE_TPL % logmsgtype)
                txt = logfile.read()

                self.assertTrue(msgre.search(txt))
        logfile.close()

    def test_getlevelint(self):
        """Test the getLevelInt"""
        DEBUG = fancylogger.getLevelInt('DEBUG')
        INFO = fancylogger.getLevelInt('INFO')
        WARNING = fancylogger.getLevelInt('WARNING')
        ERROR = fancylogger.getLevelInt('ERROR')
        CRITICAL = fancylogger.getLevelInt('CRITICAL')
        APOCALYPTIC = fancylogger.getLevelInt('APOCALYPTIC')
        self.assertTrue(INFO > DEBUG)
        self.assertTrue(WARNING > INFO)
        self.assertTrue(ERROR > WARNING)
        self.assertTrue(CRITICAL > ERROR)
        self.assertTrue(APOCALYPTIC > CRITICAL)

    def test_parentinfo(self):
        """Test the collection of parentinfo"""
        log_fr = fancylogger.getLogger(fname=False)  # rootfancylogger
        pi_fr = log_fr._get_parent_info()
        self.assertEqual(len(pi_fr), 2)

        log_l1 = fancylogger.getLogger('level1', fname=False)
        # fname=False is required to have the naming similar for child relations
        pi_l1 = log_l1._get_parent_info()
        self.assertEqual(len(pi_l1), 3)

        py_v_27 = sys.version_info >= (2, 7, 0)
        if py_v_27:
            log_l2a = log_l1.getChild('level2a')
            pi_l2a = log_l2a._get_parent_info()
            self.assertEqual(len(pi_l2a), 4)

        # this should be identical to getChild
        log_l2b = fancylogger.getLogger('level1.level2b', fname=False)
        # fname=False is required to have the name similar
        # cutoff last letter (a vs b)
        if py_v_27:
            self.assertEqual(log_l2a.name[:-1], log_l2b.name[:-1])
        pi_l2b = log_l2b._get_parent_info()
        # yes, this broken on several levels (incl in logging itself)
        # adding '.' in the name does not automatically create the parent/child relations
        # if the parent with the name exists, this works
        self.assertEqual(len(pi_l2b), 4)

        log_l2c = fancylogger.getLogger('level1a.level2c', fname=False)
        pi_l2c = log_l2c._get_parent_info()
        self.assertEqual(len(pi_l2c), 3)  # level1a as parent does not exist


    def test_uft8_decoding(self):
        """Test UTF8 decoding."""
        # truncate the logfile
        open(self.logfn, 'w')

        logger = fancylogger.getLogger('utf8_test')
        logger.setLevel('DEBUG')

        for msg in [
                    "This is a pure ASCII text.",  # pure ASCII
                    "Here are some UTF8 characters: ß, ©, Ω, £.",  # only UTF8 characters
                    "This non-UTF8 character '\x80' should be handled properly.",  # contains non UTF-8 character
                   ]:
            logger.critical(msg)
            logger.debug(msg)
            logger.error(msg)
            logger.exception(msg)
            logger.fatal(msg)
            logger.info(msg)
            logger.warning(msg)
            logger.warn(msg)
            self.assertErrorRegex(Exception, msg, logger.raiseException, msg)

    def test_deprecated(self):
        """Test deprecated log function."""
        # truncate the logfile
        open(self.logfn, 'w')

        # log message
        logger = fancylogger.getLogger('deprecated_test')

        max_ver = "1.0"

        # test whether deprecation works
        msgre_tpl_error = r"DEPRECATED\s*\(since v%s\).*%s" % (max_ver, MSG)
        self.assertErrorRegex(Exception, msgre_tpl_error, logger.deprecated, MSG, "1.1", max_ver)

        # test whether deprecated warning works
        logger.deprecated(MSG, "0.9", max_ver)
        msgre_tpl_warning = r"WARNING.*DEPRECATED\s*\(since v%s\).*%s" % (max_ver, MSG)
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

    def _stream_stdouterr(self, isstdout=True, expect_match=True):
        fd, logfn = tempfile.mkstemp()
        # fh will be checked
        fh = os.fdopen(fd, 'w')

        _stdout = sys.stdout
        _stderr = sys.stderr

        if isstdout == expect_match:
            sys.stdout = fh
            sys.stderr = open(os.devnull, 'w')
        else:
            sys.stdout = open(os.devnull, 'w')
            sys.stderr = fh

        fancylogger.setLogLevelInfo()
        name = 'test_stream_stdout'
        lh = fancylogger.logToScreen(stdout=isstdout)
        logger = fancylogger.getLogger(name)
        # logfn makes it unique
        msg = 'TEST isstdout %s expect_match %s logfn %s' % (isstdout, expect_match, logfn)
        logger.info(msg)

        # restore
        fancylogger.logToScreen(enable=False, handler=lh)
        sys.stdout = _stdout
        sys.stderr = _stderr

        fh2 = open(logfn)
        txt = fh2.read().strip()
        fh2.close()
        reg_exp = re.compile(r"INFO\s+\S+.%s.%s\s+\S+\s+%s" % (name, '_stream_stdouterr', msg))
        match = reg_exp.search(txt) is not None
        self.assertEqual(match, expect_match)

        try:
            fh.close()
            os.remove(logfn)
        except:
            pass

    def test_stream_stdout_stderr(self):
        # log to stdout, check stdout
        self._stream_stdouterr(isstdout=True, expect_match=True)
        # log to stderr, check stderr
        self._stream_stdouterr(isstdout=False, expect_match=True)

        # log to stdout, check stderr
        self._stream_stdouterr(isstdout=True, expect_match=False)
        # log to stderr, check stdout
        self._stream_stdouterr(isstdout=False, expect_match=False)


    def tearDown(self):
        fancylogger.logToFile(self.logfn, enable=False)
        self.handle.close()
        os.remove(self.logfn)


def suite():
    """ returns all the testcases in this module """
    return TestLoader().loadTestsFromTestCase(FancyLoggerTest)

if __name__ == '__main__':
    """Use this __main__ block to help write and test unittests"""
    main()
