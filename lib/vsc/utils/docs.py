#
# Copyright 2015-2022 Ghent University
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
Functions for generating rst documentation

@author: Caroline De Brouwer (Ghent University)
"""

INDENT_4SPACES = ' ' * 4


class LengthNotEqualException(ValueError):
    pass


def mk_rst_table(titles, columns):
    """
    Returns an rst table with given titles and columns (a nested list of string columns for each column)
    """
    # make sure that both titles and columns are actual lists (not generator objects),
    # since we use them multiple times (and a generator can only be consumed once
    titles, columns = list(titles), list(columns)

    title_cnt, col_cnt = len(titles), len(columns)
    if title_cnt != col_cnt:
        msg = "Number of titles/columns should be equal, found %d titles and %d columns" % (title_cnt, col_cnt)
        raise LengthNotEqualException(msg)
    table = []
    tmpl = []
    line = []

    # figure out column widths
    for i, title in enumerate(titles):
        width = max(map(len, columns[i] + [title]))

        # make line template
        tmpl.append('{%s:{c}<%s}' % (i, width))

    line = [''] * col_cnt
    line_tmpl = INDENT_4SPACES.join(tmpl)
    table_line = line_tmpl.format(*line, c='=')

    table.append(table_line)
    table.append(line_tmpl.format(*titles, c=' '))
    table.append(table_line)

    for row in map(list, zip(*columns)):
        table.append(line_tmpl.format(*row, c=' '))

    table.extend([table_line, ''])

    return table
