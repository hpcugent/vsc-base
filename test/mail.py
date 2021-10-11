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
import logging
import sys
from mock.mock import MagicMock

if sys.version_info[0] >= 3:
    from unittest.mock import mock_open
elif sys.version_info[0] >= 2:
    from mock import mock_open

from vsc.install.testing import TestCase

from email.mime.text import MIMEText
from vsc.utils.mail import VscMail

class TestVscMailConfig(TestCase):


    def test_config_file(self):

        mail_host = "mailhost.domain"
        mail_port = 123
        mail_host_port = "mailhost.domain:567"
        smtp_auth_user = "user"
        smtp_auth_password = "passwd"
        smtp_use_starttls = True

        mail = VscMail(mail_host=mail_host)

        self.assertEqual(mail.mail_host, mail_host)
        self.assertEqual(mail.mail_port, 587)

        mail = VscMail(mail_host=mail_host, mail_port=mail_port)
        self.assertEqual(mail.mail_host, mail_host)
        self.assertEqual(mail.mail_port, mail_port)

        cfgfile = """
            [main]
            mail_host = config_host
            mail_port = 789
            smtp_auth_user = config_user
            smtp_auth_password = config_passwd
            smtp_use_starttls = 1
        """
        # based on https://stackoverflow.com/questions/1289894/how-do-i-mock-an-open-used-in-a-with-statement-using-the-mock-framework-in-pyth/34677735#34677735
        if sys.version_info[0] >= 3:
            with mock.patch("builtins.open", mock_open(read_data=cfgfile)):
                mail = VscMail(mail_config="blah")
        elif sys.version_info[0] >= 2:
            with mock.patch("__builtin__.open", mock_open(read_data=cfgfile)):
                mail = VscMail(mail_config="blah")

        logging.warning("mail.mail_host: %s", mail.mail_host)

        self.assertEqual(mail.mail_host, "config_host")
        self.assertEqual(mail.mail_port, 789)
        self.assertEqual(mail.smtp_auth_user, "config_user")
        self.assertEqual(mail.smtp_auth_password, "config_passwd")
        self.assertEqual(mail.smtp_use_starttls, '1')


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
        self.assertEqual(vm.mail_port, 587)
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
