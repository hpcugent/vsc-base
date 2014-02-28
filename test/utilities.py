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
Test utilities.

@author: Kenneth Hoste (Ghent University)
"""

import re
import sys
from unittest import TestCase


class EnhancedTestCase(TestCase):
    """Enhanced test case, provides extra functionality (e.g. an assertErrorRegex method)."""

    def assertErrorRegex(self, error, regex, call, *args, **kwargs):
        """Convenience method to match regex with the expected error message"""
        try:
            call(*args, **kwargs)
            str_kwargs = ', '.join(['='.join([k,str(v)]) for (k,v) in kwargs.items()])
            str_args = ', '.join(map(str, args) + [str_kwargs])
            self.assertTrue(False, "Expected errors with %s(%s) call should occur" % (call.__name__, str_args))
        except error, err:
            if hasattr(err, 'msg'):
                msg = str(err.msg)
            elif hasattr(err, 'message'):
                msg = str(err.message)
            else:
                msg = str(err)
            self.assertTrue(re.search(regex, msg), "Pattern '%s' is found in '%s'" % (regex, msg))

