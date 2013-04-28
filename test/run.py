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
import os
import time
from unittest import TestCase, TestLoader

from vsc.utils.run import run_simple, run_asyncloop, run_timeout, run_qa
from vsc.utils.run import RUNRUN_TIMEOUT_OUTPUT, RUNRUN_TIMEOUT_EXITCODE

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), 'runtests')
SCRIPT_SIMPLE = os.path.join(SCRIPT_DIR, 'simple.py')
SCRIPT_QA = os.path.join(SCRIPT_DIR, 'qa.py')


class TestRun(TestCase):
    """Test for the run module."""
    def test_simple(self):
        ec, output = run_simple([SCRIPT_SIMPLE, 'shortsleep'])
        self.assertEqual(ec, 0)
        self.assertTrue('shortsleep' in output.lower())

    def test_simple_asyncloop(self):
        ec, output = run_asyncloop([SCRIPT_SIMPLE, 'shortsleep'])
        self.assertEqual(ec, 0)
        self.assertTrue('shortsleep' in output.lower())

    def test_timeout(self):
        start = time.time()
        timeout = 3
        # longsleep is 10sec
        ec, output = run_timeout([SCRIPT_SIMPLE, 'longsleep'], timeout=timeout)
        stop = time.time()
        self.assertEqual(ec, RUNRUN_TIMEOUT_EXITCODE)
        self.assertTrue(RUNRUN_TIMEOUT_OUTPUT == output)
        self.assertTrue(stop - start < timeout + 1)  # give 1 sec margin

    def test_qa(self):
        ec, output = run_qa([SCRIPT_QA, 'noquestion'])
        self.assertEqual(ec, 0)

        qa_dict = {
                   'Simple question:': 'simple answer',
                   }
        ec, output = run_qa([SCRIPT_QA, 'simple'], qa=qa_dict)
        self.assertEqual(ec, 0)


def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestRun)
