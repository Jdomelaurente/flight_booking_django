import os
import django
import sys

# Setup Django environment
sys.path.append('c:\\Users\\Crissaunt\\Documents\\GitHub\\fbs-vue\\fbs_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fbs_backend.settings')
django.setup()

from app.models import PricingConfiguration

def check_config():
    config = PricingConfiguration.load()
    print("=== Pricing Configuration ===")
    print(f"ID: {config.pk}")
    print(f"anonymous_user_factor: {config.anonymous_user_factor}")
    print(f"days_factor_critical: {config.days_factor_critical} (critical: {config.days_departure_critical} days)")
    print(f"days_factor_near: {config.days_factor_near} (near: {config.days_departure_near} days)")
    print(f"days_factor_medium: {config.days_factor_medium} (medium: {config.days_departure_medium} days)")
    print(f"days_factor_far: {config.days_factor_far} (far: {config.days_departure_far} days)")
    print(f"demand_factor_high: {config.demand_factor_high}")
    print(f"occupancy_factor_high: {config.occupancy_factor_high}")

if __name__ == "__main__":
    check_config()
