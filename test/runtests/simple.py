#
# Copyright 2016-2020 Ghent University
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
Simple, ugly test script
"""
import time
import os
import sys

EC_SUCCES = 0
EC_NOARGS = 1

txt = []
ec = EC_SUCCES

if 'shortsleep' in sys.argv:
    time.sleep(0.1)
    txt.append("Shortsleep completed")

if 'longsleep' in sys.argv:
    time.sleep(10)
    txt.append("Longsleep completed")

if __name__ == '__main__':
    if len(txt) == 0:
        txt.append('Nothing passed')
        ec = EC_NOARGS
    print "\n".join(txt)
    sys.exit(ec)
