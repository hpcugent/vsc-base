#!/usr/bin/env python
# #
# Copyright 2012-2014 Ghent University
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
# #
"""
Various functions related to files & directories.

@author: Kenneth Hoste (Ghent University)
"""
import os
import stat

from vsc.utils import fancylogger


_log = fancylogger.getLogger(name='vsc.utils.filetools')


def adjust_permissions(name, permission_bits, add=True, onlyfiles=False, onlydirs=False, recursive=True,
                       group_id=None, relative=True, ignore_errors=False):
    """
    Add or remove (if add is False) permission_bits from all files (if onlydirs is False)
    and directories (if onlyfiles is False) in path
    """

    name = os.path.abspath(name)

    if recursive:
        _log.info("Adjusting permissions recursively for %s" % name)
        allpaths = [name]
        for root, dirs, files in os.walk(name):
            paths = []
            if not onlydirs:
                paths += files
            if not onlyfiles:
                paths += dirs

            for path in paths:
                allpaths.append(os.path.join(root, path))

    else:
        _log.info("Adjusting permissions for %s" % name)
        allpaths = [name]

    failed_paths = []
    fail_cnt = 0
    for path in allpaths:

        try:
            if relative:

                # relative permissions (add or remove)
                perms = os.stat(path)[stat.ST_MODE]

                if add:
                    os.chmod(path, perms | permission_bits)
                else:
                    os.chmod(path, perms & ~permission_bits)

            else:
                # hard permissions bits (not relative)
                os.chmod(path, permission_bits)

            if group_id:
                # only change the group id if it the current gid is different from what we want
                cur_gid = os.stat(path).st_gid
                if not cur_gid == group_id:
                    _log.debug("Changing group id of %s to %s" % (path, group_id))
                    os.chown(path, -1, group_id)
                else:
                    _log.debug("Group id of %s is already OK (%s)" % (path, group_id))

        except OSError, err:
            if ignore_errors:
                # ignore errors while adjusting permissions (for example caused by bad links)
                _log.info("Failed to chmod/chown %s (but ignoring it): %s" % (path, err))
                fail_cnt += 1
            else:
                failed_paths.append(path)

    if failed_paths:
        _log.raiseException("Failed to chmod/chown several paths: %s (last error: %s)" % (failed_paths, err))

    # we ignore some errors, but if there are to many, something is definitely wrong
    fail_ratio = fail_cnt / float(len(allpaths))
    max_fail_ratio = 0.5
    if fail_ratio > max_fail_ratio:
        tup = (100 * fail_ratio, 100 * max_fail_ratio)
        msg = "%.2f%% of permissions/owner operations failed (more than %.2f%%), something must be wrong..." % tup
        _log.raiseException(msg)
    elif fail_cnt > 0:
        _log.debug("%.2f%% of permissions/owner operations failed, ignoring that..." % (100 * fail_ratio))


def mkdir(path, parents=False, set_gid=None, sticky=None):
    """
    Create a directory
    Directory is the path to create

    @param parents: create parent directories if needed (mkdir -p)
    @param set_gid: set group ID bit, to make subdirectories and files inherit group
    @param sticky: set the sticky bit on this directory (a.k.a. the restricted deletion flag),
                   to avoid users can removing/renaming files in this directory
    """
    if not os.path.isabs(path):
        path = os.path.abspath(path)

    # exit early if path already exists
    if not os.path.exists(path):
        tup = (path, parents, set_gid, sticky)
        _log.info("Creating directory %s (parents: %s, set_gid: %s, sticky: %s)" % tup)
        # set_gid and sticky bits are only set on new directories, so we need to determine the existing parent path
        existing_parent_path = os.path.dirname(path)
        try:
            if parents:
                # climb up until we hit an existing path or the empty string (for relative paths)
                while existing_parent_path and not os.path.exists(existing_parent_path):
                    existing_parent_path = os.path.dirname(existing_parent_path)
                os.makedirs(path)
            else:
                os.mkdir(path)
        except OSError, err:
            _log.raiseException("Failed to create directory %s: %s" % (path, err))

        # set group ID and sticky bits, if desired
        bits = 0
        if set_gid:
            bits |= stat.S_ISGID
        if sticky:
            bits |= stat.S_ISVTX
        if bits:
            try:
                new_subdir = path[len(existing_parent_path):].lstrip(os.path.sep)
                new_path = os.path.join(existing_parent_path, new_subdir.split(os.path.sep)[0])
                adjust_permissions(new_path, bits, add=True, relative=True, recursive=True, onlydirs=True)
            except OSError, err:
                _log.raiseException("Failed to set groud ID/sticky bit: %s" % err)
    else:
        _log.debug("Not creating existing path %s" % path)


def read_file(path, log_error=True):
    """Read contents of file at given path, in a robust way."""
    f = None
    # note: we can't use try-except-finally, because Python 2.4 doesn't support it as a single block
    try:
        f = open(path, 'r')
        txt = f.read()
        f.close()
        return txt
    except IOError, err:
        # make sure file handle is always closed
        if f is not None:
            f.close()
        if log_error:
            _log.raiseException("Failed to read %s: %s" % (path, err))
        else:
            return None


def write_file(path, txt, append=False):
    """Write given contents to file at given path (overwrites current file contents!)."""
    f = None
    # note: we can't use try-except-finally, because Python 2.4 doesn't support it as a single block
    try:
        mkdir(os.path.dirname(path), parents=True)
        if append:
            f = open(path, 'a')
        else:
            f = open(path, 'w')
        f.write(txt)
        f.close()
        msg = "File %s written." % path
        _log.info(msg)
    except IOError, err:
        # make sure file handle is always closed
        if f is not None:
            f.close()
        _log.raiseException("Failed to write to %s: %s" % (path, err))
