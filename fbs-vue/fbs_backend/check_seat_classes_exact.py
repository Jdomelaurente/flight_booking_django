import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import SeatClass

# Check exact SeatClass names
classes = SeatClass.objects.all()
print(f"Total SeatClasses: {classes.count()}")
print("--- START ---")
for c in classes:
    print(f"ID: {c.id} | Name: '{c.name}'")
print("--- END ---")
