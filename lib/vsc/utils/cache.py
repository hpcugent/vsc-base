#!/usr/bin.env python
##
#
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
"""
Caching utilities.
"""
try:
    import cPickle as pickle
except:
    import pickle

import os
import time

from vsc import fancylogger


class FileCache(object):
    """File cache with a timestamp safety.

    Stores data (something that can be pickled) into a dictionary
    indexed by the data.key(). The value stored is a tuple consisting
    of (the time of addition to the dictionary, the complete
    data instance).
    """

    def __init__(self, filename):
        """Initializer.

        Checks if the file can be accessed and load the data therein if any. If the file does not yet exist, start
        with an empty shelf. This ensures that old data is readily available when the FileCache instance is created.
        The file is closed after reading the data.

        @type filename: string

        @param filename: (absolute) path to the cache file.
        """

        self.log = fancylogger.getLogger(self.__class__.__name__)
        self.filename = filename

        if not os.access(self.filename, os.R_OK):
            self.log.error("Could not access the file cache at %s" % (self.filename))
            self.shelf = {}
        else:
            f = open(self.filename, 'r')
            try:
                self.shelf = pickle.load(f)
            except Exception, err:
                self.log.error("Could not load pickle data from %s (%s)" % (self.filename, err))
                self.shelf = {}
            f.close()
        if not self.shelf:
            self.log.info("Loaded empty shelf from %s" % (self.filename))
        self.new_shelf = {}

    def update(self, data, threshold):
        """Update the given data if the existing data is older than the given threshold.

        @type data: an instance that implements a key() method. key() returns a
                    string that uniquely corresponds to this data instance. Note that hash is fubar (see XXX)
        @type threshold: int

        @param data: whatever needs to be stored
        @param threshold: time in seconds
        """
        now = time.time()
        key = data.key()
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

        @returns: (timestamp, data) if there is data foer the given key, None otherwise.
        """
        return  self.shelf.get(key, None)

    def close(self):
        """Close the cache."""

        f = open(self.filename, 'w')
        if not f:
            self.log.error('cannot open the file cache at %s for writing' % (self.filename))
        else:
            pickle.dump(self.new_shelf, f)
            f.close()
            self.log.info('closing the file cache at %s' % (self.filename))
