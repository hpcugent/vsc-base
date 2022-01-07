#
# Copyright 2020-2022 Ghent University
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
Utility functions to help with keeping the codebase compatible with both Python 2 and 3.

@author: Kenneth Hoste (Ghent University)
"""
# declare vsc.utils.py2vs3 namespace
# (must be exactly like this to avoid vsc-install complaining)
import pkg_resources
pkg_resources.declare_namespace(__name__)


import sys


def is_py_ver(maj_ver, min_ver=0):
    """Check whether current Python version matches specified version specs."""

    curr_ver = sys.version_info

    lower_limit = (maj_ver, min_ver)
    upper_limit = (maj_ver + 1, 0)

    return lower_limit <= curr_ver < upper_limit


def is_py2():
    """Determine whether we're using Python 3."""
    return is_py_ver(2)


def is_py3():
    """Determine whether we're using Python 3."""
    return is_py_ver(3)


# all functionality provided by the py2 and py3 modules is made available via the easybuild.tools.py2vs3 namespace
if is_py3():
    from vsc.utils.py2vs3.py3 import *  # noqa
else:
    from vsc.utils.py2vs3.py2 import *  # noqa
