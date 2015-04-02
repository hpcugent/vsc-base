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
import logging
import os
import re
import sys
from StringIO import StringIO
import tempfile
from unittest import TestLoader, main

from vsc.utils import fancylogger
from vsc.utils.testing import EnhancedTestCase

MSG = "This is a test log message."
# message format: '<date> <time> <type> <source location> <message>'
MSGRE_TPL = r"%%s.*%s" % MSG


def classless_function():
    logger = fancylogger.getLogger(fname=True, clsname=True)
    logger.warn("from classless_function")


class FancyLoggerTest(EnhancedTestCase):
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

        self.orig_raise_exception_class = fancylogger.FancyLogger.RAISE_EXCEPTION_CLASS
        self.orig_raise_exception_method = fancylogger.FancyLogger.RAISE_EXCEPTION_LOG_METHOD

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

        msgs = [
            # bytestrings
            "This is a pure ASCII text.",  # pure ASCII
            "Here are some UTF-8 characters: ß, ©, Ω, £.",  # only UTF8 characters
            "This non-UTF-8 character '\x80' should be handled properly.",  # contains non UTF-8 character
            # unicode strings
            u"This is a pure ASCII text.",  # pure ASCII
            u"Here are some UTF8 characters: ß, ©, Ω, £.",  # only UTF8 characters
            u"This non-UTF8 character '\x80' should be handled properly.",  # contains non UTF-8 character
        ]
        for msg in msgs:
            logger.critical(msg)
            logger.debug(msg)
            logger.error(msg)
            logger.exception(msg)
            logger.fatal(msg)
            logger.info(msg)
            logger.warning(msg)
            logger.warn(msg)
            if isinstance(msg, unicode):
                regex = msg.encode('utf8', 'replace')
            else:
                regex = str(msg)
            self.assertErrorRegex(Exception, regex, logger.raiseException, msg)

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
        self.assertErrorRegex(Exception, msgre_tpl_error, logger.deprecated, MSG, "1.0", max_ver)

        # test whether deprecated warning works
        # no deprecation if current version is lower than max version
        logger.deprecated(MSG, "0.9", max_ver)
        msgre_tpl_warning = r"WARNING.*DEPRECATED\s*\(since v%s\).*%s" % (max_ver, MSG)
        msgre_warning = re.compile(msgre_tpl_warning)
        txt = open(self.logfn, 'r').read()
        self.assertTrue(msgre_warning.search(txt))

        # test handling of non-UTF8 chars
        msg = MSG + u"\x81"
        msgre_tpl_error = r"DEPRECATED\s*\(since v%s\).*\xc2\x81" % max_ver
        self.assertErrorRegex(Exception, msgre_tpl_error, logger.deprecated, msg, "1.1", max_ver)
        logger.deprecated(msg, "0.9", max_ver)
        txt = open(self.logfn, 'r').read()
        self.assertTrue(msgre_warning.search(txt))

    def test_fail(self):
        """Test fail log method."""
        # truncate the logfile
        open(self.logfn, 'w')

        logger = fancylogger.getLogger('fail_test')
        self.assertErrorRegex(Exception, 'failtest', logger.fail, 'failtest')
        self.assertTrue(re.match("^WARNING.*failtest$", open(self.logfn, 'r').read()))
        self.assertErrorRegex(Exception, 'failtesttemplatingworkstoo', logger.fail, 'failtest%s', 'templatingworkstoo')

        open(self.logfn, 'w')
        fancylogger.FancyLogger.RAISE_EXCEPTION_CLASS = KeyError
        logger = fancylogger.getLogger('fail_test')
        self.assertErrorRegex(KeyError, 'failkeytest', logger.fail, 'failkeytest')
        self.assertTrue(re.match("^WARNING.*failkeytest$", open(self.logfn, 'r').read()))

        open(self.logfn, 'w')
        fancylogger.FancyLogger.RAISE_EXCEPTION_LOG_METHOD = lambda c, msg: c.warning(msg)
        logger = fancylogger.getLogger('fail_test')
        self.assertErrorRegex(KeyError, 'failkeytestagain', logger.fail, 'failkeytestagain')
        self.assertTrue(re.match("^WARNING.*failkeytestagain$", open(self.logfn, 'r').read()))

    def test_raiseException(self):
        """Test raiseException log method."""
        # truncate the logfile
        open(self.logfn, 'w')

        def test123(exception, msg):
            """Utility function for testing raiseException."""
            try:
                raise exception(msg)
            except:
                logger.raiseException('HIT')

        logger = fancylogger.getLogger('fail_test')
        self.assertErrorRegex(Exception, 'failtest', test123, Exception, 'failtest')
        self.assertTrue(re.match("^WARNING.*HIT.*failtest\n.*in test123.*$", open(self.logfn, 'r').read(), re.M))

        open(self.logfn, 'w')
        fancylogger.FancyLogger.RAISE_EXCEPTION_CLASS = KeyError
        logger = fancylogger.getLogger('fail_test')
        self.assertErrorRegex(KeyError, 'failkeytest', test123, KeyError, 'failkeytest')
        self.assertTrue(re.match("^WARNING.*HIT.*'failkeytest'\n.*in test123.*$", open(self.logfn, 'r').read(), re.M))

        open(self.logfn, 'w')
        fancylogger.FancyLogger.RAISE_EXCEPTION_LOG_METHOD = lambda c, msg: c.warning(msg)
        logger = fancylogger.getLogger('fail_test')
        self.assertErrorRegex(AttributeError, 'attrtest', test123, AttributeError, 'attrtest')
        self.assertTrue(re.match("^WARNING.*HIT.*attrtest\n.*in test123.*$", open(self.logfn, 'r').read(), re.M))

    def _stream_stdouterr(self, isstdout=True, expect_match=True):
        """Log to stdout or stderror, check stdout or stderror"""
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
        logger = fancylogger.getLogger(name, fname=True, clsname=False)
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
            os.remove(logfn)
        except:
            pass

    def test_stream_stdout_stderr(self):
        # log to stdout, check stdout
        self._stream_stdouterr(True, True)
        # log to stderr, check stderr
        self._stream_stdouterr(False, True)

        # log to stdout, check stderr
        self._stream_stdouterr(True, False)
        # log to stderr, check stdout
        self._stream_stdouterr(False, False)

    def test_classname_in_log(self):
        """Do a log and check if the classname is correctly in it"""
        _stderr = sys.stderr

        class Foobar:
            def somefunction(self):
                logger = fancylogger.getLogger(fname=True, clsname=True)
                logger.warn('we are logging something here')

        stringfile = StringIO()
        sys.stderr = stringfile
        handler = fancylogger.logToScreen()

        Foobar().somefunction()
        self.assertTrue('Foobar.somefunction' in stringfile.getvalue())
        stringfile.close()

        # restore
        fancylogger.logToScreen(enable=False, handler=handler)
        # and again
        stringfile = StringIO()
        sys.stderr = stringfile
        handler = fancylogger.logToScreen()
        classless_function()
        self.assertTrue('?.classless_function' in stringfile.getvalue())

        # restore
        fancylogger.logToScreen(enable=False, handler=handler)
        stringfile = StringIO()
        sys.stderr = stringfile

        fancylogger.setLogFormat("%(className)s blabla")
        handler = fancylogger.logToScreen()
        logger = fancylogger.getLogger(fname=False, clsname=False)
        logger.warn("blabla")
        print stringfile.getvalue()
        # this will only hold in debug mode, so also disable the test
        if  __debug__:
            self.assertTrue('FancyLoggerTest' in stringfile.getvalue())
        # restore
        fancylogger.logToScreen(enable=False, handler=handler)
        sys.stderr = _stderr

    def test_getDetailsLogLevels(self):
        """
        Test the getDetailsLogLevels selection logic
        (and also the getAllExistingLoggers, getAllFancyloggers and
        getAllNonFancyloggers function call)
        """
        # logger names are unique
        for fancy, func in [(False, fancylogger.getAllNonFancyloggers),
                            (True, fancylogger.getAllFancyloggers),
                            (None, fancylogger.getAllExistingLoggers)]:
            self.assertEqual([name for name, _ in func()],
                             [name for name, _ in fancylogger.getDetailsLogLevels(fancy)],
                             "Test getDetailsLogLevels fancy %s and function %s" % (fancy, func.__name__))
        self.assertEqual([name for name, _ in fancylogger.getAllFancyloggers()],
                         [name for name, _ in fancylogger.getDetailsLogLevels()],
                         "Test getDetailsLogLevels default fancy True and function getAllFancyloggers")

    def test_normal_logging(self):
        """
        Test if just using import logging, logging.warning still works after importing fancylogger
        """
        _stderr = sys.stderr
        stringfile = StringIO()
        sys.stderr = stringfile
        handler = fancylogger.logToScreen()
        import logging
        logging.warning('this is my string')
        self.assertTrue('this is my string' in stringfile.getvalue())

        logging.getLogger().warning('there are many like it')
        self.assertTrue('there are many like it' in stringfile.getvalue())

        logging.getLogger('mine').warning('but this one is mine')
        self.assertTrue('but this one is mine' in stringfile.getvalue())

        # restore
        fancylogger.logToScreen(enable=False, handler=handler)
        sys.stderr = _stderr

    def test_fancyrecord(self):
        """
        Test fancyrecord usage
        """
        logger = fancylogger.getLogger()
        self.assertEqual(logger.fancyrecord, True)

        logger = fancylogger.getLogger(fancyrecord=True)
        self.assertEqual(logger.fancyrecord, True)

        logger = fancylogger.getLogger(fancyrecord=False)
        self.assertEqual(logger.fancyrecord, False)

        logger = fancylogger.getLogger('myname')
        self.assertEqual(logger.fancyrecord, False)

        logger = fancylogger.getLogger('myname', fancyrecord=True)
        self.assertEqual(logger.fancyrecord, True)

        orig = fancylogger.FANCYLOG_FANCYRECORD
        fancylogger.FANCYLOG_FANCYRECORD = False

        logger = fancylogger.getLogger()
        self.assertEqual(logger.fancyrecord, False)

        logger = fancylogger.getLogger('myname', fancyrecord=True)
        self.assertEqual(logger.fancyrecord, True)

        fancylogger.FANCYLOG_FANCYRECORD = True

        logger = fancylogger.getLogger()
        self.assertEqual(logger.fancyrecord, True)

        logger = fancylogger.getLogger('myname')
        self.assertEqual(logger.fancyrecord, True)

        logger = fancylogger.getLogger('myname', fancyrecord=False)
        self.assertEqual(logger.fancyrecord, False)

        logger = fancylogger.getLogger('myname', fancyrecord='yes')
        self.assertEqual(logger.fancyrecord, True)
        
        logger = fancylogger.getLogger('myname', fancyrecord=0)
        self.assertEqual(logger.fancyrecord, False)

        fancylogger.FANCYLOG_FANCYRECORD = orig

    def tearDown(self):
        fancylogger.logToFile(self.logfn, enable=False)
        self.handle.close()
        os.remove(self.logfn)

        fancylogger.FancyLogger.RAISE_EXCEPTION_CLASS = self.orig_raise_exception_class
        fancylogger.FancyLogger.RAISE_EXCEPTION_LOG_METHOD = self.orig_raise_exception_method


def suite():
    """ returns all the testcases in this module """
    return TestLoader().loadTestsFromTestCase(FancyLoggerTest)

if __name__ == '__main__':
    """Use this __main__ block to help write and test unittests"""
    main()
