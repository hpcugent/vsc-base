#
# Copyright 2012-2019 Ghent University
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
Tests for the vsc.utils.testing module.

@author: Kenneth Hoste (Ghent University)
"""
import os
import re
import sys
from unittest import TestLoader, main

from vsc.utils.missing import shell_quote
from vsc.install.testing import TestCase

import logging

class TestTesting(TestCase):
    """Tests for vsc.utils.testing module."""

    def test_convert_exception_to_str(self):
        """Tests for convert_exception_to_str method."""
        class TestException(Exception):
            """Test Exception class."""
            def __init__(self, msg):
                Exception.__init__(self, msg)
                self.msg = msg

            def __str__(self):
                return repr(self.msg)

        for exception in OSError, Exception, TestException:
            msg = 'test_%s' % exception.__name__
            err = exception(msg)
            self.assertEqual(self.convert_exception_to_str(err), msg)

    def test_assertErrorRegex(self):
        """Tests for assertErrorRegex method."""
        testfile = '/no/such/file'
        self.assertErrorRegex(KeyError, "foo", {'one': 1}.pop, 'foo')
        self.assertErrorRegex(KeyError, "^foo$", {'two': 2}.pop, 'foo')
        self.assertErrorRegex(KeyError, re.compile("^foo$"), {'two': 2}.pop, 'foo')
        self.assertErrorRegex(KeyError, re.compile(".*bar.*"), {'two': 2}.pop, 'foobarbaz')
        # INCEPTION!
        # id(0) should never throw any error
        regex = "Expected errors with .* should occur"
        self.assertErrorRegex(AssertionError, regex, self.assertErrorRegex, Exception, '.*', id, 0)
        # exception should be of specified type, otherwise it's not catched and simply raised through
        self.assertErrorRegex(OSError, '.*', self.assertErrorRegex, KeyError, '.*', os.remove, testfile)
        # provided regex pattern should match
        regex = "Pattern .* is found in .*"
        self.assertErrorRegex(AssertionError, regex, self.assertErrorRegex, Exception, 'foobar', os.remove, testfile)

    def test_capture_stdout_stderr(self):
        """Test capturing of stdout."""
        orig_sys_stdout = sys.stdout
        orig_sys_stderr = sys.stderr

        self.mock_stdout(True)
        print('test')
        self.assertEqual(self.get_stdout(), "test\n")
        sys.stdout.write('foo')
        self.mock_stderr(True)
        sys.stdout.write('bar\n')
        sys.stderr.write('testerror')
        self.assertEqual(self.get_stdout(), "test\nfoobar\n")
        self.assertEqual(self.get_stderr(), "testerror")
        self.mock_stdout(False)
        self.mock_stderr(False)

        self.assertEqual(sys.stdout, orig_sys_stdout)
        self.assertEqual(sys.stderr, orig_sys_stderr)

    def test_mock_logmethod(self):
        """Test the mocked cache logger"""
        # There shouldn't be any yet
        self.assertEqual(self.count_logcache('error'), 0)

        myerror = self.mock_logmethod(logging.error)

        myerror("Error")
        self.assertEqual(self.count_logcache('error'), 1)

        myerror("Moar error")
        myerror("Even moar error")
        self.assertEqual(self.count_logcache('error'), 3)

        self.reset_logcache('error')
        self.assertEqual(self.count_logcache('error'), 0)

        myerror("Error")
        myerror("Moar error")
        self.assertEqual(self.count_logcache('error'), 2)

def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestTesting)


if __name__ == '__main__':
    main()
