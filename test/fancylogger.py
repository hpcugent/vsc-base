# -*- coding: utf-8 -*-
#
# Copyright 2013-2020 Ghent University
#
# This file is part of vsc-base,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://www.vscentrum.be),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# https://github.com/hpcugent/vsc-base
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
from __future__ import print_function

import coloredlogs
import logging
import os
import re
import sys
import shutil
import tempfile
from random import randint
from unittest import TestLoader, main, TestSuite

try:
    from cStringIO import StringIO  # Python 2
except ImportError:
    from io import StringIO  # Python 3

try:
    from unittest import skipUnless
except (AttributeError, ImportError):
    # Python 2.6 does not have `skipIf`/`skipUnless`
    def skipUnless(condition, reason):
        if condition:
            def deco(fn):
                return fn
        else:
            def deco(fn):
                return (lambda *args, **kwargs: True)
        return deco

from vsc.utils import fancylogger
from vsc.install.testing import TestCase

MSG = "This is a test log message."
# message format: '<date> <time> <type> <source location> <message>'
MSGRE_TPL = r"%%s.*%s" % MSG


def _get_tty_stream():
    """Try to open and return a stream connected to a TTY device."""
    # sys.stdout/sys.stderr may be a StringIO object, which does not have fileno
    # this happens when running the tests in a virtualenv (e.g. via tox)
    if hasattr(sys.stdout, 'fileno') and os.isatty(sys.stdout.fileno()):
        return sys.stdout
    elif hasattr(sys.stderr, 'fileno') and os.isatty(sys.stderr.fileno()):
        return sys.stderr
    else:
        if 'TTY' in os.environ:
            try:
                tty = os.environ['TTY']
                stream = open(tty, 'w')
                if os.isatty(stream.fileno()):
                    return stream
            except IOError:
                # cannot open $TTY for writing, continue
                pass
        # give up
        return None


def classless_function():
    logger = fancylogger.getLogger(fname=True, clsname=True)
    logger.warn("from classless_function")


class FancyLoggerLogToFileTest(TestCase):
    """
    Tests for fancylogger, specific for logToFile
    These dont' fit in the FancyLoggerTest class because they don't work with the setUp and tearDown used there.
    """

    def test_logtofile(self):
        """Test to see if logtofile doesn't fail when logging to a non existing file /directory"""
        tempdir = tempfile.mkdtemp()
        non_dir = os.path.join(tempdir, 'verytempdir')
        fancylogger.logToFile(os.path.join(non_dir, 'nosuchfile'))
        # clean up temp dir
        shutil.rmtree(tempdir)


