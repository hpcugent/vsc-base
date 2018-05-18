#!/usr/bin/env python
#
# Copyright 2018-2018 Ghent University
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
Example script to use the RestClient to get repo statistics from github
@author Jens Timmerman
@author Ewald Pauwels
"""

from datetime import date, timedelta
from vsc.utils.rest import RestClient

from vsc.utils.generaloption import simple_option

options = {
    'token':('github token', None, 'store', None, 't'),
    'organisation': ('github organisation to scan', None, 'store', 'hpcugent', 'o'),
    'year': ('year to get statistics for', None, 'store', '2017', 'y'),
    'url': ('github api url to use', None, 'store', 'https://api.github.com', 'u'),
}

go = simple_option(options)
githubclient =  RestClient(go.options.url, token=go.options.token)

# get list of repositories for organisation
repos = githubclient.orgs[go.options.organisation].repos.get()[1]

repo_totals = {}
part_totals = {}


def all_sundays(year):
    # January 1st of the given year
    dt = date(year, 1, 1)
    # First Sunday of the given year
    dt += timedelta(days = 6 - dt.weekday())
    while dt.year == year:
        yield dt
        dt += timedelta(days = 7)

# init weeks of the year, github returns datestamps for first second of the sunday of the week
weeks = {}
for sunday in all_sundays(int(go.options.year)):
    weeks[(sunday - date(1970, 1, 1)).total_seconds()] = 0


for repo in repos:
    print repo['name']

    totalcommitsrepo=0

    participators = githubclient.repos[go.options.organisation][repo['name']].stats.contributors.get()[1]
    for part in participators:
        #set weeks to zero
        weeks=dict((k,0) for k in weeks)

        print ' - ',part['author']['login'],
        for week in part['weeks']:
            #print week['w'],
            if week['w'] in weeks:
                weeks[week['w']] += week['c']
        print sum(weeks.values())
        totalcommitsrepo+=sum(weeks.values())
    print '--TOTAL--'
    print totalcommitsrepo
    print
