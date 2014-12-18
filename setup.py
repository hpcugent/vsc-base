#!/usr/bin/env python
# -*- coding: latin-1 -*-
#
# Copyright 2009-2014 Ghent University
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
#
"""
vsc-base base distribution setup.py

@author: Stijn De Weirdt (Ghent University)
@author: Andy Georges (Ghent University)
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import vsc.install.shared_setup as shared_setup
from vsc.install.shared_setup import ag, jt, sdw

def remove_bdist_rpm_source_file():
    """List of files to remove from the (source) RPM."""
    return []

shared_setup.remove_extra_bdist_rpm_files = remove_bdist_rpm_source_file
shared_setup.SHARED_TARGET.update({
    'url': 'https://github.com/hpcugent/vsc-base',
    'download_url': 'https://github.com/hpcugent/vsc-base'
})


PACKAGE = {
    'name': 'vsc-base',
    'version': '2.0.0',
    'author': [sdw, jt, ag],
    'maintainer': [sdw, jt, ag],
    'packages': ['vsc', 'vsc.utils', 'vsc.install'],
    'scripts': ['bin/logdaemon.py', 'bin/startlogdaemon.sh', 'bin/bdist_rpm.sh', 'bin/optcomplete.bash'],
    'install_requires' : ['setuptools'],
}

if __name__ == '__main__':
    shared_setup.action_target(PACKAGE)
