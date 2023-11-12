# email_utils.py

from postmarker.core import PostmarkClient
from decouple import config


def send_email_via_postmark(subject, message, sender, recipients, token):
    postmark = PostmarkClient(server_token=config('ONBOARDING_EMAIL_SERVER_TOKEN'))
    postmark.emails.send(
        From=sender,
        To=recipients,
        Subject=subject,
        HtmlBody=message,
    )
