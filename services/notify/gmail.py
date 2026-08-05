"""Gmail SMTP delivery (App Password auth).

smtplib is blocking, so the actual send happens in a worker thread
(asyncio.to_thread) - kept async so this matches how telegram.py/the rest
of the pipeline calls things, without actually stalling the event loop
during the SMTP round-trip.
"""

import asyncio
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from services.config import get_settings

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


class GmailSendError(RuntimeError):
    pass


def _send_sync(subject: str, html_body: str) -> None:
    settings = get_settings()
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.gmail_address
    message["To"] = settings.gmail_to_address
    message.attach(MIMEText(html_body, "html"))

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(settings.gmail_address, settings.gmail_app_password)
        server.sendmail(settings.gmail_address, settings.gmail_to_address, message.as_string())


async def send(subject: str, html_body: str) -> None:
    try:
        await asyncio.to_thread(_send_sync, subject, html_body)
    except smtplib.SMTPException as e:
        raise GmailSendError(f"Gmail send failed: {e}") from e


def _verify_login_sync() -> None:
    settings = get_settings()
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, context=context) as server:
        server.login(settings.gmail_address, settings.gmail_app_password)


async def verify_login() -> bool:
    try:
        await asyncio.to_thread(_verify_login_sync)
        return True
    except smtplib.SMTPException:
        return False
