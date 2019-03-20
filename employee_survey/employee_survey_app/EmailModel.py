# pylint: disable=invalid-name
# pylint: disable=broad-except
# pylint: disable=missing-docstring
"""
Email Model
"""
import logging
from django.core.mail import EmailMessage


def send_mail_fun(subject, sms_text, email_to):
    try:
        email = EmailMessage(subject, ''.join(sms_text), to=[email_to])
        email.content_subtype = "html"
        email.send()
    except Exception as e:
        logging.exception("Exception in send email: %s", e)
