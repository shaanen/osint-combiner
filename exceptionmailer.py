import logging.handlers
import configparser
import datetime
import socket
import os


class TlsSMTPHandler(logging.handlers.SMTPHandler):
    def emit(self, record):
        """
        Emit a record.

        Format the record and send it to the specified addressees.
        """
        try:
            import smtplib
            import string  # for tls add this line
            try:
                from email.utils import formatdate
            except ImportError:
                formatdate = datetime.datetime.now()
            port = self.mailport
            if not port:
                port = smtplib.SMTP_PORT
            smtp = smtplib.SMTP(self.mailhost, port)
            msg = self.format(record)
            msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
                self.fromaddr,
                ",".join(self.toaddrs),
                # string.join(self.toaddrs, ","),
                self.getSubject(record),
                formatdate(), msg)
            if self.username:
                smtp.ehlo()  # for tls add this line
                smtp.starttls()  # for tls add this line
                smtp.ehlo()  # for tls add this line
                smtp.login(self.username, self.password)
            smtp.sendmail(self.fromaddr, self.toaddrs, msg)
            smtp.quit()
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)


def get_email_sender():
    """Returns sender's email from config.ini """
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.realpath(__file__)) + "/config.ini")
    return config['email']['EMAIL_SENDER']


def get_email_password_sender():
    """Returns sender's password from config.ini """
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.realpath(__file__)) + "/config.ini")
    return config['email']['EMAIL_PASSWORD_SENDER']


def get_email_receiver():
    """Returns receivers email from config.ini """
    config = configparser.ConfigParser()
    config.read(os.path.dirname(os.path.realpath(__file__)) + "/config.ini")
    return config['email']['EMAIL_RECEIVER']


def send_exc_mail():
    logger = logging.getLogger()
    sender = get_email_sender()
    sender_password = get_email_password_sender()
    receiver = get_email_receiver()
    gm = TlsSMTPHandler(("smtp.gmail.com", 587), sender, [receiver],
                        'Error found on ' + socket.gethostname(),
                        (sender, sender_password))
    gm.setLevel(logging.ERROR)
    logger.addHandler(gm)
    logger.exception('An error occurred on :' + socket.gethostname())
