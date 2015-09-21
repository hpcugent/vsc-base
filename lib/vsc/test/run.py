#!/usr/bin/env python
# #
#
# Copyright 2012-2013 Ghent University
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
# #
"""
Tests for the vsc.utils.run module.

@author: Stijn De Weirdt (Ghent University)
"""
import pkgutil
import os
import re
import stat
import tempfile
import time
from unittest import TestLoader, main

from vsc.utils.run import run_simple, run_asyncloop, run_timeout, RunQA
from vsc.utils.run import RUNRUN_TIMEOUT_OUTPUT, RUNRUN_TIMEOUT_EXITCODE, RUNRUN_QA_MAX_MISS_EXITCODE
from vsc.utils.testing import EnhancedTestCase


class RunQAShort(RunQA):
    LOOP_MAX_MISS_COUNT = 3  # approx 3 sec

run_qas = RunQAShort.run


class TestRun(EnhancedTestCase):
    """Test for the run module."""

    def setUp(self):
        """Setup test."""
        super(TestRun, self).setUp()

        script_txt = pkgutil.get_data('vsc.test', os.path.join('runtests', 'simple.py'))
        fd, self.script_simple = tempfile.mkstemp()
        os.close(fd)
        f = open(self.script_simple, 'w')
        f.write(script_txt)
        f.close()
        os.chmod(self.script_simple, stat.S_IRUSR|stat.S_IXUSR)

        script_txt = pkgutil.get_data('vsc.test', os.path.join('runtests', 'qa.py'))
        fd, self.script_qa = tempfile.mkstemp()
        os.close(fd)
        f = open(self.script_qa, 'w')
        f.write(script_txt)
        f.close()
        os.chmod(self.script_qa, stat.S_IRUSR|stat.S_IXUSR)

    def test_simple(self):
        ec, output = run_simple([self.script_simple, 'shortsleep'])
        self.assertEqual(ec, 0)
        self.assertTrue('shortsleep' in output.lower())

    def test_simple_asyncloop(self):
        ec, output = run_asyncloop([self.script_simple, 'shortsleep'])
        self.assertEqual(ec, 0)
        self.assertTrue('shortsleep' in output.lower())

    def test_timeout(self):
        start = time.time()
        timeout = 3
        # longsleep is 10sec
        ec, output = run_timeout([self.script_simple, 'longsleep'], timeout=timeout)
        stop = time.time()
        self.assertEqual(ec, RUNRUN_TIMEOUT_EXITCODE)
        self.assertTrue(RUNRUN_TIMEOUT_OUTPUT == output)
        self.assertTrue(stop - start < timeout + 1)  # give 1 sec margin

    def test_qa_simple(self):
        """Simple testing"""
        ec, output = run_qas([self.script_qa, 'noquestion'])
        self.assertEqual(ec, 0)

        qa_dict = {
                   'Simple question:': 'simple answer',
                   }
        ec, output = run_qas([self.script_qa, 'simple'], qa=qa_dict)
        self.assertEqual(ec, 0)

    def test_qa_regex(self):
        """Test regex based q and a (works only for qa_reg)"""
        qa_dict = {
                   '\s(?P<time>\d+(?:\.\d+)?).*?What time is it\?': '%(time)s',
                   }
        ec, output = run_qas([self.script_qa, 'whattime'], qa_reg=qa_dict)
        self.assertEqual(ec, 0)

    def test_qa_noqa(self):
        """Test noqa"""
        # this has to fail
        qa_dict = {
                   'Now is the time.': 'OK',
                   }
        ec, output = run_qas([self.script_qa, 'waitforit'], qa=qa_dict)
        self.assertEqual(ec, RUNRUN_QA_MAX_MISS_EXITCODE)

        # this has to work
        no_qa = ['Wait for it \(\d+ seconds\)']
        ec, output = run_qas([self.script_qa, 'waitforit'], qa=qa_dict, no_qa=no_qa)
        self.assertEqual(ec, 0)

    def test_qa_list_of_answers(self):
        """Test qa with list of answers."""
        # test multiple answers in qa
        qa_dict = {
            "Enter a number ('0' to stop):": ['1', '2', '4', '0'],
        }
        ec, output = run_qas([self.script_qa, 'ask_number', '4'], qa=qa_dict)
        self.assertEqual(ec, 0)
        answer_re = re.compile(".*Answer: 7$")
        self.assertTrue(answer_re.match(output), "'%s' matches pattern '%s'" % (output, answer_re.pattern))

        # test multple answers in qa_reg
        # and test premature exit on 0 while we're at it
        qa_reg_dict = {
            "Enter a number \(.*\):": ['2', '3', '5', '0'] + ['100'] * 100,
        }
        ec, output = run_qas([self.script_qa, 'ask_number', '100'], qa_reg=qa_reg_dict)
        self.assertEqual(ec, 0)
        answer_re = re.compile(".*Answer: 10$")
        self.assertTrue(answer_re.match(output), "'%s' matches pattern '%s'" % (output, answer_re.pattern))

        # verify type checking on answers
        self.assertErrorRegex(TypeError, "Invalid type for answer", run_qas, [], qa={'q': 1})

        # test more questions than answers, both with and without cycling
        qa_reg_dict = {
            "Enter a number \(.*\):": ['2', '7'],
        }
        # loop 3 times, with cycling (the default) => 2 + 7 + 2 + 7 = 18
        self.assertTrue(RunQAShort.CYCLE_ANSWERS)
        orig_cycle_answers = RunQAShort.CYCLE_ANSWERS
        RunQAShort.CYCLE_ANSWERS = True
        ec, output = run_qas([self.script_qa, 'ask_number', '4'], qa_reg=qa_reg_dict)
        self.assertEqual(ec, 0)
        answer_re = re.compile(".*Answer: 18$")
        self.assertTrue(answer_re.match(output), "'%s' matches pattern '%s'" % (output, answer_re.pattern))
        # loop 3 times, no cycling => 2 + 7 + 7 + 7 = 23
        RunQAShort.CYCLE_ANSWERS = False
        ec, output = run_qas([self.script_qa, 'ask_number', '4'], qa_reg=qa_reg_dict)
        self.assertEqual(ec, 0)
        answer_re = re.compile(".*Answer: 23$")
        self.assertTrue(answer_re.match(output), "'%s' matches pattern '%s'" % (output, answer_re.pattern))
        # restore
        RunQAShort.CYCLE_ANSWERS = orig_cycle_answers


def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestRun)

if __name__ == '__main__':
    main()
