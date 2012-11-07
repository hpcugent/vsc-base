#!/usr/bin/env python
##
#
# Copyright 2012 Andy Georges
#
# This file is part of the tools originally by the HPC team of
# Ghent University (http://ugent.be/hpc).
#
# This is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
##
"""
Tests for the vsc.utils.missing module.
"""
import unittest
from paycheck import with_checker

from vsc.utils.missing import nub

class TestNub(unittest.TestCase):
    """Test for the nub function."""

    @with_checker([int])
    def test_length(self, list_of_ints):
        nubbed = nub(list_of_ints)
        self.assertTrue(len(list_of_ints) >= len(nubbed))

    @with_checker([int])
    def test_membership(self, list_of_ints):
        nubbed = nub(list_of_ints)
        for x in list_of_ints:
            self.assertTrue(x in nubbed)

    @with_checker([int])
    def test_order(self, list_of_ints):
        nubbed = nub(2 * list_of_ints)
        for (x, y) in [(x_, y_) for x_ in list_of_ints for y_ in list_of_ints]:
            self.assertTrue((list_of_ints.index(x) <= list_of_ints.index(y)) == (nubbed.index(x) <= nubbed.index(y)))


if __name__ == '__main__':
    unittest.main()


