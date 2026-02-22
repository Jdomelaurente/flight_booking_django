import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from django.contrib.auth.models import User
users = User.objects.all()
for u in users:
    print(f"Username: {u.username}, Email: {u.email}, Active: {u.is_active}")
