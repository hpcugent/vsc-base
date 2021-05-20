#
# Copyright 2014-2021 Ghent University
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
Unit tests for the mail wrapper.

@author: Andy Georges (Ghent University)
"""
import mock
import os

from vsc.install.testing import TestCase

from email.mime.text import MIMEText
from vsc.utils.mail import VscMail

class TestVscMail(TestCase):

    @mock.patch('vsc.utils.mail.smtplib')
    @mock.patch('vsc.utils.mail.ssl')
    def test_send(self, mock_ssl, mock_smtplib):

        msg = MIMEText("test")
        msg['Subject'] = "subject"
        msg['From'] = "test@noreply.com"
        msg['To'] = "test@noreply.com"
        msg['Reply-to'] = "test@noreply.com"

        vm = VscMail()

        self.assertEqual(vm.mail_host, '')
        self.assertEqual(vm.mail_port, 0)
        self.assertEqual(vm.smtp_auth_user, None)
        self.assertEqual(vm.smtp_auth_password, None)
        self.assertEqual(vm.smtp_use_starttls, False)

        vm._send(mail_from="test@noreply.com", mail_to="test@noreply.com", mail_subject="s", msg=msg)

        vm = VscMail(
            mail_host = "test.machine.com",
            mail_port=123,
            smtp_auth_user="me",
            smtp_auth_password="hunter2",
        )

        self.assertEqual(vm.mail_host, "test.machine.com")
        self.assertEqual(vm.mail_port, 123)
        self.assertEqual(vm.smtp_auth_user, "me")
        self.assertEqual(vm.smtp_auth_password, "hunter2")
        self.assertEqual(vm.smtp_use_starttls, False)

        vm._send(mail_from="test@noreply.com", mail_to="test@noreply.com", mail_subject="s", msg=msg)

        mock_smtplib.SMTP.assert_called_with(host="test.machine.com", port=123)

        vm = VscMail(
            mail_host = "test.machine.com",
            mail_port=124,
            smtp_auth_user="me",
            smtp_auth_password="hunter2",
            smtp_use_starttls=True
        )

        self.assertEqual(vm.mail_host, "test.machine.com")
        self.assertEqual(vm.mail_port, 124)
        self.assertEqual(vm.smtp_auth_user, "me")
        self.assertEqual(vm.smtp_auth_password, "hunter2")
        self.assertEqual(vm.smtp_use_starttls, True)

        vm._send(mail_from="test@noreply.com", mail_to="test@noreply.com", mail_subject="s", msg=msg)

        mock_smtplib.SMTP.assert_called_with(host="test.machine.com", port=124)
        mock_ssl.create_default_context.assert_called()
