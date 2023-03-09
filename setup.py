#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Copyright 2009-2023 Ghent University
#
# This file is part of vsc-base,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Flemish Research Foundation (FWO) (http://www.fwo.be/en)
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
#
"""
vsc-base base distribution setup.py

@author: Stijn De Weirdt (Ghent University)
@author: Andy Georges (Ghent University)
@author: Kenneth Hoste (Ghent University)
"""

import vsc.install.shared_setup as shared_setup
from vsc.install.shared_setup import ag, kh, jt, sdw

PACKAGE = {
    'version': '3.5.3',
    'author': [sdw, jt, ag, kh],
    'maintainer': [sdw, jt, ag, kh],
    'install_requires': [
        'vsc-install >= 0.17.19',
    ],
}

if __name__ == '__main__':
    shared_setup.action_target(PACKAGE)
