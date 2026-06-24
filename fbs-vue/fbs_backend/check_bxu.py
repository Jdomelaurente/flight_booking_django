from app.models import Airport, Route
bxu = Airport.objects.filter(code='BXU').first()
dvo = Airport.objects.filter(code='DVO').first()
print(f'BXU exists: {bool(bxu)}')
if bxu and dvo:
    route = Route.objects.filter(origin_airport=dvo, destination_airport=bxu).first()
    print(f'DVO-BXU Route exists: {bool(route)}')
else:
    print('DVO or BXU not found')
