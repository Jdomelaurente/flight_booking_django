import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Aircraft

def dump_configs():
    with open('layout_dump.json', 'w') as f:
        data = []
        for aircraft in Aircraft.objects.all():
            data.append({
                'id': aircraft.id,
                'model': aircraft.model,
                'airline': aircraft.airline.name,
                'layout_config': aircraft.layout_config
            })
        json.dump(data, f, indent=2)
    print("Dumped to layout_dump.json")

if __name__ == '__main__':
    dump_configs()
