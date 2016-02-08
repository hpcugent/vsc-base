#
# Copyright 2014-2016 Ghent University
#
# This file is part of vsc-base,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
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
Tests for the vsc.utils.wrapper module.

@author: Stijn De Weirdt (Ghent University)
"""
from vsc.install.testing import TestCase

from vsc.utils.wrapper import Wrapper


class TestWrapper(TestCase):
    """Test for the Wrapper class."""
    def test_wrapper(self):
        """Use the tests provided by the stackoverflow page"""
        class DictWrapper(Wrapper):
            __wraps__ = dict

        wrapped_dict = DictWrapper(dict(a=1, b=2, c=3))

        self.assertTrue("b" in wrapped_dict)  # __contains__
        self.assertEqual(wrapped_dict, dict(a=1, b=2, c=3))  # __eq__
        self.assertTrue("'a': 1" in str(wrapped_dict))  # __str__
        self.assertTrue(wrapped_dict.__doc__.startswith("dict()"))  # __doc__


def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestWrapper)
