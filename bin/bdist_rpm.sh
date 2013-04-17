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

all_packages=
edit=
release=

which rpmrebuild >& /dev/null
if [ $? -gt 0 ]
then
    echo "Missing rpmrebuild"
    exit 1
fi

while getopts er:p:h name
do
    case $name in
	e) edit="-e";;
	r) release="$OPTARG";;
	p) all_packages="$OPTARG";;
	h) printf "Usage: %s [-e] [-r RELEASE] [-p PACKAGE]" $0
	    echo
	    echo "  -e            Edit the generated spec file before rebuilding the RPM"
	    echo "  -r [RELEASE]  Specify the RELEASE tag given to the RPM. Automagically adds .ug.noarch"
	    echo "  -p [PACKAGE]  Specify a single PACKAGE to be built. Default builds all packages."
	    exit 1;;
    esac
done

if [ ! -f bdist_rpm_settings.sh ]; then
    echo "No bdist_rpm_settings.sh found. Cowardly refusing to continue. Bye."
    exit 1
fi

source bdist_rpm_settings.sh

package=$all_packages
echo $package
python ./setup.py bdist_rpm
rpm_target=`ls dist/${package}*noarch.rpm`
rpm_target_name=`basename ${rpm_target}`

if [ ! -f "setup.cfg" ]
then
    echo "No setup.cfg. Cowardly refusing to continue."
    exit 1
fi
  # user specified requirements can be found in setup.cfg
  requirements=`grep "requires" setup.cfg | cut -d" " -f3- | tr "," "\n" | grep -vE "(^python-)|(-python$)|(_python)|(python_)" | tr "\n" "|" | sed -e 's/|$//'`
if [ -z "$requirements" ]; then
    echo "No requirements found."
    requirements="well-now-there-is-no-match-is-there"
fi

if [ -z "$release" ]; then
    release="\\2"
fi

rpmrebuild --define "_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm" \
    --change-spec-preamble="sed -e 's/^Name:\(\s\s*\)\(.*\)/Name:\1python-\2/'" \
    --change-spec-provides="sed -e 's/${package}/python-${package}/g'" \
    --change-spec-requires="sed -r 's/^Requires:(\s\s*)(${requirements})/Requires:\1python-\2/'" \
    --change-spec-preamble="sed -e 's/^\(Release:\s\s*\)\(.*\)\s*$/\1${release}.ug/'" \
    --directory=./dist/ \
    ${edit} -n -p ${rpm_target}
