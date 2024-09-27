from email.message import EmailMessage
from dataclasses import dataclass
from smtplib import SMTP_SSL

from flask import current_app

def send_email(subject: str, address: str, sender: str, body: str):
    msg = EmailMessage()#

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = address

    msg.set_content("Plain text emails are currently not supported.")
    msg.add_alternative(body, subtype='html')

    with SMTP_SSL(current_app.config['SMTP_HOST'], current_app.config['SMTP_PORT']) as smtp:
        smtp.login(current_app.config['SMTP_USERNAME'], current_app.config['SMTP_PASSWORD'])
        smtp.sendmail(sender, address, msg.as_string())