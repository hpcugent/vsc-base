# #
# Copyright 2015-2015 Ghent University
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
Functions for generating rst documentation

@author: Caroline De Brouwer (Ghent University)
"""

INDENT_4SPACES = ' ' * 4


class LengthNotEqualException(Exception):
    pass

def mk_rst_table(titles, columns):
    """
    Returns an rst table with given titles and columns (a nested list of string columns for each column)
    """
    num_col = len(titles)
    if num_col != len(columns):
        msg = "Length of titles and columns should be equal, found titles: %s and entries: %s" % (len(titles), len(columns))
        raise LengthNotEqualException, msg
    table = []
    col_widths = []
    tmpl = []
    line= []

    # figure out column widths
    for i, title in enumerate(titles):
        width = max(map(len, columns[i] + [title]))

        # make line template
        tmpl.append('{%s:{c}<%s}' % (i, width))

    line = [''] * num_col
    line_tmpl = INDENT_4SPACES.join(tmpl)
    table_line = line_tmpl.format(*line, c="=")

    table.append(table_line)
    table.append(line_tmpl.format(*titles, c=' '))
    table.append(table_line)

    for row in map(list, zip(*columns)):
        table.append(line_tmpl.format(*row, c=' '))

    table.extend([table_line, ''])

    return table
