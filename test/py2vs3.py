#
# Copyright 2020-2020 Ghent University
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
Tests for the vsc.utils.py2vs3 module.

@author: Kenneth Hoste (Ghent University)
"""
import os
import sys

from vsc.utils.py2vs3 import is_py_ver, is_py2, is_py3, is_string, pickle
from vsc.install.testing import TestCase


class TestPy2vs3(TestCase):
    """Test for vsc.utils.py2vs3 module."""

    def test_is_py_ver(self):
        """Tests for is_py_ver, is_py2, is_py3 functions."""

        maj_ver = sys.version_info[0]
        min_ver = sys.version_info[1]

        if maj_ver >= 3:
            self.assertFalse(is_py2())
            self.assertFalse(is_py_ver(2))
            self.assertFalse(is_py_ver(2, 4))
            self.assertFalse(is_py_ver(2, min_ver=6))
            self.assertTrue(is_py3())
            self.assertTrue(is_py_ver(3))
            self.assertTrue(is_py_ver(3, min_ver))
            self.assertTrue(is_py_ver(3, min_ver=min_ver))
            if min_ver >= 6:
                self.assertTrue(is_py_ver(3, 6))
                self.assertTrue(is_py_ver(3, min_ver=6))
                self.assertFalse(is_py_ver(3, 99))
                self.assertFalse(is_py_ver(3, min_ver=99))
        else:
            # must be Python 2.6 or more recent Python 2 nowdays
            self.assertTrue(is_py2())
            self.assertTrue(is_py_ver(2))
            self.assertTrue(is_py_ver(2, 4))
            self.assertTrue(is_py_ver(2, min_ver=6))
            self.assertFalse(is_py3())
            self.assertFalse(is_py_ver(3))
            self.assertFalse(is_py_ver(3, 6))
            self.assertFalse(is_py_ver(3, min_ver=6))

    def test_is_string(self):
        """Tests for is_string function."""
        for item in ['foo', u'foo', "hello world", """foo\nbar""", '']:
            self.assertTrue(is_string(item))

        for item in [1, None, ['foo'], ('foo',), {'foo': 'bar'}]:
            self.assertFalse(is_string(item))

        if is_py3():
            self.assertFalse(is_string(b'bytes_are_not_a_string'))
        else:
            # in Python 2, b'foo' is really just a regular string
            self.assertTrue(is_string(b'foo'))

    def test_picke(self):
        """Tests for pickle module provided by py2vs3."""

        test_pickle_file = os.path.join(self.tmpdir, 'test.pickle')

        test_dict = {1: 'one', 2: 'two'}

        fp = open(test_pickle_file, 'wb')
        pickle.dump(test_dict, fp)
        fp.close()

        self.assertTrue(os.path.exists(test_pickle_file))

        fp = open(test_pickle_file, 'rb')
        loaded_pickle = pickle.load(fp)
        fp.close()

        self.assertEqual(test_dict, loaded_pickle)
