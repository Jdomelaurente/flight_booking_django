from rest_framework import viewsets, permissions

from app.models import TravelInsurancePlan
from .serializers import TravelInsurancePlanSerializer


class TravelInsurancePlanViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset exposing active travel insurance plans.
    Used by the Add-ons page to show a simple insurance card.
    """
    permission_classes = [permissions.AllowAny]
    queryset = TravelInsurancePlan.objects.filter(is_active=True).order_by('display_order', 'retail_price')
    serializer_class = TravelInsurancePlanSerializer