class FancyLoggerTest(TestCase):
    """Tests for fancylogger"""

    logfn = None
    handle = None
    fd = None

    def _reset_fancylogger(self):
        fancylogger.resetroot()

        # delete all fancyloggers
        loggers = logging.Logger.manager.loggerDict
        for name, lgr in loggers.items():
            if isinstance(lgr, fancylogger.FancyLogger):
                del loggers[name]
        # reset root handlers; mimic clean import logging
        logging.root.handlers = []

    def setUp(self):
        super(FancyLoggerTest, self).setUp()

        self._reset_fancylogger()

        (self.fd, self.logfn) = tempfile.mkstemp()
        self.handle = os.fdopen(self.fd)

        # set the test log format
        fancylogger.setTestLogFormat()

        # make new logger
        self.handler = fancylogger.logToFile(self.logfn)

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

        open(self.logfn, 'w').write('')

        # test whether deprecated warning works
        # no deprecation if current version is lower than max version
        logger.deprecated(MSG, "0.9", max_ver)

        msgre_warning = re.compile(r"WARNING.*Deprecated.* will no longer work in v%s:.*%s" % (max_ver, MSG))
        txt = open(self.logfn, 'r').read()
        self.assertTrue(msgre_warning.search(txt), "Pattern '%s' found in: %s" % (msgre_warning.pattern, txt))

        # wipe log to start over
        open(self.logfn, 'w').write('')

        callback_cache = []
        def test_log_callback(msg, cache=callback_cache):
            """Log callback function to log warning message and print to stderr."""
            cache.append(msg)

        # test use of log_callback
        logger.deprecated("test callback", "0.9", max_ver, log_callback=test_log_callback)
        self.assertEqual(callback_cache[-1], "Deprecated functionality, will no longer work in v1.0: test callback")

        # wipe log to start over
        open(self.logfn, 'w').write('')

        # test handling of non-UTF8 chars
        msg = MSG + u"\x81"
        msgre_tpl_error = r"DEPRECATED\s*\(since v%s\).*\xc2\x81" % max_ver
        msgre_warning = re.compile(r"WARNING.*Deprecated.* will no longer work in v%s:.*\xc2\x81" % max_ver)

        self.assertErrorRegex(Exception, msgre_tpl_error, logger.deprecated, msg, "1.1", max_ver)

        open(self.logfn, 'w').write('')

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

        regex = re.compile("^WARNING.*HIT.*failtest\n.*in test123.*$", re.M)
        txt = open(self.logfn, 'r').read()
        self.assertTrue(regex.match(txt), "Pattern '%s' matches '%s'" % (regex.pattern, txt))

        open(self.logfn, 'w')
        fancylogger.FancyLogger.RAISE_EXCEPTION_CLASS = KeyError
        logger = fancylogger.getLogger('fail_test')
        self.assertErrorRegex(KeyError, 'failkeytest', test123, KeyError, 'failkeytest')

        regex = re.compile("^WARNING.*HIT.*'failkeytest'\n.*in test123.*$", re.M)
        txt = open(self.logfn, 'r').read()
        self.assertTrue(regex.match(txt), "Pattern '%s' matches '%s'" % (regex.pattern, txt))

        open(self.logfn, 'w')
        fancylogger.FancyLogger.RAISE_EXCEPTION_LOG_METHOD = lambda c, msg: c.warning(msg)
        logger = fancylogger.getLogger('fail_test')
        self.assertErrorRegex(AttributeError, 'attrtest', test123, AttributeError, 'attrtest')

        regex = re.compile("^WARNING.*HIT.*attrtest\n.*in test123.*$", re.M)
        txt = open(self.logfn, 'r').read()
        self.assertTrue(regex.match(txt), "Pattern '%s' matches '%s'" % (regex.pattern, txt))

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
        self.assertTrue('unknown__getCallingClassName.classless_function' in stringfile.getvalue())

        # restore
        fancylogger.logToScreen(enable=False, handler=handler)
        stringfile = StringIO()
        sys.stderr = stringfile

        fancylogger.setLogFormat("%(className)s blabla")
        handler = fancylogger.logToScreen()
        logger = fancylogger.getLogger(fname=False, clsname=False)
        logger.warn("blabla")
        print(stringfile.getvalue())
        # this will only hold in debug mode, so also disable the test
        if __debug__:
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

        res = fancylogger.getDetailsLogLevels(fancy=True)
        self.assertTrue(isinstance(res[0][1], basestring), msg='getDetailsLogLevels returns loglevel names by default')
        res = fancylogger.getDetailsLogLevels(fancy=True, numeric=True)
        self.assertTrue(isinstance(res[0][1], int), msg='getDetailsLogLevels returns loglevel values with numeric=True')

    def test_normal_warning_logging(self):
        """
        Test if just using import logging, logging.warning still works after importing fancylogger
        (take this literally; this does not imply the root logging logger is a fancylogger)
        """

        stringfile = StringIO()
        sys.stderr = stringfile

        msg = 'this is my string'
        logging.warning(msg)
        self.assertTrue(msg in stringfile.getvalue(),
                        msg="'%s' in '%s'" % (msg, stringfile.getvalue()))

        msg = 'there are many like it'
        logging.getLogger().warning(msg)
        self.assertTrue(msg in stringfile.getvalue(),
                        msg="'%s' in '%s'" % (msg, stringfile.getvalue()))

        msg = 'but this one is mine'
        logging.getLogger('mine').warning(msg)
        self.assertTrue(msg in stringfile.getvalue(),
                        msg="'%s' in '%s'" % (msg, stringfile.getvalue()))

    # make sure this test runs last, since it may mess up other tests (like test_raiseException)
    def test_zzz_fancylogger_as_rootlogger_logging(self):
        """
        Test if just using import logging, logging with logging uses fancylogger
        after setting the root logger
        """

        # test logging.root is loggin root logger
        # this is an assumption made to make the fancyrootlogger code work
        orig_root = logging.getLogger()
        self.assertEqual(logging.root, orig_root,
                         msg='logging.root is the root logger')
        self.assertFalse(isinstance(logging.root, fancylogger.FancyLogger),
                         msg='logging.root is not a FancyLogger')

        stringfile = StringIO()
        sys.stderr = stringfile
        handler = fancylogger.logToScreen()
        fancylogger.setLogLevelDebug()
        logger = fancylogger.getLogger()

        self.assertEqual(logger.handlers, [self.handler, handler],
                         msg='active handler for root fancylogger')
        self.assertEqual(logger.level, fancylogger.getLevelInt('DEBUG'), msg='debug level set')

        msg = 'this is my string'
        logging.debug(msg)
        self.assertEqual(stringfile.getvalue(), '',
                         msg="logging.debug reports nothing when fancylogger loglevel is debug")

        fancylogger.setroot()
        self.assertTrue(isinstance(logging.root, fancylogger.FancyLogger),
                         msg='logging.root is a FancyLogger after setRootLogger')
        self.assertEqual(logging.root.level, fancylogger.getLevelInt('DEBUG'), msg='debug level set for root')
        self.assertEqual(logger.level, logging.NOTSET, msg='original root fancylogger level set to NOTSET')

        self.assertEqual(logging.root.handlers, [self.handler, handler],
                         msg='active handler for root logger from previous root fancylogger')
        self.assertEqual(logger.handlers, [], msg='no active handlers on previous root fancylogger')

        root_logger = logging.getLogger('')
        self.assertEqual(root_logger, logging.root,
                        msg='logging.getLogger() returns logging.root FancyLogger')

        frl = fancylogger.getLogger()
        self.assertEqual(frl, logging.root,
                        msg='fancylogger.getLogger() returns logging.root FancyLogger')

        logging.debug(msg)
        self.assertTrue(msg in stringfile.getvalue(),
                         msg="logging.debug reports when fancylogger loglevel is debug")

        fancylogger.resetroot()
        self.assertEqual(logging.root, orig_root,
                         msg='logging.root is the original root logger after resetroot')

        # restore
        fancylogger.logToScreen(enable=False, handler=handler)

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

        self._reset_fancylogger()

        super(FancyLoggerTest, self).tearDown()


