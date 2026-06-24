import os
import django
import sys
from django.core.mail import send_mail
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
sys.path.append(os.getcwd())
django.setup()

def test_smtp():
    print(f"Using EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"Using EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"Using EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    
    try:
        subject = 'SMTP Test'
        message = 'If you receive this, SMTP is working.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [settings.EMAIL_HOST_USER]  # Send to self
        
        print(f"Sending test email from {from_email} to {recipient_list}...")
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        print("SUCCESS: Email sent successfully!")
    except Exception as e:
        print(f"ERROR: Failed to send email: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smtp()
