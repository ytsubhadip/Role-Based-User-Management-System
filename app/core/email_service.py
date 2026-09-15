
import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

sender_email = os.getenv("EMAIL_ADDRESS")
sender_password = os.getenv("EMAIL_PASSWORD")

def send_temporary_password_email(
    receiver_email: str,
    full_name: str,
    temporary_password: str
):
    message = EmailMessage()

    message["Subject"] = "Your Account Login Credentials"
    message["From"] = os.getenv("EMAIL_ADDRESS")
    message["To"] = receiver_email

    message.set_content(
        f"""
        Hello {full_name},

            An account has been created for you by the administrator.

            Login Email: {receiver_email}
            Temporary Password: {temporary_password}

            Please log in using these credentials.
            You must verify your email and change your temporary password
            before accessing your dashboard.

            Regards,
            Administration
            """
       )

    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email,
            receiver_email,
            message.as_string()
        )



def send_otp_email(
    receiver_email: str,
    full_name: str,
    otp: str
):
    message = EmailMessage()

    message["Subject"] = "Your OTP for Email Verification"
    message["From"] = os.getenv("EMAIL_ADDRESS")
    message["To"] = receiver_email

    message.set_content(
        f"""
        Hello {full_name},

            Your One-Time Password (OTP) for email verification is: {otp}

            Please use this OTP to verify your email address.

            Regards,
            Administration
            """
       )

    
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(
            sender_email,
            receiver_email,
            message.as_string()
        )

if __name__ == "__main__":
    # send_temporary_password_email("local02299@gmail.com", "subhadip Bar","1245789")
    # print("Email Send Successfully")
    send_otp_email("local02299@gmail.com", "subhadip Bar", "457812")