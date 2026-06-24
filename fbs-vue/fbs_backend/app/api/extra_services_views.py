from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from ..models import (
    Country, SeatClassFeature, InsuranceProvider, InsuranceBenefit,
    InsuranceCoverageType, TravelInsurancePlan, PlanCoverage,
    MealCategory, MealOption, AssistanceService, BaggageOption, PricingConfiguration
)
from ..serializers import (
    CountrySerializer, SeatClassFeatureSerializer,
    InsuranceProviderSerializer, InsuranceBenefitSerializer, InsuranceCoverageTypeSerializer,
    TravelInsurancePlanSerializer, PlanCoverageSerializer,
    MealCategorySerializer, MealOptionSerializer, AssistanceServiceSerializer,
    BaggageOptionSerializer, PricingConfigurationSerializer
)

class CountryViewSet(viewsets.ModelViewSet):
    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer
    permission_classes = [AllowAny]
    pagination_class = None

class SeatClassFeatureViewSet(viewsets.ModelViewSet):
    queryset = SeatClassFeature.objects.all()
    serializer_class = SeatClassFeatureSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class InsuranceProviderViewSet(viewsets.ModelViewSet):
    queryset = InsuranceProvider.objects.all()
    serializer_class = InsuranceProviderSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class InsuranceBenefitViewSet(viewsets.ModelViewSet):
    queryset = InsuranceBenefit.objects.all()
    serializer_class = InsuranceBenefitSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class InsuranceCoverageTypeViewSet(viewsets.ModelViewSet):
    queryset = InsuranceCoverageType.objects.all()
    serializer_class = InsuranceCoverageTypeSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class TravelInsurancePlanViewSet(viewsets.ModelViewSet):
    queryset = TravelInsurancePlan.objects.all()
    serializer_class = TravelInsurancePlanSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class PlanCoverageViewSet(viewsets.ModelViewSet):
    queryset = PlanCoverage.objects.all()
    serializer_class = PlanCoverageSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class MealCategoryViewSet(viewsets.ModelViewSet):
    queryset = MealCategory.objects.all()
    serializer_class = MealCategorySerializer
    permission_classes = [AllowAny]
    pagination_class = None

class MealOptionViewSet(viewsets.ModelViewSet):
    queryset = MealOption.objects.all()
    serializer_class = MealOptionSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class AssistanceServiceViewSet(viewsets.ModelViewSet):
    queryset = AssistanceService.objects.all()
    serializer_class = AssistanceServiceSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class BaggageOptionViewSet(viewsets.ModelViewSet):
    queryset = BaggageOption.objects.all()
    serializer_class = BaggageOptionSerializer
    permission_classes = [AllowAny]
    pagination_class = None

class PricingConfigurationViewSet(viewsets.ModelViewSet):
    queryset = PricingConfiguration.objects.all()
    serializer_class = PricingConfigurationSerializer
    permission_classes = [AllowAny]
    pagination_class = None
