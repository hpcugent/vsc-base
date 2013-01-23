##
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
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# vsc-base is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with vsc-base. If not, see <http://www.gnu.org/licenses/>.
##
"""
@author: Andy Georges

Unit tests for vsc.utils.cache
"""

import os
import tempfile
import time
import sys
from paycheck import with_checker, irange
from unittest import TestCase, TestLoader, main

from vsc.utils.cache import FileCache


class TestCache(TestCase):

    @with_checker({int: int}, irange(0, sys.maxint))
    def test_contents(self, data, threshold):
        """Check that the contents of the cache is what is expected prior to closing it."""
        # create a tempfilename
        (handle, filename) = tempfile.mkstemp(dir='/tmp')
        os.unlink(filename)
        cache = FileCache(filename)
        for (key, value) in data.items():
            cache.update(key, value, threshold)

        now = time.time()
        for key in data.keys():
            info = cache.load(key)
            self.assertFalse(info is None)
            (ts, value) = info
            self.assertTrue(value == data[key])
            self.assertTrue(ts <= now)


    @with_checker({int: int}, irange(0, sys.maxint))
    def test_save_and_load(self, data, threshold):
        """Check if the loaded data is the same as the saved data."""

        # create a tempfilename
        (handle, filename) = tempfile.mkstemp()
        os.unlink(filename)
        cache = FileCache(filename)
        for (key, value) in data.items():
            cache.update(key, value, threshold)
        cache.close()

        now = time.time()
        new_cache = FileCache(filename)
        for key in data.keys():
            info = cache.load(key)
            self.assertTrue(info is not None)
            (ts, value) = info
            self.assertTrue(value == data[key])
            self.assertTrue(ts <= now)
        new_cache.close()

        os.unlink(filename)

def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestCache)

if __name__ == '__main__':
    main()
