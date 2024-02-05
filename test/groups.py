#
# Copyright 2012-2024 Ghent University
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
tests for groups module
"""
import pwd
import logging

# Uncomment when debugging, cannot enable permanetnly, messes up tests that toggle debugging
#logging.basicConfig(level=logging.DEBUG)

from vsc.install.testing import TestCase

from vsc.utils.groups import getgrouplist
from vsc.utils.run import run

class GroupsTest(TestCase):
    """TestCase for groups"""

    def test_getgrouplist(self):
        """Test getgrouplist"""
        for user in pwd.getpwall():
            gidgroups = sorted(getgrouplist(user.pw_uid))
            namegroups = sorted(getgrouplist(user.pw_name))

            # get named groups from id
            #   grp.getgrall is wrong, e.g. for root user on F30,
            #   gr_mem for root group is empty (as is entry in /etc/group),
            #   while id returns 1 group
            #groups = [g.gr_name for g in grp.getgrall() if user.pw_name in g.gr_mem]
            ec, groups_txt = run(['id', '-Gn', user.pw_name])
            groups = sorted(groups_txt.strip().split())

            logging.debug("User %s gidgroups %s namegroups %s groups %s",
                          user, gidgroups, namegroups, groups)
            self.assertEqual(gidgroups, namegroups)
            self.assertEqual(gidgroups, groups)
