import os
import django
import traceback
from django.conf import settings
from django.core.mail import send_mail

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'song_recommender.settings')
django.setup()

def test_email():
    print("--- Email Configuration ---")
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print("---------------------------")

    recipient = 'sp23-bse-125@cuilahore.edu.pk' # Email from screenshot
    print(f"Attempting to send email to: {recipient}")
    print(f"From: {settings.DEFAULT_FROM_EMAIL}")

    try:
        send_mail(
            'Test Email from Debug Script 2',
            'This is a test email to verify configuration with specific recipient.',
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        print("✅ Email sent successfully!")
    except Exception as e:
        print("❌ Email sending failed!")
        print(f"Error Type: {type(e).__name__}")
        print(f"Error Message: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_email()
