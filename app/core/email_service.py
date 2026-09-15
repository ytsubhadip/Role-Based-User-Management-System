import os
import smtplib
import logging
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

sender_email = os.getenv("EMAIL_ADDRESS")
sender_password = os.getenv("EMAIL_PASSWORD")


def send_temporary_password_email(
    receiver_email: str,
    full_name: str,
    temporary_password: str
):
    print(f"\n==========================================")
    print(f"[TEMPORARY CREDENTIALS GENERATED]")
    print(f"Recipient: {full_name} <{receiver_email}>")
    print(f"Temporary Password: {temporary_password}")
    print(f"==========================================\n")

    message = EmailMessage()
    message["Subject"] = "Your Account Login Credentials"
    message["From"] = sender_email or "no-reply@school.com"
    message["To"] = receiver_email

    message.set_content(
        f"""Hello {full_name},

An account has been created for you by the administrator.

Login Email: {receiver_email}
Temporary Password: {temporary_password}

Please log in using these credentials.
You must verify your email with an OTP and change your temporary password
before accessing your dashboard.

Regards,
Administration
"""
    )

    if not sender_email or not sender_password:
        logger.warning("SMTP credentials not fully configured; skipping email dispatch.")
        return

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(sender_email, sender_password)
            server.sendmail(
                sender_email,
                receiver_email,
                message.as_string()
            )
        logger.info(f"Temporary password email successfully sent to {receiver_email}")
    except Exception as e:
        logger.error(f"Failed to send temporary password email to {receiver_email}: {e}")
        print(f"[WARN] Email sending failed: {e}. Use temporary password from console.")


def send_otp_email(
    receiver_email: str,
    full_name: str,
    otp: str
):
    print(f"\n==========================================")
    print(f"[OTP GENERATED]")
    print(f"Recipient: {full_name} <{receiver_email}>")
    print(f"OTP Code: {otp}")
    print(f"==========================================\n")

    message = EmailMessage()
    message["Subject"] = "Your OTP for Email Verification"
    message["From"] = sender_email or "no-reply@school.com"
    message["To"] = receiver_email

    message.set_content(
        f"""Hello {full_name},

Your One-Time Password (OTP) for email verification is: {otp}

Please use this OTP to verify your email address. It will expire in 10 minutes.

Regards,
Administration
"""
    )

    if not sender_email or not sender_password:
        logger.warning("SMTP credentials not fully configured; skipping OTP email dispatch.")
        return

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=10) as server:
            server.login(sender_email, sender_password)
            server.sendmail(
                sender_email,
                receiver_email,
                message.as_string()
            )
        logger.info(f"OTP email successfully sent to {receiver_email}")
    except Exception as e:
        logger.error(f"Failed to send OTP email to {receiver_email}: {e}")
        print(f"[WARN] OTP email sending failed: {e}. Use OTP code from console.")