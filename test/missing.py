#!/usr/bin/env python
##
#
# Copyright 2012-2013 Ghent University
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
##
"""
Tests for the vsc.utils.missing module.

@author: Andy Georges (Ghent University)
"""
from collections import defaultdict
from paycheck import with_checker
from random import randint
from unittest import TestCase, TestLoader

from vsc.utils.missing import nub
from vsc.utils.missing import TryOrFail
from vsc.utils.missing import topological_sort


def generate_random_dag():
    """
    Based on http://stackoverflow.com/questions/12790337/generating-a-random-dag
    """
    edge_probability = randint(10,30)
    ranks = randint(3, 10)
    graph = defaultdict(list)
    node_max = 0

    for r in xrange(ranks):
        new_nodes = randint(2, 20)

        for old_node in xrange(node_max):
            for n in xrange(new_nodes):
                node = node_max + n
                if randint(0,100) < edge_probability:
                    graph[old_node].append(node)
                else:
                    graph[old_node]

        node_max += new_nodes

    for n in xrange(new_nodes):
        graph[node_max - n - 1] = []

    return graph


class TestMissing(TestCase):
    """Test for the nub function."""

    @with_checker([int])
    def test_nub_length(self, list_of_ints):
        nubbed = nub(list_of_ints)
        self.assertTrue(len(list_of_ints) >= len(nubbed))

    @with_checker([int])
    def test_nub_membership(self, list_of_ints):
        nubbed = nub(list_of_ints)
        for x in list_of_ints:
            self.assertTrue(x in nubbed)

    @with_checker([int])
    def test_nub_order(self, list_of_ints):
        nubbed = nub(2 * list_of_ints)
        for (x, y) in [(x_, y_) for x_ in list_of_ints for y_ in list_of_ints]:
            self.assertTrue((list_of_ints.index(x) <= list_of_ints.index(y)) == (nubbed.index(x) <= nubbed.index(y)))

    def test_tryorfail_no_sleep(self):
        """test for a retry that succeeds."""

        raise_boundary = 2

        @TryOrFail(3, (Exception,), 0)
        def f(i):
            if i < raise_boundary:
                raise Exception
            else:
                return i

        for n in xrange(0, 2 * raise_boundary):
            try:
                v = f(n)
                self.assertFalse(n < raise_boundary)
                self.assertTrue(v == n)
            except:
                self.assertTrue(n < raise_boundary)

    def test_random_topological_sort(self):
        """
        test for a topological sort.

        the key invariant should be that if a appears before b in the resulting sort, there is no way to reach
        b from a in the DAG.
        """
        random.seed([42])
        for i in xrange(10):
            g = generate_random_dag()
            sorting = list(topological_sort(g))
            visited = set()
            for node in reversed(sorting):
                adjacent = set(g[node])
                self.assertTrue(adjacent.isdisjoint(visited))

            self.assertTrue(len(sorting) == len(g.keys()))


def suite():
    """ return all the tests"""
    return TestLoader().loadTestsFromTestCase(TestMissing)
