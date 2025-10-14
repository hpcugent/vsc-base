#
# Copyright 2012-2025 Ghent University
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
Unit tests for asyncprocess.py.

@author: Toon Willems (Ghent University)
@author: Stijn De Weirdt (Ghent University)
"""

import os
import time
from vsc.install.testing import TestCase

import vsc.utils.asyncprocess as p
from vsc.utils.asyncprocess import Popen


def p_recv_some_exception(*args, **kwargs):
    """Call recv_some with raise exception enabled"""
    kwargs['e'] = True
    return p.recv_some(*args, **kwargs)


class AsyncProcessTest(TestCase):
    """ Testcase for asyncprocess """

    def setUp(self):
        """ setup a basic shell """
        self.shell = Popen('sh', stdin=p.PIPE, stdout=p.PIPE, shell=True, executable='/bin/bash')
        self.cwd = os.getcwd()
        super().setUp()

    def runTest(self):
        """ try echoing some text and see if it comes back out """
        p.send_all(self.shell, "echo hello\n")
        time.sleep(0.1)
        self.assertEqual(p.recv_some(self.shell), b"hello\n")

        p.send_all(self.shell, "echo hello world\n")
        time.sleep(0.1)
        self.assertEqual(p.recv_some(self.shell), b"hello world\n")

        p.send_all(self.shell, "exit\n")
        time.sleep(0.2)
        self.assertEqual(b"", p.recv_some(self.shell, e=False))
        self.assertRaises(Exception, p_recv_some_exception, self.shell)

    def tearDown(self):
        """cleanup"""
        os.chdir(self.cwd)
