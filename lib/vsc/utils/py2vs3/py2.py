#
# Copyright 2020-2020 Ghent University
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
import cPickle as pickle  # noqa
import ConfigParser as configparser  # noqa
from cStringIO import StringIO  # noqa
from pipes import quote  # noqa
from urllib import urlencode, unquote  # noqa
from urllib import quote as urlquote  # noqa
from urllib2 import HTTPError, HTTPSHandler, Request, build_opener, urlopen  # noqa
from collections import Mapping  # noqa


def is_string(value):
    """Check whether specified value is of type string (not bytes)."""
    return isinstance(value, basestring)  # noqa


def ensure_ascii_string(value):
    """
    Convert the provided value to an ASCII string (no Unicode characters).
    """
    if isinstance(value, unicode):  # noqa
        # encode as string, replace non-ASCII characters with backslashed escape sequences
        value = value.encode('ascii', 'backslashreplace')
    elif isinstance(value, str):
        # str-typed values can also include Unicode characters, so strip them out
        # (can't use backslashreplace here, since that triggers error for values that include
        # Unicode characters because UnicodeDecodeError can't be handled?!)
        value = value.decode('ascii', 'ignore')
    else:
        # str will replace Unicode characters with equivalent escape codes (like \xa2)
        value = str(value)

    return value
