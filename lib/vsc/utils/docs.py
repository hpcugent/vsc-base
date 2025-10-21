#
# Copyright 2015-2025 Ghent University
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
        msg = f"Number of titles/columns should be equal, found {int(title_cnt)} titles and {int(col_cnt)} columns"
        raise LengthNotEqualException(msg)

    table = []
    separator_blocks = []
    title_items = []
    column_widths = []

    for i, title in enumerate(titles):
        # figure out column widths
        width = max(map(len, columns[i] + [title]))

        column_widths.append(width)
        separator_blocks.append(f"{'=' * width}")
        title_items.append(f"{title}".ljust(width))

    separator_line = " ".join(separator_blocks)

    # header
    table.extend([separator_line, " ".join(title_items), separator_line])

    # rows
    for row in map(list, zip(*columns)):
        row_items = []
        for i, item in enumerate(row):
            row_items.append(item.ljust(column_widths[i]))
        table.append(" ".join(row_items))

    # footer
    table.extend([separator_line, ""])

    return table
