
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import Airline, Aircraft, Flight, Schedule, Country, Route, Airport

models = [Country, Airline, Aircraft, Airport, Route, Flight, Schedule]

for model in models:
    fields = [f.name for f in model._meta.get_fields() if not f.auto_created and not f.is_relation]
    relations = [f.name for f in model._meta.get_fields() if f.is_relation and (f.one_to_one or f.many_to_one)]
    print(f"{model.__name__} Fields: {fields}")
    print(f"{model.__name__} Relations: {relations}")
    print("-" * 20)
