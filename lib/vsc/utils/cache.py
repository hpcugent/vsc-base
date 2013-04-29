#!/usr/bin.env python
##
#
# Copyright 2012-2013 Ghent University
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
##
"""
Caching utilities.

@author: Andy Georges (Ghent University)
"""
try:
    import cPickle as pickle
except:
    import pickl
import gzip
import json
import time

from vsc import fancylogger


class FileCache(object):
    """File cache with a timestamp safety.

    Stores data (something that can be pickled) into a dictionary
    indexed by the data.key(). The value stored is a tuple consisting
    of (the time of addition to the dictionary, the complete
    data instance).

    By default, only updated entries are stored to the file; old
    entries are discarded. This can be changed by setting a flag
    during instatiation or at run time. The changed behaviour only
    has an effect when closing the cache, i.e., storing it to a file.

    Note that the cache is persistent only when it is closed correctly.
    During a crash of your application ar runtime, the information is
    _not_ written to the file.
    """

    def __init__(self, filename, retain_old=False):
        """Initializer.

        Checks if the file can be accessed and load the data therein if any. If the file does not yet exist, start
        with an empty shelf. This ensures that old data is readily available when the FileCache instance is created.
        The file is closed after reading the data.

        @type filename: string

        @param filename: (absolute) path to the cache file.
        """

        self.log = fancylogger.getLogger(self.__class__.__name__)
        self.filename = filename
        self.retain_old = retain_old

        try:
            f = open(self.filename, 'rb')
            try:
                f = gzip.GzipFile(mode='rb', fileobj=f)
                self.shelf = json.load(f)
            except IOError, err:
                try:
                    self.shelf = pickle.load(f)
                except (OSError, IOError):
                    self.log.raiseException("Could not load pickle data from %s" % (self.filename))
            finally:
                f.close()
        except (OSError, IOError), err:
            self.log.warning("Could not access the file cache at %s [%s]" % (self.filename, err))
            self.shelf = {}

        if not self.shelf:
            self.log.info("Cache in %s starts with an empty shelf" % (self.filename))

        self.new_shelf = {}

    def update(self, key, data, threshold):
        """Update the given data if the existing data is older than the given threshold.

        @type key: something that can serve as a dictionary key (and thus can be pickled)
        @type data: something that can be pickled
        @type threshold: int

        @param key: identification of the data item
        @param data: whatever needs to be stored
        @param threshold: time in seconds
        """
        now = time.time()
        old = self.load(key)
        if old:
            (ts, _) = old
            if now - ts > threshold:
                self.new_shelf[key] = (now, data)
            else:
                self.new_shelf[key] = old
        else:
            self.new_shelf[key] = (now, data)

    def load(self, key):
        """Load the stored data for the given key along with the timestamp it was stored.

        @type key: anything that can serve as a dictionary key

        @returns: (timestamp, data) if there is data for the given key, None otherwise.
        """
        return self.shelf.get(key, None) or self.new_shelf.get(key, None)

    def retain(self):
        """Retain non-updated data on close."""
        self.retain_old = True

    def discard(self):
        """Discard non-updated data on close."""
        self.retain_old = False

    def close(self):
        """Close the cache."""

        f = open(self.filename, 'wb')
        if not f:
            self.log.error('cannot open the file cache at %s for writing' % (self.filename))
        else:
            if self.retain_old:
                self.shelf.update(self.new_shelf)
                self.new_shelf = self.shelf

            pickle.dump(self.new_shelf, f)
            f.close()
            self.log.info('closing the file cache at %s' % (self.filename))
