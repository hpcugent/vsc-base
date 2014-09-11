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
@author: Kenneth Hoste (Ghent University)
"""
import os
import shutil
import stat
import tempfile
from test.utilities import EnhancedTestCase
from unittest import TestLoader, main

from vsc.utils.filetools import mkdir, read_file, write_file


class TestFileTools(EnhancedTestCase):
    """Tests for vsc.utils.filetools module."""

    def test_mkdir(self):
        """Test mkdir function."""
        tmpdir = tempfile.mkdtemp()

        def check_mkdir(path, error=None, **kwargs):
            """Create specified directory with mkdir, and check for correctness."""
            if error is None:
                mkdir(path, **kwargs)
                self.assertTrue(os.path.exists(path) and os.path.isdir(path), "Directory %s exists" % path)
            else:
                self.assertErrorRegex(Exception, error, mkdir, path, **kwargs)

        foodir = os.path.join(tmpdir, 'foo')
        barfoodir = os.path.join(tmpdir, 'bar', 'foo')
        check_mkdir(foodir)
        # no error on existing paths
        check_mkdir(foodir)
        # no recursion by defaults, requires parents=True
        check_mkdir(barfoodir, error="Failed.*No such file or directory")
        check_mkdir(barfoodir, parents=True)
        check_mkdir(os.path.join(barfoodir, 'bar', 'foo', 'trolololol'), parents=True)
        # group ID and sticky bits are disabled by default
        self.assertFalse(os.stat(foodir).st_mode & (stat.S_ISGID | stat.S_ISVTX), "no gid/sticky bit %s" % foodir)
        self.assertFalse(os.stat(barfoodir).st_mode & (stat.S_ISGID | stat.S_ISVTX), "no gid/sticky bit %s" % barfoodir)
        # setting group ID bit works
        giddir = os.path.join(foodir, 'gid')
        check_mkdir(giddir, set_gid=True)
        self.assertTrue(os.stat(giddir).st_mode & stat.S_ISGID, "gid bit set %s" % giddir)
        self.assertFalse(os.stat(giddir).st_mode & stat.S_ISVTX, "no sticky bit %s" % giddir)
        # setting stciky bit works
        stickydir = os.path.join(barfoodir, 'sticky')
        check_mkdir(stickydir, sticky=True)
        self.assertFalse(os.stat(stickydir).st_mode & stat.S_ISGID, "no gid bit %s" % stickydir)
        self.assertTrue(os.stat(stickydir).st_mode & stat.S_ISVTX, "sticky bit set %s" % stickydir)
        # setting both works, bits are set for all new subdirectories
        stickygiddirs = [os.path.join(foodir, 'new')]
        stickygiddirs.append(os.path.join(stickygiddirs[-1], 'sticky'))
        stickygiddirs.append(os.path.join(stickygiddirs[-1], 'and'))
        stickygiddirs.append(os.path.join(stickygiddirs[-1], 'gid'))
        check_mkdir(stickygiddirs[-1], parents=True, set_gid=True, sticky=True)
        for subdir in stickygiddirs:
            gid_or_sticky = stat.S_ISGID | stat.S_ISVTX
            self.assertEqual(os.stat(subdir).st_mode & gid_or_sticky, gid_or_sticky, "gid bit set %s" % subdir)
        # existing parent dirs are untouched, no sticky/group ID bits set
        self.assertFalse(os.stat(foodir).st_mode & (stat.S_ISGID | stat.S_ISVTX), "no gid/sticky bit %s" % foodir)
        self.assertFalse(os.stat(barfoodir).st_mode & (stat.S_ISGID | stat.S_ISVTX), "no gid/sticky bit %s" % barfoodir)

        shutil.rmtree(tmpdir)

    def test_read_write_file(self):
        """Test reading/writing files."""
        tmpdir = tempfile.mkdtemp()

        fp = os.path.join(tmpdir, 'test.txt')
        txt = "test123"
        write_file(fp, txt)
        self.assertEqual(read_file(fp), txt)

        txt2 = '\n'.join(['test', '123'])
        write_file(fp, txt2, append=True)
        self.assertEqual(read_file(fp), txt+txt2)

        self.assertErrorRegex(Exception, 'Failed to read', read_file, '/no/such/file')

        shutil.rmtree(tmpdir)


def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestFileTools)


if __name__ == '__main__':
    #logToScreen(enable=True)
    #setLogLevelDebug()
    main()
