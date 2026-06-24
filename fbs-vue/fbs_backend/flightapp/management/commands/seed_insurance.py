from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from app.models import (
    InsuranceBenefit,
    InsuranceCoverageType,
    InsuranceProvider,
    PlanCoverage,
    TravelInsurancePlan,
)


class Command(BaseCommand):
    help = "Seed travel insurance providers, benefits, coverage types, and plans (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        providers = self._seed_providers()
        coverage_types = self._seed_coverage_types()
        benefits = self._seed_benefits()
        self._seed_plans(providers=providers, coverage_types=coverage_types, benefits=benefits)

        self.stdout.write(self.style.SUCCESS("✅ Travel insurance seed completed."))

    def _seed_providers(self):
        provider_defs = [
            {
                "code": "MAL",
                "name": "Malayan Insurance",
                "description": "Philippine-based travel insurance provider.",
                "contact_email": "support@malayan.com",
                "contact_phone": "+63 2 0000 0000",
                "default_commission_rate": Decimal("15.00"),
                "is_active": True,
            },
            {
                "code": "AXA",
                "name": "AXA Travel Insurance",
                "description": "International travel insurance provider.",
                "contact_email": "support@axa.com",
                "contact_phone": "+63 2 0000 0001",
                "default_commission_rate": Decimal("18.00"),
                "is_active": True,
            },
            {
                "code": "APL",
                "name": "APL Insurance",
                "description": "Premium coverage options for frequent travelers.",
                "contact_email": "support@apl.com",
                "contact_phone": "+63 2 0000 0002",
                "default_commission_rate": Decimal("20.00"),
                "is_active": True,
            },
        ]

        providers = {}
        for p in provider_defs:
            provider, created = InsuranceProvider.objects.get_or_create(
                code=p["code"],
                defaults={k: v for k, v in p.items() if k != "code"},
            )
            if not created:
                # Keep it idempotent but ensure active
                provider.is_active = True
                provider.save(update_fields=["is_active"])

            providers[provider.code] = provider
            self.stdout.write(f"- Provider: {provider.code} {provider.name}")

        return providers

    def _seed_coverage_types(self):
        coverage_defs = [
            {
                "name": "Medical",
                "code": "MED",
                "description": "Medical emergency and hospitalization",
                "unit": "PHP",
                "icon_class": "fas fa-stethoscope",
                "display_order": 1,
                "is_active": True,
            },
            {
                "name": "Trip Cancellation",
                "code": "CANCEL",
                "description": "Reimbursement for prepaid trip costs",
                "unit": "PHP",
                "icon_class": "fas fa-ban",
                "display_order": 2,
                "is_active": True,
            },
            {
                "name": "Baggage",
                "code": "BAGGAGE",
                "description": "Lost, damaged, or delayed baggage",
                "unit": "PHP",
                "icon_class": "fas fa-suitcase",
                "display_order": 3,
                "is_active": True,
            },
            {
                "name": "Personal Accident",
                "code": "ACCIDENT",
                "description": "Accidental death or disability",
                "unit": "PHP",
                "icon_class": "fas fa-user-injured",
                "display_order": 4,
                "is_active": True,
            },
            {
                "name": "Flight Delay",
                "code": "DELAY",
                "description": "Compensation for flight delays",
                "unit": "per hour",
                "icon_class": "fas fa-clock",
                "display_order": 5,
                "is_active": True,
            },
        ]

        coverages = {}
        for c in coverage_defs:
            cov, created = InsuranceCoverageType.objects.get_or_create(
                code=c["code"],
                defaults={k: v for k, v in c.items() if k != "code"},
            )
            if not created:
                cov.is_active = True
                cov.save(update_fields=["is_active"])

            coverages[cov.code] = cov
            self.stdout.write(f"- CoverageType: {cov.code} {cov.name}")

        return coverages

    def _seed_benefits(self):
        benefit_defs = [
            {"name": "24/7 Emergency Assistance", "icon_class": "fas fa-phone-alt", "display_order": 1, "is_active": True},
            {"name": "Medical Evacuation", "icon_class": "fas fa-ambulance", "display_order": 2, "is_active": True},
            {"name": "Trip Interruption", "icon_class": "fas fa-exclamation-triangle", "display_order": 3, "is_active": True},
            {"name": "Lost Passport Assistance", "icon_class": "fas fa-passport", "display_order": 4, "is_active": True},
            {"name": "Legal Assistance", "icon_class": "fas fa-balance-scale", "display_order": 5, "is_active": True},
            {"name": "Family Coverage", "icon_class": "fas fa-users", "display_order": 6, "is_active": True},
        ]

        benefits = {}
        for b in benefit_defs:
            benefit, created = InsuranceBenefit.objects.get_or_create(
                name=b["name"],
                defaults={k: v for k, v in b.items() if k != "name"},
            )
            if not created:
                benefit.is_active = True
                benefit.save(update_fields=["is_active"])

            benefits[benefit.name] = benefit
            self.stdout.write(f"- Benefit: {benefit.name}")

        return benefits

    def _seed_plans(self, *, providers, coverage_types, benefits):
        plan_defs = [
            {
                "provider_code": "MAL",
                "name": "Travel Lite",
                "description": "Basic coverage for occasional travelers",
                "retail_price": Decimal("500.00"),
                "wholesale_price": Decimal("425.00"),
                "plan_type": "basic",
                "best_for": "Short domestic trips",
                "coverage_duration_days": 15,
                "seller_type": "booking_platform",
                "is_default": True,
                "display_order": 1,
                "policy_document_url": "https://example.com/policies/travel-lite.pdf",
                "terms_conditions_url": "https://example.com/terms/travel-lite",
                "claims_contact": "Email: claims@malayan.com | Hotline: +63 2 0000 0000",
                "coverages": [
                    {"coverage_code": "MED", "amount": Decimal("100000.00")},
                    {"coverage_code": "BAGGAGE", "amount": Decimal("20000.00")},
                ],
                "benefits": ["24/7 Emergency Assistance"],
            },
            {
                "provider_code": "AXA",
                "name": "Travel Standard",
                "description": "Comprehensive coverage for regular travelers",
                "retail_price": Decimal("1200.00"),
                "wholesale_price": Decimal("984.00"),
                "plan_type": "standard",
                "best_for": "International trips",
                "coverage_duration_days": 30,
                "seller_type": "booking_platform",
                "is_default": False,
                "display_order": 2,
                "policy_document_url": "https://example.com/policies/travel-standard.pdf",
                "terms_conditions_url": "https://example.com/terms/travel-standard",
                "claims_contact": "Email: claims@axa.com | Hotline: +63 2 0000 0001",
                "coverages": [
                    {"coverage_code": "MED", "amount": Decimal("500000.00")},
                    {"coverage_code": "CANCEL", "amount": Decimal("50000.00")},
                    {"coverage_code": "BAGGAGE", "amount": Decimal("50000.00")},
                    {"coverage_code": "DELAY", "amount": Decimal("1000.00")},
                ],
                "benefits": [
                    "24/7 Emergency Assistance",
                    "Medical Evacuation",
                    "Lost Passport Assistance",
                ],
            },
            {
                "provider_code": "APL",
                "name": "Travel Premium",
                "description": "Premium coverage for frequent travelers",
                "retail_price": Decimal("2500.00"),
                "wholesale_price": Decimal("2050.00"),
                "plan_type": "premium",
                "best_for": "Business and luxury travel",
                "coverage_duration_days": 60,
                "seller_type": "airline",
                "is_default": False,
                "display_order": 3,
                "policy_document_url": "https://example.com/policies/travel-premium.pdf",
                "terms_conditions_url": "https://example.com/terms/travel-premium",
                "claims_contact": "Email: claims@apl.com | Hotline: +63 2 0000 0002",
                "coverages": [
                    {"coverage_code": "MED", "amount": Decimal("1000000.00")},
                    {"coverage_code": "CANCEL", "amount": Decimal("100000.00")},
                    {"coverage_code": "BAGGAGE", "amount": Decimal("100000.00")},
                    {"coverage_code": "ACCIDENT", "amount": Decimal("2000000.00")},
                    {"coverage_code": "DELAY", "amount": Decimal("2000.00")},
                ],
                "benefits": [
                    "24/7 Emergency Assistance",
                    "Medical Evacuation",
                    "Trip Interruption",
                    "Lost Passport Assistance",
                    "Legal Assistance",
                    "Family Coverage",
                ],
            },
            {
                "provider_code": "AXA",
                "name": "Travel Comprehensive",
                "description": "Higher limits + broader protection for long trips",
                "retail_price": Decimal("3500.00"),
                "wholesale_price": Decimal("2870.00"),
                "plan_type": "comprehensive",
                "best_for": "Long international trips",
                "coverage_duration_days": 90,
                "seller_type": "booking_platform",
                "is_default": False,
                "display_order": 4,
                "policy_document_url": "https://example.com/policies/travel-comprehensive.pdf",
                "terms_conditions_url": "https://example.com/terms/travel-comprehensive",
                "claims_contact": "Email: claims@axa.com | Hotline: +63 2 0000 0001",
                "coverages": [
                    {"coverage_code": "MED", "amount": Decimal("2000000.00")},
                    {"coverage_code": "CANCEL", "amount": Decimal("150000.00")},
                    {"coverage_code": "BAGGAGE", "amount": Decimal("150000.00")},
                    {"coverage_code": "ACCIDENT", "amount": Decimal("3000000.00")},
                    {"coverage_code": "DELAY", "amount": Decimal("3000.00")},
                ],
                "benefits": [
                    "24/7 Emergency Assistance",
                    "Medical Evacuation",
                    "Trip Interruption",
                    "Lost Passport Assistance",
                    "Legal Assistance",
                ],
            },
            {
                "provider_code": "MAL",
                "name": "Family Protect",
                "description": "Designed for families traveling together",
                "retail_price": Decimal("1800.00"),
                "wholesale_price": Decimal("1530.00"),
                "plan_type": "standard",
                "best_for": "Family trips",
                "coverage_duration_days": 30,
                "seller_type": "booking_platform",
                "is_default": False,
                "display_order": 5,
                "policy_document_url": "https://example.com/policies/family-protect.pdf",
                "terms_conditions_url": "https://example.com/terms/family-protect",
                "claims_contact": "Email: claims@malayan.com | Hotline: +63 2 0000 0000",
                "coverages": [
                    {"coverage_code": "MED", "amount": Decimal("800000.00")},
                    {"coverage_code": "CANCEL", "amount": Decimal("75000.00")},
                    {"coverage_code": "BAGGAGE", "amount": Decimal("80000.00")},
                    {"coverage_code": "DELAY", "amount": Decimal("1500.00")},
                ],
                "benefits": [
                    "24/7 Emergency Assistance",
                    "Medical Evacuation",
                    "Family Coverage",
                ],
            },
        ]

        for p in plan_defs:
            provider = providers[p["provider_code"]]

            plan, created = TravelInsurancePlan.objects.get_or_create(
                provider=provider,
                name=p["name"],
                defaults={
                    "description": p["description"],
                    "retail_price": p["retail_price"],
                    "wholesale_price": p["wholesale_price"],
                    "plan_type": p["plan_type"],
                    "best_for": p["best_for"],
                    "coverage_duration_days": p["coverage_duration_days"],
                    "seller_type": p["seller_type"],
                    "policy_document_url": p.get("policy_document_url"),
                    "terms_conditions_url": p.get("terms_conditions_url"),
                    "claims_contact": p.get("claims_contact"),
                    "is_default": p["is_default"],
                    "display_order": p["display_order"],
                    "is_active": True,
                },
            )

            if not created:
                # Ensure stable ordering and active
                changed = False
                if plan.display_order != p["display_order"]:
                    plan.display_order = p["display_order"]
                    changed = True
                if not plan.is_active:
                    plan.is_active = True
                    changed = True
                if changed:
                    plan.save(update_fields=["display_order", "is_active"])

            # Enforce only one default (best-effort)
            if p["is_default"]:
                TravelInsurancePlan.objects.filter(is_default=True).exclude(id=plan.id).update(is_default=False)

            # Coverages
            for c in p["coverages"]:
                cov_type = coverage_types[c["coverage_code"]]
                PlanCoverage.objects.get_or_create(
                    insurance_plan=plan,
                    coverage_type=cov_type,
                    defaults={"amount": c["amount"]},
                )

            # Benefits
            for benefit_name in p["benefits"]:
                benefit = benefits.get(benefit_name)
                if benefit:
                    plan.benefits.add(benefit)

            self.stdout.write(f"- Plan: {plan.name} ({provider.code})")
