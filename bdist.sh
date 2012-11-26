#!/bin/bash

# Copyright 2012 Ghent University
# Copyright 2012 Andy Georges
#
# This file is part of VSC-tools,
# originally created by the HPC team of Ghent University (http://ugent.be/hpc/en),
# with support of Ghent University (http://ugent.be/hpc),
# the Flemish Supercomputer Centre (VSC) (https://vscentrum.be/nl/en),
# the Hercules foundation (http://www.herculesstichting.be/in_English)
# and the Department of Economy, Science and Innovation (EWI) (http://www.ewi-vlaanderen.be/en).
#
# http://github.com/hpcugent/VSC-tools
#
# VSC-tools is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# VSC-tools is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with VSC-tools. If not, see <http://www.gnu.org/licenses/>.
##

# This script will generate the RPMs for deployment on some system, prefixing the Python package names with python-
# to indicate their contents in a more appropriate way. We do not do this for the packages when shipped to
# PyPi, since it is pretty obvious these are Python packages in any case.



ALL_PACKAGES=`python ./setup.py --name 2>/dev/null | tr "\n" " "`

for package in $ALL_PACKAGES; do
  echo $package
  python ./setup.py ${package} bdist_rpm
  rpm_target=`ls dist/${package}*noarch.rpm`
  rpm_target_name=`basename ${rpm_target}`
  rpmrebuild --define "_rpmfilename python-${rpm_target_name}" \
             --change-spec-preamble="sed -e 's/^Name:\(\s\s*\)\(.*\)/Name:\1python-\2/'" \
             --change-spec-provides="sed 's/${package}/python-${package}/g'" \
             -n -p ${rpm_target}
done
