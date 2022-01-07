#
# Copyright 2012-2022 Ghent University
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
Python module for handling data and time strings.

@author: Stijn De Weirdt (Ghent University)
"""
from __future__ import print_function

import datetime
import os
from vsc.install.testing import TestCase
from vsc.utils.dateandtime import FancyMonth, date_parser, datetime_parser

class DateAndTimeTest(TestCase):
    """Tests for dateandtime"""

    def test_date_parser(self):
        """Test the date_parser"""
        testdate = datetime.date(1970, 1, 1)
        self.assertEqual(date_parser('1970-01-01') , testdate)
        self.assertEqual(date_parser('1970-1-1'), testdate)

        today = datetime.date.today()
        beginthismonth = datetime.date(today.year, today.month, 1)
        self.assertEqual(date_parser('BEGINTHISMONTH') , beginthismonth)

        endapril = datetime.date(today.year, 4, 30)
        self.assertEqual(date_parser('ENDAPRIL') , endapril)

    def test_datetime_parser(self):
        """Test the date_parser"""
        testdate = datetime.datetime(1970, 1, 1)
        self.assertEqual(datetime_parser('1970-01-01') , testdate)
        self.assertEqual(datetime_parser('1970-1-1'), testdate)

        today = datetime.datetime.today()
        beginthismonth = datetime.datetime(today.year, today.month, 1, 12, 1)
        self.assertEqual(datetime_parser('BEGINTHISMONTH 12:1') , beginthismonth)

        endapril = datetime.datetime(today.year, 4, 30, 12, 1, 1, 1)
        self.assertEqual(datetime_parser('ENDAPRIL 12:01:01.000001') , endapril)

    def test_fancymonth(self):
        """Test some of the FancyMonth functions"""
        today = datetime.date.today()
        endapril = datetime.date(today.year, 4, 10)
        f = FancyMonth(endapril)
        self.assertEqual(f.nrdays, 30)  # nr days in month

        may2nd = datetime.date(today.year, 5, 2)
        self.assertEqual(f.number(may2nd), 2)  # spans 2 months
        self.assertEqual([x.nrdays for x in f.interval(may2nd)], [30, 31])  # interval returns FancyMonth instances


def suite():
    """ returns all the testcases in this module """
    return TestLoader().loadTestsFromTestCase(DateAndTimeTest)
