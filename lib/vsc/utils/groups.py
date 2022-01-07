#
# Copyright 2018-2022 Ghent University
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
This module contains tools related to users and groups
"""
import grp
import pwd
from ctypes import c_char_p, c_uint, c_int32, POINTER, byref, cdll
from ctypes.util import find_library

from vsc.utils.py2vs3 import is_string


def getgrouplist(user, groupnames=True):
    """
    Return a list of all groupid's for groups this user is in
    This function is needed here because python's user database only contains local users, not remote users from e.g.
    sssd
    user can be either an integer (uid) or a string (username)
    returns a list of groupnames
    if groupames is false, returns a list of groupids (skip groupname lookups)
    """
    libc = cdll.LoadLibrary(find_library('libc'))

    getgrouplist = libc.getgrouplist
    # max of 50 groups should be enough as first try
    ngroups = 50
    getgrouplist.argtypes = [c_char_p, c_uint, POINTER(c_uint * ngroups), POINTER(c_int32)]
    getgrouplist.restype = c_int32

    grouplist = (c_uint * ngroups)()
    ngrouplist = c_int32(ngroups)

    if is_string(user):
        user = pwd.getpwnam(user)
    else:
        user = pwd.getpwuid(user)

    # .encode() is required in Python 3, since we need to pass a bytestring to getgrouplist
    user_name, user_gid = user.pw_name.encode(), user.pw_gid

    ct = getgrouplist(user_name, user_gid, byref(grouplist), byref(ngrouplist))
    # if a max of 50 groups was not enough, try again with exact given nr
    if ct < 0:
        getgrouplist.argtypes = [c_char_p, c_uint, POINTER(c_uint * int(ngrouplist.value)), POINTER(c_int32)]
        grouplist = (c_uint * int(ngrouplist.value))()
        ct = getgrouplist(user_name, user_gid, byref(grouplist), byref(ngrouplist))

    if ct < 0:
        raise Exception("Could not find groups for %s: getgrouplist returned %s" % (user, ct))

    grouplist = [grouplist[i] for i in range(ct)]
    if groupnames:
        grouplist = [grp.getgrgid(i).gr_name for i in grouplist]
    return grouplist
