import os
import django
from django.utils import timezone
from datetime import datetime
import pytz

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

print(f"--- TIME CHECK ---")
print(f"System Time (Local): {datetime.now()}")
print(f"Django Time (Now):   {timezone.now()}")

# Get local time in Asia/Manila 
manila_tz = pytz.timezone('Asia/Manila')
manila_time = timezone.now().astimezone(manila_tz)
print(f"Manila Time:         {manila_time}")

# Check settings
from django.conf import settings
print(f"--- SETTINGS ---")
print(f"TIME_ZONE: {settings.TIME_ZONE}")
print(f"USE_TZ:    {settings.USE_TZ}")
