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
A class that has some support functions for generating rst documentation

@author: Caroline De Brouwer (Ghent University)
"""

def det_col_width(entries, title):
    """Determine column width based on column title and list of entries."""
    return max(map(len, entries + [title]))

def mk_rst_table(titles, values):
    """
    Returns an rst table with given titles and values (a nested list of string values for each column)
    """
    num_col = len(titles)
    table = []
    col_widths = []
    tmpl = []
    line= []

    # figure out column widths
    for i in range(0, num_col):
        col_widths.append(det_col_width(values[i], titles[i]))

        # make line template
        tmpl.append('{' + str(i) + ':{c}<' + str(col_widths[i]) + '}')
        line.append('') # needed for table line

    line_tmpl = '   '.join(tmpl)
    table_line = line_tmpl.format(*line, c="=")

    table.append(table_line)
    table.append(line_tmpl.format(*titles, c=' '))
    table.append(table_line)

    for i in range(0, len(values[0])):
        table.append(line_tmpl.format(*[v[i] for v in values], c=' '))

    table.extend([table_line, ''])

    return table
