from rest_framework import viewsets, permissions

from app.models import TravelInsurancePlan
from app.serializers import TravelInsurancePlanSerializer


class TravelInsurancePlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset exposing active travel insurance plans.
    Supports optional ?airline_id=<id> query param to filter by airline.
    Used by the Add-ons page to show carrier-specific insurance options.
    """
    permission_classes = [permissions.AllowAny]
    serializer_class = TravelInsurancePlanSerializer

    def get_queryset(self):
        qs = TravelInsurancePlan.objects.filter(is_active=True).order_by('display_order', 'retail_price')
        airline_id = self.request.query_params.get('airline_id')
        if airline_id:
            qs = qs.filter(airlines__id=airline_id)
        return qs
