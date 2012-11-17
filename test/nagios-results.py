#!/usr/bin/env python
##
#
# Copyright 2012 Luis Fernando Muñoz Mejías
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
Tests for the NagiosResult class in the vsc.utils.nagios module
"""
import os
import tempfile
import time
import sys

from unittest import TestCase, TestLoader, main

from vsc.utils.nagios import NagiosResult


class TestNagiosResult(TestCase):
    """Test for the nagios result class."""

    def test_no_perfdata(self):
        """Test what is generated when no performance data is given"""
        n = NagiosResult('hello')
        self.assertEqual(n.message, 'hello', 'Class correctly filled in')
        self.assertEqual(len(n.__dict__.keys()), 1, 'Nothing gets added with no performance data')
        self.assertEqual(n.__str__(), n.message, 'Correct stringification with no performance data')

    def test_perfdata_no_thresholds(self):
        """Test what is generated when performance data with no thresholds is given"""
        n = NagiosResult('hello', a_metric=1)
        self.assertEqual(n.message, 'hello', 'Class message correctly filled in')
        self.assertEqual(n.a_metric, 1, "Performance data correctly filled in")
        self.assertEqual(len(n.__dict__.keys()), 2, "No extra fields added")
        self.assertEqual(n.__str__(), 'hello | a_metric=1;;;',
                         'Performance data with no thresholds correctly stringified')

    def test_perfdata_with_thresholds(self):
        """Test what is generated when performance AND thresholds are given"""
        n = NagiosResult('hello', a_metric=1, a_metric_critical=2)
        self.assertEqual(n.a_metric_critical, 2, "Threshold for a perfdata is a normal key")
        self.assertEqual(len(n.__dict__.keys()), 3, "All keys correctly stored in the object")
        self.assertTrue(n.__str__().endswith('a_metric=1;;2;'),
                        "Critical threshold in correct position")
        n.a_metric_warning = 5
        self.assertTrue(n.__str__().endswith('a_metric=1;5;2;'),
                        "Warning threshold in correct position")


def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestNagiosResult)


if __name__ == '__main__':
    main()  # unittest.main
