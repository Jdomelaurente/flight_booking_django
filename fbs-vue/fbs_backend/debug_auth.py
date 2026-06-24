import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth.models import User

username = 'admin'
password = 'admin12345'

user = authenticate(username=username, password=password)
print(f"Authenticate result: {user}")

if user:
    print(f"User found: {user.username}")
    print(f"is_staff: {user.is_staff}")
    print(f"is_active: {user.is_active}")
else:
    print("Authentication failed.")
    # Check if user exists at all
    u = User.objects.filter(username=username).first()
    if u:
        print(f"User exists: {u.username}")
        print(f"Check password admin12345: {u.check_password(password)}")
    else:
        print("User does not exist.")
