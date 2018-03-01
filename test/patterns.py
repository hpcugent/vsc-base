#
# Copyright 2018-2018 Ghent University
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
Unit tests for the patterns.
"""
from vsc.install.testing import TestCase

from vsc.utils.patterns import Singleton


class ABC(object):
    __metaclass__ = Singleton

    def __init__(self, value):
        """
        Singleton metaclass with init that has args is probably the most stupid thing to have,
        but easy for unittests
        """
        self.value = value

class PatTest(TestCase):
    """
    Simplet tests for the patterns
    """
    def test_singleton(self):

        abc = ABC(1)
        self.assertEqual(abc.value, 1, "init with value 1")

        abc2 = ABC(2)
        self.assertEqual(abc2.value, 1,
                         "2nd init with value 2, gives value from (first) singleton")
        self.assertEqual(id(abc2), id(abc), "2nd instance is identical to 1st")

        abc3 = ABC(2, skip_singleton=True)
        self.assertEqual(abc3.value, 2,
                         "3rd init with value 2 and skip_singleton, gives new instance")
        self.assertNotEqual(id(abc3), id(abc2), "3rd with skip_singleton is different instance from 2nd")

        abc4 = ABC(2, skip_singleton=True)
        self.assertEqual(abc3.value, 2,
                         "4th init with value 2 and skip_singleton, gives new instance")
        self.assertNotEqual(id(abc4), id(abc3), "4th with skip_singleton is different instance from 3rd")
