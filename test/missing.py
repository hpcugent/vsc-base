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
from test.utilities import EnhancedTestCase
from unittest import TestLoader, main

from vsc.utils.fancylogger import setLogLevelDebug, logToScreen
from vsc.utils.missing import nub, TryOrFail, ConstantDict


class TestMissing(EnhancedTestCase):
    """Test for vsc.utils.missing module."""

    @with_checker([int])
    def test_nub_length(self, list_of_ints):
        nubbed = nub(list_of_ints)
        self.assertTrue(len(list_of_ints) >= len(nubbed))

    @with_checker([int])
    def test_nub_membership(self, list_of_ints):
        nubbed = nub(list_of_ints)
        for x in list_of_ints:
            self.assertTrue(x in nubbed)

    @with_checker([int])
    def test_nub_order(self, list_of_ints):
        nubbed = nub(2 * list_of_ints)
        for (x, y) in [(x_, y_) for x_ in list_of_ints for y_ in list_of_ints]:
            self.assertTrue((list_of_ints.index(x) <= list_of_ints.index(y)) == (nubbed.index(x) <= nubbed.index(y)))

    def test_tryorfail_no_sleep(self):
        """test for a retry that succeeds."""

        raise_boundary = 2

        @TryOrFail(3, (Exception,), 0)
        def f(i):
            if i < raise_boundary:
                raise Exception
            else:
                return i

        for n in xrange(0, 2 * raise_boundary):
            try:
                v = f(n)
                self.assertFalse(n < raise_boundary)
                self.assertTrue(v == n)
            except:
                self.assertTrue(n < raise_boundary)

    def test_constant_dict(self):
        """Tests for ConstantDict."""
        cd = ConstantDict()
        cd.KNOWN_KEYS = ['foo', 'bar']

        # setting values works fine
        cd['foo'] = 'FOO'
        self.assertEqual(cd['foo'], 'FOO')

        # updated method can be used, is_defined class variable is set to True
        cd.update({
            'foo': 'FOOFOO',
            'bar': 'BAR',
        })
        cd.set_defined()
        self.assertTrue(cd.is_defined)
        self.assertEqual(cd['foo'], 'FOOFOO')
        self.assertEqual(cd['bar'], 'BAR')

        # further updates are prohibited after a call to the is_defined method
        msg = "Modifying key '.*' is prohibited after set_defined\(\)"
        self.assertErrorRegex(Exception, msg, cd.update, {'foo': 'BAR'})
        self.assertErrorRegex(Exception, msg, cd.__setitem__, 'foo', 'BAR')

        # only valid keys can be set
        cd = ConstantDict()
        msg = "Key 'thisisclearlynotavalidkey' \(value: 'FAIL'\) is not valid \(valid keys: .*\)"
        self.assertErrorRegex(Exception, msg, cd.update, {'thisisclearlynotavalidkey': 'FAIL'})

        # different KeyError messages for unknown and missing keys
        cd = ConstantDict()
        cd.KNOWN_KEYS = ['foo', 'bar']
        self.assertErrorRegex(KeyError, "^\'foo\'$", cd.__getitem__, 'foo')
        self.assertErrorRegex(KeyError, "unknown key '.*', known keys: .*", cd.__getitem__, 'thisisclearlynotavalidkey')

        # the update_skip_unknown method simply ignores unknown keys (no errors)
        cd.update_skip_unknown({
            'foo': 'BAR',
            'bar': 'FOO',
            'foobar': 'whatever',
        })
        self.assertEqual(cd['foo'], 'BAR')
        self.assertEqual(cd['bar'], 'FOO')
        self.assertTrue(not 'foobar' in cd)

def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestMissing)


if __name__ == '__main__':
    #logToScreen(enable=True)
    #setLogLevelDebug()
    main()
