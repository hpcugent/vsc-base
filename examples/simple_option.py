#!/usr/bin/env python
#
# Copyright 2011-2013 Ghent University
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
An example how simple_option can do its magic.

Run it with -h and/or -H to see the help functions.

To see it do something, try
python examples/simple_option.py --info -L itjustworks

@author: Stijn De Weirdt (Ghent University)
"""
import logging
from vsc.utils.generaloption import simple_option

# dict = {longopt:(help_description,type,action,default_value,shortopt),}
options = {'long1':('1st long option', None, 'store', 'excellent', 'L')}

go = simple_option(options)

go.log.info("1st option %s" % go.options.long1)
go.log.debug("DEBUG 1st option %s" % go.options.long1)

logging.info("logging from logging.info (eg from 3rd party module)")
logging.debug("logging with logging.root root %s", logging.root)