class ScreenLogFormatterFactoryTest(TestCase):
    """Test `_screenLogFormatterFactory`"""

    def test_colorize_never(self):
        # with colorize=Colorize.NEVER, return plain old formatter
        cls = fancylogger._screenLogFormatterFactory(fancylogger.Colorize.NEVER)
        self.assertEqual(cls, logging.Formatter)

    def test_colorize_always(self):
        # with colorize=Colorize.ALWAYS, return colorizing formatter
        cls = fancylogger._screenLogFormatterFactory(fancylogger.Colorize.ALWAYS)
        self.assertEqual(cls, coloredlogs.ColoredFormatter)

    @skipUnless(_get_tty_stream(), "cannot get a stream connected to a TTY")
    def test_colorize_auto_tty(self):
        # with colorize=Colorize.AUTO on a stream connected to a TTY,
        # return colorizing formatter
        stream = _get_tty_stream()
        cls = fancylogger._screenLogFormatterFactory(fancylogger.Colorize.AUTO, stream)
        self.assertEqual(cls, coloredlogs.ColoredFormatter)

    def test_colorize_auto_nontty(self):
        # with colorize=Colorize.AUTO on a stream *not* connected to a TTY,
        # return colorizing formatter
        stream = open(os.devnull, 'w')
        cls = fancylogger._screenLogFormatterFactory(fancylogger.Colorize.AUTO, stream)
        self.assertEqual(cls, logging.Formatter)


class EnvToBooleanTest(TestCase):

    def setUp(self):
        self.testvar = self._generate_var_name()
        self.testvar_undef = self._generate_var_name()

    def _generate_var_name(self):
        while True:
            rnd = randint(0, 0xffffff)
            name = ('TEST_VAR_%06X' % rnd)
            if name not in os.environ:
                return name

    def test_env_to_boolean_true(self):
        for value in (
                '1',
                'Y',
                'y',
                'Yes',
                'yes',
                'YES',
                'True',
                'TRUE',
                'true',
                'TrUe', # weird capitalization but should work nonetheless
        ):
            os.environ[self.testvar] = value
            self.assertTrue(fancylogger._env_to_boolean(self.testvar))

    def test_env_to_boolean_false(self):
        for value in (
                '0',
                'n',
                'N',
                'no',
                'No',
                'NO',
                'false',
                'FALSE',
                'False',
                'FaLsE', # weird capitalization but should work nonetheless
                'whatever', # still maps to false
        ):
            os.environ[self.testvar] = value
            self.assertFalse(fancylogger._env_to_boolean(self.testvar))

    def test_env_to_boolean_undef_without_default(self):
        self.assertEqual(fancylogger._env_to_boolean(self.testvar_undef), False)

    def test_env_to_boolean_undef_with_default(self):
        self.assertEqual(fancylogger._env_to_boolean(self.testvar_undef, 42), 42)

    def tearDown(self):
        if self.testvar in os.environ:
            del os.environ[self.testvar]
        del self.testvar
        del self.testvar_undef
