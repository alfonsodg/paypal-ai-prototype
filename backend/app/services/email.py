import smtplib
from email.message import EmailMessage

from ..config import settings


def send_invoice_email(to_email: str, subject: str, body: str, pdf_bytes: bytes | None = None) -> bool:
    if not settings.smtp_host:
        # dev fallback: print
        print(f"[email-fallback] to={to_email} subject={subject}\n{body}")
        return True
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = settings.smtp_from
    msg["To"] = to_email
    msg.set_content(body)
    if pdf_bytes:
        msg.add_attachment(pdf_bytes, maintype="application", subtype="pdf", filename="invoice.pdf")
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        if settings.smtp_port == 587:
            server.starttls()
        if settings.smtp_user:
            server.login(settings.smtp_user, settings.smtp_password)
        server.send_message(msg)
    return True