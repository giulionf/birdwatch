import os
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
from typing import List


def send_mail(recipient_mails: List[str],
              subject: str,
              text: str,
              server: str,
              port: int,
              sender_mail: str,
              sender_mail_pw: str,
              attachment_path: str = None):

    # Login
    server = smtplib.SMTP(server, port)
    server.starttls()
    server.login(user=sender_mail, password=sender_mail_pw)

    msg = MIMEMultipart()
    msg['From'] = sender_mail
    msg['To'] = ", ".join(recipient_mails)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject
    msg.attach(MIMEText(text))

    if attachment_path is not None:
        attachment = MIMEBase('application', "octet-stream")
        attachment.set_payload(open(attachment_path, "rb").read())
        encoders.encode_base64(attachment)
        attachment.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(attachment_path))
        msg.attach(attachment)

    server.sendmail(sender_mail, recipient_mails, msg.as_string())
    server.close()
