import uuid
from django.core.mail import send_mail
from django.conf import settings

def generateRandomToken():
    """Generate a random UUID token for email verification."""
    return str(uuid.uuid4())

def sendEmailToken(email, token):
    """Send verification email with token link."""
    subject = "Verify Your HK Smart Store Account"
    message = f"""
    Hi there 👋,

    Please verify your email address to activate your HK Smart Store account.

    Click the link below to verify:
    http://127.0.0.1:8000/accounts/verify/{token}/

    Thanks,
    HK Smart Store Team 🛍️
    """

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )

def sendOTPtoEmail(email, otp):
    """Send OTP for secure login."""
    subject = "HK Smart Store - OTP for Login"
    message = f"""
    Hello 👋,

    Use the following One-Time Password (OTP) to log in:

    🔐 {otp}

    This code is valid for a short period. Please do not share it with anyone.

    – HK Smart Store Security Team
    """

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
