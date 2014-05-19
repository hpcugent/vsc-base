##
# Copyright 2014 Ghent University
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
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation v2.
#
# vsc-base is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with EasyBuild.  If not, see <http://www.gnu.org/licenses/>.
##
"""
Unit tests for the rest client.

@author: Jens Timmerman (Ghent University)
"""
import os

from unittest import TestLoader, TestCase, main

from vsc.utils.rest import RestClient


# the user who's repo to test
GITHUB_USER = "hpcugent"
# the repo of this user to use in this test
GITHUB_REPO = "testrepository"
# Github username (optional)
GITHUB_LOGIN = os.environ.get('VSC_GITHUB_LOGIN', None)
# github auth token to use (optional)
GITHUB_TOKEN = os.environ.get('VSC_GITHUB_TOKEN', None)
# branch to test
GITHUB_BRANCH = 'master'


class RestClientTest(TestCase):
    """ small test for The RestClient
    This should not be to much, since there is an hourly limit of requests for the github api
    """

    def setUp(self):
        """setup"""
        super(RestClientTest, self).setUp()
        self.client = RestClient('https://api.github.com', username=GITHUB_LOGIN, token=GITHUB_TOKEN)

    def test_client(self):
        """Do a test api call"""
        status, body = self.client.repos[GITHUB_USER][GITHUB_REPO].contents.a_directory['a_file.txt'].get()
        self.assertEqual(status, 200)
        # dGhpcyBpcyBhIGxpbmUgb2YgdGV4dAo= == 'this is a line of text' in base64 encoding
        self.assertEqual(body['content'].strip(), u"dGhpcyBpcyBhIGxpbmUgb2YgdGV4dAo=")


def suite():
    """ returns all the testcases in this module """
    return TestLoader().loadTestsFromTestCase(RestClientTest)

if __name__ == '__main__':
    main()
