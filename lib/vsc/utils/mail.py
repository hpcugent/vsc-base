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
Wrapper around the standard Python mail library.

  - Send a plain text message
  - Send an HTML message, with a plain text alternative

@author: Andy Georges (Ghent University)
"""
import logging
import re
import smtplib
import ssl
from configparser import ConfigParser
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from future.utils import string_types

class VscMailError(Exception):
    """Raised if the sending of an email fails for some reason."""

    def __init__(self, mail_host=None, mail_to=None, mail_from=None, mail_subject=None, err=None):
        """Initialisation.

        @type mail_host: string
        @type mail_to: list of strings (or string, but deprecated)
        @type mail_from: string
        @type mail_subject: string
        @type err: Exception subclass

        @param mail_host: the SMTP host for actually sending the mail.
        @param mail_to: a well-formed email address of the recipient.
        @param mail_from: a well-formed email address of the sender.
        @param mail_subject: the subject of the mail.
        @param err: the original exception, if any.
        """
        self.mail_host = mail_host
        self.mail_to = mail_to
        self.mail_from = mail_from
        self.mail_subject = mail_subject
        self.err = err


class VscMail(object):
    """Class providing functionality to send out mail."""

    def __init__(
        self,
        mail_host='',
        mail_port=587,
        smtp_auth_user=None,
        smtp_auth_password=None,
        smtp_use_starttls=False,
        mail_config=None):
        """
        - If there is a config file provided, its values take precedence over the arguments passed to __init__
        - If the mail_host is of the format host:port, that port takes precedence over mail_port
        """

        mail_options = ConfigParser()
        if mail_config:
            logging.info("Reading config file: %s", mail_config)
            with open(mail_config, "r") as mc:
                mail_options.read_file(mc)

        # we can have cases where the host part is actually host:port
        _mail_host = mail_options.get("MAIN", "smtp", fallback=mail_host)
        try:
            self.mail_host, _mail_port = _mail_host.split(":")
        except ValueError:
            self.mail_host = _mail_host
            _mail_port = mail_options.get("MAIN", "mail_port", fallback=mail_port)

        self.mail_port = int(_mail_port)
        self.smtp_auth_user = mail_options.get("MAIN", "smtp_auth_user", fallback=smtp_auth_user)
        self.smtp_auth_password = mail_options.get("MAIN", "smtp_auth_password", fallback=smtp_auth_password)
        self.smtp_use_starttls = mail_options.get("MAIN", "smtp_use_starttls", fallback=smtp_use_starttls)


    def _connect(self):
        """
        Connect to the mail host on the given port.

        If provided, use authentication and TLS.
        """
        logging.debug("Using mail host %s, mail port %s", self.mail_host, self.mail_port)
        s = smtplib.SMTP(host=self.mail_host, port=self.mail_port)

        if self.smtp_use_starttls:
            context = ssl.create_default_context()
            s.starttls(context=context)
            logging.debug("Started TLS connection")
        elif not self.mail_host:
            s.connect()

        if self.smtp_auth_user and self.smtp_auth_password:
            s.login(user=self.smtp_auth_user, password=self.smtp_auth_password)
            logging.debug("Authenticated")

        return s

    def _send(self, mail_from, mail_to, mail_subject, msg):
        """Actually send the mail.

        @type mail_from: string representing the sender.
        @type mail_to: list of strings (or string, but deprecated) representing the recipient.
        @type mail_subject: string representing the subject.
        @type msg: MIME message.
        """

        try:
            s = self._connect()

            try:
                s.sendmail(mail_from, mail_to, msg.as_string())
            except smtplib.SMTPHeloError as err:
                logging.error("Cannot get a proper response from the SMTP host %s: %s", self.mail_host, err)
                raise
            except smtplib.SMTPRecipientsRefused as err:
                logging.error("All recipients were refused by SMTP host %s [%s]: %s", self.mail_host, mail_to, err)
                raise
            except smtplib.SMTPSenderRefused as err:
                logging.error("Sender was refused by SMTP host %s [%s]: %s", self.mail_host, mail_from, err)
                raise
            except smtplib.SMTPDataError as err:
                logging.error("Data error: %s", err)
                raise

        except smtplib.SMTPConnectError as err:
            logging.exception("Cannot connect to the SMTP host %s", self.mail_host)
            raise VscMailError(
                mail_host=self.mail_host,
                mail_to=mail_to,
                mail_from=mail_from,
                mail_subject=mail_subject,
                err=err)
        except Exception as err:
            logging.exception("Some unknown exception occurred in VscMail.sendTextMail. Raising a VscMailError.")
            raise VscMailError(
                mail_host=self.mail_host,
                mail_to=mail_to,
                mail_from=mail_from,
                mail_subject=mail_subject,
                err=err)
        else:
            s.quit()

    def sendTextMail(
        self,
        mail_to,
        mail_from,
        reply_to,
        mail_subject,
        message,
        cc=None,
        bcc=None):
        """Send out the given message by mail to the given recipient(s).

        @type mail_to: list
        @type mail_from: string
        @type reply_to: string
        @type mail_subject: string
        @type message: string
        @type cc: list
        @type bcc: list

        @param mail_to: a list of valid email addresses
        @param mail_from: a valid sender email address.
        @param reply_to: a valid email address for the (potential) replies.
        @param mail_subject: the subject of the email.
        @param message: the body of the mail.
        @param cc: a list of valid CC email addresses
        @param bcc: a list of valid BCC email addresses
        """

        # deprecated: single email as string
        if isinstance(mail_to, string_types):
            mail_to = [mail_to]

        logging.info("Sending mail [%s] to %s.", mail_subject, mail_to)

        msg = MIMEText(message, 'plain', 'utf-8')
        msg['Subject'] = mail_subject
        msg['From'] = mail_from
        msg['To'] = ','.join(mail_to)

        if cc:
            logging.info("Sending mail [%s] in CC to %s.", mail_subject, cc)
            msg['Cc'] = cc
            mail_to.extend(cc)

        if bcc:
            logging.info("Sending mail [%s] in BCC to %s.", mail_subject, bcc)
            # do *not* set msg['Bcc'] to avoid leaking the BCC email address to all recipients
            mail_to.extend(bcc)

        if reply_to is None:
            reply_to = mail_from
        msg['Reply-to'] = reply_to

        self._send(mail_from, mail_to, mail_subject, msg)

    def _replace_images_cid(self, html, images):
        """Replaces all occurences of the src="IMAGE" with src="cid:IMAGE" in the provided html argument.

        @type html: string
        @type images: list of strings

        @param html: HTML data, containing image tags for each of the provided images
        @param images: references to the images occuring in the HTML payload

        @return: the altered HTML string.
        """

        for im in images:
            re_src = re.compile("src=\"%s\"" % im)
            (html, count) = re_src.subn("src=\"cid:%s\"" % im, html)
            if count == 0:
                logging.error("Could not find image %s in provided HTML.", im)
                raise VscMailError("Could not find image")

        return html

    def sendHTMLMail(
        self,
        mail_to,
        mail_from,
        reply_to,
        mail_subject,
        html_message,
        text_alternative,
        images=None,
        css=None,
        cc=None,
        bcc=None):
        """
        Send an HTML email message, encoded in a MIME/multipart message.

        The images and css are included in the message, and should be provided separately.

        @type mail_to: list
        @type mail_from: string
        @type reply_to: string
        @type mail_subject: string
        @type html_message: string
        @type text_alternative: string
        @type images: list of strings
        @type css: string
        @type cc: list
        @type bcc: list

        @param mail_to: a list of valid email addresses
        @param mail_from: a valid sender email address.
        @param reply_to: a valid email address for the (potential) replies.
        @param html_message: the actual payload, body of the mail
        @param text_alternative: plain-text version of the mail body
        @param images: the images that are referenced in the HTML body. These should be available as files on the
                      filesystem in the directory where the script runs. Caveat: assume jpeg image type.
        @param css: CSS definitions
        @param cc: a list of valid CC email addresses
        @param bcc: a list of valid BCC email addresses
        """

        # deprecated: single email as string
        if isinstance(mail_to, string_types):
            mail_to = [mail_to]

        logging.info("Sending mail [%s] to %s.", mail_subject, mail_to)

        # Create message container - the correct MIME type is multipart/alternative.
        msg_root = MIMEMultipart('alternative')
        msg_root['Subject'] = mail_subject
        msg_root['From'] = mail_from
        msg_root['To'] = ','.join(mail_to)

        if cc:
            logging.info("Sending mail [%s] in CC to %s.", mail_subject, cc)
            msg_root['Cc'] = cc
            mail_to.extend(cc)

        if bcc:
            logging.info("Sending mail [%s] in BCC to %s.", mail_subject, bcc)
            # do *not* set msg_root['Bcc'] to avoid leaking the BCC email address to all recipients
            mail_to.extend(bcc)

        if reply_to is None:
            reply_to = mail_from
        msg_root['Reply-to'] = reply_to

        msg_root.preamble = 'This is a multi-part message in MIME format. If your email client does not support this' \
                            '(correctly), the first part is the plain text version.'

        # Create the body of the message (a plain-text and an HTML version).
        if images is not None:
            html_message = self._replace_images_cid(html_message, images)

        # Record the MIME types of both parts - text/plain and text/html_message.
        msg_plain = MIMEText(text_alternative, 'plain', 'utf-8')
        msg_html = MIMEText(html_message, 'html_message', 'utf-8')

        # Attach parts into message container.
        # According to RFC 2046, the last part of a multipart message, in this case
        # the HTML message, is best and preferred.
        msg_root.attach(msg_plain)
        msg_alt = MIMEMultipart('related')
        msg_alt.attach(msg_html)

        if css is not None:
            msg_html_css = MIMEText(css, 'css', 'utf-8')
            msg_html_css.add_header('Content-ID', '<newsletter.css>')
            msg_alt.attach(msg_html_css)

        if images is not None:
            for im in images:
                image_fp = open(im, 'r')
                msg_image = MIMEImage(image_fp.read(), 'jpeg')  # FIXME: for now, we assume jpegs
                image_fp.close()
                msg_image.add_header('Content-ID', "<%s>" % im)
                msg_alt.attach(msg_image)

        msg_root.attach(msg_alt)

        self._send(mail_from, mail_to, mail_subject, msg_root)
