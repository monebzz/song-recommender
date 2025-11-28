import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'song_recommender.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

print("=" * 50)
print("EMAIL CONFIGURATION CHECK")
print("=" * 50)
print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'*' * len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else '(empty)'}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print("=" * 50)

# Test email sending
print("\nTesting email sending...")
try:
    send_mail(
        'Test Email',
        'This is a test email from your Django app.',
        settings.DEFAULT_FROM_EMAIL,
        ['test@example.com'],  # Replace with your actual email to test
        fail_silently=False,
    )
    print("✅ Email sent successfully!")
except Exception as e:
    print(f"❌ Error sending email: {e}")
    import traceback
    traceback.print_exc()
