#
# Copyright 2014-2022 Ghent University
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
Unit tests for the rest client.

@author: Jens Timmerman (Ghent University)
"""
import os

from vsc.install.testing import TestCase
from vsc.utils.py2vs3 import HTTPError
from vsc.utils.rest import Client, RestClient


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
        if GITHUB_TOKEN is None:
            print("Skipping test_client, since no GitHub token is available")
            return

        status, body = self.client.repos[GITHUB_USER][GITHUB_REPO].contents.a_directory['a_file.txt'].get()
        self.assertEqual(status, 200)
        # dGhpcyBpcyBhIGxpbmUgb2YgdGV4dAo= == 'this is a line of text' in base64 encoding
        self.assertEqual(body['content'].strip(), u"dGhpcyBpcyBhIGxpbmUgb2YgdGV4dAo=")

        status, body = self.client.repos['hpcugent']['easybuild-framework'].pulls[1].get()
        self.assertEqual(status, 200)
        self.assertEqual(body['merge_commit_sha'], u'fba3e13815f3d2a9dfbd2f89f1cf678dd58bb1f1')

    def test_request_methods(self):
        """Test all request methods"""
        if GITHUB_TOKEN is None:
            print("Skipping test_request_methods, since no GitHub token is available")
            return

        status, headers = self.client.head()
        self.assertEqual(status, 200)
        self.assertTrue(headers)
        self.assertTrue('X-GitHub-Media-Type' in headers)
        try:
            status, body = self.client.user.emails.post(body='jens.timmerman@ugent.be')
            self.assertTrue(False, 'posting to unauthorized endpoint did not trhow a http error')
        except HTTPError:
            pass
        try:
            status, body = self.client.user.emails.delete(body='jens.timmerman@ugent.be')
            self.assertTrue(False, 'deleting to unauthorized endpoint did not trhow a http error')
        except HTTPError:
            pass

    def test_get_method(self):
        """A quick test of a GET to the github API"""

        status, body = self.client.users['hpcugent'].get()
        self.assertEqual(status, 200)
        self.assertEqual(body['login'], 'hpcugent')
        self.assertEqual(body['id'], 1515263)

    def test_get_connection(self):
        """Test for Client.get_connection."""

        client = Client('https://api.github.com')

        url = '/repos/hpcugent/vsc-base/pulls/296/comments'
        try:
            client.get_connection(Client.POST, url, body="{'body': 'test'}", headers={})
            self.assertTrue(False, "Trying to post a comment unauthorized should result in HTTPError")
        except HTTPError:
            pass

    def test_censor_request(self):
        """Test censor of requests"""

        client = Client('https://api.github.com')

        payload = {'username': 'vsc10001', 'password': 'potato', 'token': '123456'}
        payload_censored = client.censor_request(['password'], payload)
        self.assertEqual(
            payload_censored,
            {'username': 'vsc10001', 'password': '<actual secret censored>', 'token': '123456'},
        )
        payload_censored = client.censor_request(['password', 'token'], payload)
        self.assertEqual(
            payload_censored,
            {'username': 'vsc10001', 'password': '<actual secret censored>', 'token': '<actual secret censored>'},
        )
        payload_censored = client.censor_request(['something_else'], payload)
        self.assertEqual(payload_censored, payload)

        nondict_payload = [payload, 'more_payload']
        payload_censored = client.censor_request(['password'], nondict_payload)
        self.assertEqual(payload_censored, nondict_payload)
