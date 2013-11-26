#!/usr/bin/env python
##
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
##
"""
Tests for the vsc.utils.missing module.

@author: Andy Georges (Ghent University)
"""
from paycheck import with_checker
from unittest import TestCase, TestLoader

from vsc.utils.missing import nub
from vsc.utils.missing import TryOrFail


class TestNub(TestCase):
    """Test for the nub function."""

    @with_checker([int])
    def test_length(self, list_of_ints):
        nubbed = nub(list_of_ints)
        self.assertTrue(len(list_of_ints) >= len(nubbed))

    @with_checker([int])
    def test_membership(self, list_of_ints):
        nubbed = nub(list_of_ints)
        for x in list_of_ints:
            self.assertTrue(x in nubbed)

    @with_checker([int])
    def test_order(self, list_of_ints):
        nubbed = nub(2 * list_of_ints)
        for (x, y) in [(x_, y_) for x_ in list_of_ints for y_ in list_of_ints]:
            self.assertTrue((list_of_ints.index(x) <= list_of_ints.index(y)) == (nubbed.index(x) <= nubbed.index(y)))


class TestTryOrFail(TestCase):
    """Test for the try_or_fail decorator."""

    def test_retry(self):
        """test for a retry that succeeds."""
        @TryOrFail(3, (Exception,), 0)
        def f(i):
            if i < 10:
                raise Exception
            else:
                return i

        for n in xrange(0,20):
            try:
                v = f(n)
                self.assertTrue(n >= 10)
                self.assertTrue(v == n)
            except:
                self.assertTrue(n < 10)


def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCasestsFromTestCase(TestNub)
