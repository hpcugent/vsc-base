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
"""Caching utilities.

Created Mar 15, 2012

@author Andy Georges
"""
import cPickle
import os
import time

import vsc.fancylogger as fancylogger

from vsc.gpfs.utils.exceptions import CriticalException


class FileCache(object):
    """Cached information for VSC users.

    Stores data (something that can be pickled) into a dictionary
    indexed by the data.key(). The value stored is a tuple consisting
    of (the time of addition to the dictionary, the complete
    data instance).
    """

    def __init__(self, filename):
        """Initializer."""
        self.logger = fancylogger.getLogger(self.__class__.__name__)
        self.filename = filename
        if not os.access(self.filename, os.R_OK):
            self.logger.error('Could not access the file cache at %s' % (self.filename))
            self.shelf = {}
        else:
            f = open(self.filename, 'r')
            try:
                self.shelf = cPickle.load(f)
            except Exception, err:
                self.logger.error("Could not load pickle data from %s (%s)" % (self.filename, err))
                self.shelf = {}
            f.close()
        if not self.shelf:
            self.logger.error('Could not load the file cache at %s' % (self.filename))
        self.new_shelf = {}

    def update(self, data, threshold):
        """Update the given data. Will only store the new data if the old data
        is older than the given threshold.

        @type data: an instance that implements a key() method. key() returns a
                    string that uniquely corresponds to a data instance.
        @type threshold: a time in seconds.
        """
        t = time.time()
        old = self.load(data.key())
        if old:
            (ts, _) = old
            if t - ts > threshold:
                self.new_shelf[data.key()] = (t, data)
            else:
                self.new_shelf[data.key()] = old
        else:
            self.new_shelf[data.key()] = (t, data)

    def load(self, key):
        """Load the stored data D for the given key along with the timestamp
        indicating the time the data was stored to the reminderCache.

        Returns (timestamp, D) or None if there is no data for userId in
        the reminderCache.
        """
        v = self.shelf.get(key, None)
        return v

    def close(self):
        """Close the reminderCache."""
        f = open(self.filename, 'w')
        if not f:
            self.logger.error('cannot open the file cache at %s for writing' % (self.filename))
        else:
            cPickle.dump(self.new_shelf, f)
            f.close()
            self.logger.info('closing the file cache at %s' % (self.filename))
