from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage
from email.utils import formataddr
from pathlib import Path

from .config import EmailSettings


def send_report_email(
    settings: EmailSettings,
    subject: str,
    html_body: str,
    text_body: str,
    attachments: list[Path],
) -> None:
    smtp_user = os.getenv(settings.smtp_user_env, "").strip()
    smtp_password = os.getenv(settings.smtp_password_env, "").strip()
    recipients = _split_recipients(os.getenv(settings.mail_to_env, ""))

    if not smtp_user:
        raise ValueError(f"{settings.smtp_user_env} 환경변수가 비어 있습니다.")
    if not smtp_password:
        raise ValueError(f"{settings.smtp_password_env} 환경변수가 비어 있습니다.")
    if not recipients:
        raise ValueError(f"{settings.mail_to_env} 환경변수가 비어 있습니다.")

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((settings.from_name, smtp_user))
    message["To"] = ", ".join(recipients)
    message.set_content(text_body)
    message.add_alternative(html_body, subtype="html")

    for path in attachments:
        if not path.exists():
            continue
        maintype, subtype = _mime_type(path)
        message.add_attachment(path.read_bytes(), maintype=maintype, subtype=subtype, filename=path.name)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(smtp_user, smtp_password)
        smtp.send_message(message)


def _split_recipients(value: str) -> list[str]:
    chunks = value.replace(";", ",").split(",")
    return [chunk.strip() for chunk in chunks if chunk.strip()]


def _mime_type(path: Path) -> tuple[str, str]:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return "application", "pdf"
    if suffix in {".html", ".htm"}:
        return "text", "html"
    if suffix == ".txt":
        return "text", "plain"
    return "application", "octet-stream"
