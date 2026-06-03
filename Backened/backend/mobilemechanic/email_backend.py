from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail import EmailMessage
from django.conf import settings
import logging
import requests

logger = logging.getLogger(__name__)


class WebhookEmailBackend(BaseEmailBackend):
    """Email backend that posts email payloads to a configured webhook (e.g., n8n).

    It supports posting either a single message payload
    {to, subject, body, reply_to} or a batch payload {emails: [...] }.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.webhook_url = getattr(settings, 'EMAIL_WEBHOOK_URL', None)

    def send_messages(self, email_messages):
        if not email_messages:
            return 0

        if not self.webhook_url:
            logger.error('EMAIL_WEBHOOK_URL not configured; cannot send via webhook')
            return 0

        sent_count = 0
        payload_emails = []

        for msg in email_messages:
            # msg is an instance of EmailMessage
            to_list = msg.to or []
            subject = msg.subject or ''
            # Prefer html alternative if present
            body = None
            if hasattr(msg, 'alternatives') and msg.alternatives:
                # alternatives is a list of (content, mimetype)
                for alt, mimetype in msg.alternatives:
                    if mimetype == 'text/html':
                        body = alt
                        break
            if not body:
                body = msg.body or ''

            reply_to = ''
            if hasattr(msg, 'reply_to') and msg.reply_to:
                reply_to = msg.reply_to[0]

            if len(to_list) == 1:
                payload_emails.append({
                    'to': to_list[0],
                    'subject': subject,
                    'body': body,
                    'reply_to': reply_to,
                })
            else:
                # For multiple recipients create one entry per recipient
                for r in to_list:
                    payload_emails.append({
                        'to': r,
                        'subject': subject,
                        'body': body,
                        'reply_to': reply_to,
                    })

        try:
            # If single email, send single payload; else send batch
            if len(payload_emails) == 1:
                resp = requests.post(self.webhook_url, json=payload_emails[0], timeout=10)
                resp.raise_for_status()
                sent_count = 1
            else:
                resp = requests.post(self.webhook_url, json={'emails': payload_emails}, timeout=10)
                resp.raise_for_status()
                sent_count = len(payload_emails)

            logger.info('Sent %d emails via webhook %s', sent_count, self.webhook_url)
            return sent_count

        except Exception as e:
            logger.error('Failed to send emails via webhook %s: %s', self.webhook_url, str(e))
            return 0
