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
import configparser  # noqa
import pickle  # noqa
from io import StringIO  # noqa
from shlex import quote  # noqa
from tempfile import TemporaryDirectory  # noqa
from urllib.parse import urlencode, unquote  # noqa
from urllib.request import HTTPError, HTTPSHandler, Request, build_opener, urlopen  # noqa
from collections.abc import Mapping  # noqa

FileExistsErrorExc = FileExistsError  # noqa
FileNotFoundErrorExc = FileNotFoundError  # noqa


def is_string(value):
    """Check whether specified value is of type string (not bytes)."""
    return isinstance(value, str)


def ensure_ascii_string(value):
    """
    Convert the provided value to an ASCII string (no Unicode characters).
    """
    if isinstance(value, bytes):
        # if we have a bytestring, decode it to a regular string using ASCII encoding,
        # and replace Unicode characters with backslash escaped sequences
        value = value.decode('ascii', 'backslashreplace')
    else:
        # for other values, just convert to a string (which may still include Unicode characters)
        # then convert to bytestring with UTF-8 encoding,
        # which can then be decoded to regular string using ASCII encoding
        value = bytes(str(value), encoding='utf-8').decode(encoding='ascii', errors='backslashreplace')

    return value
