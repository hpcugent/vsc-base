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
import cPickle as pickle  # noqa
import ConfigParser as configparser  # noqa
import os  # noqa
from cStringIO import StringIO  # noqa
from pipes import quote  # noqa
from tempfile import mkdtemp  # noqa
from urllib import urlencode, unquote  # noqa
from urllib2 import HTTPError, HTTPSHandler, Request, build_opener, urlopen  # noqa
from collections import Mapping  # noqa

FileExistsErrorExc = OSError  # noqa
FileNotFoundErrorExc = OSError  # noqa


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

# https://stackoverflow.com/questions/19296146/tempfile-temporarydirectory-context-manager-in-python-2-7

class TemporaryDirectory(object):
    """Create and return a temporary directory.  This has the same
    behavior as mkdtemp but can be used as a context manager.  For
    example:

        with TemporaryDirectory() as tmpdir:
            ...

    Upon exiting the context, the directory and everything contained
    in it are removed.
    """

    def __init__(self, suffix="", prefix="tmp", dir=None):  # noqa
        self._closed = False
        self.name = None # Handle mkdtemp raising an exception
        self.name = mkdtemp(suffix, prefix, dir)

    def __repr__(self):
        return "<{} {!r}>".format(self.__class__.__name__, self.name)

    def __enter__(self):
        return self.name

    def cleanup(self):
        if self.name and not self._closed:
            self._rmtree(self.name)
            self._closed = True

    def __exit__(self, exc, value, tb):
        self.cleanup()

    def __del__(self):
        # Issue a ResourceWarning if implicit cleanup needed
        self.cleanup()

    # XXX (ncoghlan): The following code attempts to make
    # this class tolerant of the module nulling out process
    # that happens during CPython interpreter shutdown
    # Alas, it doesn't actually manage it. See issue #10188
    _listdir = staticmethod(os.listdir)
    _path_join = staticmethod(os.path.join)
    _isdir = staticmethod(os.path.isdir)
    _islink = staticmethod(os.path.islink)
    _remove = staticmethod(os.remove)
    _rmdir = staticmethod(os.rmdir)

    def _rmtree(self, path):
        # Essentially a stripped down version of shutil.rmtree.  We can't
        # use globals because they may be None'ed out at shutdown.
        for name in self._listdir(path):
            fullname = self._path_join(path, name)
            try:
                isdir = self._isdir(fullname) and not self._islink(fullname)
            except OSError:
                isdir = False
            if isdir:
                self._rmtree(fullname)
            else:
                try:
                    self._remove(fullname)
                except OSError:
                    pass
        try:
            self._rmdir(path)
        except OSError:
            pass
