import base64
import logging
from email.message import EmailMessage
from html import escape
from zoneinfo import ZoneInfo

from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from config import settings
from models import Enquiry

logger = logging.getLogger("uvicorn.error")

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
IST = ZoneInfo("Asia/Kolkata")


def _load_credentials() -> Credentials | None:
    if not (settings.gmail_client_id and settings.gmail_client_secret and settings.gmail_refresh_token):
        return None

    creds = Credentials(
        token=None,
        refresh_token=settings.gmail_refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=settings.gmail_client_id,
        client_secret=settings.gmail_client_secret,
        scopes=SCOPES,
    )
    creds.refresh(Request())
    return creds


def _greeting_name() -> str:
    return settings.gmail_notify_name or "there"


def _build_text(enquiry: Enquiry, submitted_ist: str) -> str:
    return (
        f"Hi {_greeting_name()},\n\n"
        f"A new demo request has been submitted through the website.\n\n"
        f"Contact Details\n\n"
        f"Name: {enquiry.name}\n"
        f"Email: {enquiry.email}\n"
        f"Company / Plant: {enquiry.company}\n\n"
        f"Message\n\n"
        f"{enquiry.message}\n\n"
        f"Submitted On: {submitted_ist}\n\n"
        f"Regards,\n"
        f"Website Demo Request System\n"
    )


def _build_html(enquiry: Enquiry, submitted_ist: str) -> str:
    message_html = escape(enquiry.message).replace("\n", "<br>")

    return f"""\
<!DOCTYPE html>
<html>
  <body style="margin:0;padding:0;background:#ffffff;
               font-family:Arial,Helvetica,sans-serif;font-size:15px;color:#111;line-height:1.6;">
    <div style="max-width:560px;margin:0 auto;padding:24px;">
      <p>Hi {escape(_greeting_name())},</p>

      <p>A new demo request has been submitted through the website.</p>

      <p style="font-weight:bold;margin-bottom:4px;">Contact Details</p>
      <p style="margin-top:0;">
        Name: {escape(enquiry.name)}<br>
        Email: {escape(enquiry.email)}<br>
        Company / Plant: {escape(enquiry.company)}
      </p>

      <p style="font-weight:bold;margin-bottom:4px;">Message</p>
      <p style="margin-top:0;">{message_html}</p>

      <p>Submitted On: {escape(submitted_ist)}</p>

      <p>Regards,<br>Website Demo Request System</p>
    </div>
  </body>
</html>"""


def send_enquiry_notification(enquiry: Enquiry) -> None:
    """Best-effort Gmail notification. No-ops if Gmail isn't configured, and never
    raises - a notification failure must not fail the enquiry submission."""
    if not settings.gmail_notify_to:
        return

    try:
        creds = _load_credentials()
        if creds is None:
            logger.warning(
                "Gmail notification skipped: GMAIL_CLIENT_ID/GMAIL_CLIENT_SECRET/GMAIL_REFRESH_TOKEN not set. "
                "Run gmail_auth.py once to get these values."
            )
            return

        submitted_ist = enquiry.created_at.astimezone(IST).strftime("%d %b %Y, %I:%M %p IST")

        message = EmailMessage()
        message["To"] = settings.gmail_notify_to
        message["Subject"] = f"New Demo Request - {enquiry.name}"
        message.set_content(_build_text(enquiry, submitted_ist))
        message.add_alternative(_build_html(enquiry, submitted_ist), subtype="html")

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service = build("gmail", "v1", credentials=creds)
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
    except RefreshError:
        logger.exception(
            "Gmail refresh token is invalid or revoked - re-run gmail_auth.py to re-authorize."
        )
    except Exception:
        logger.exception("Failed to send enquiry notification via Gmail API")
