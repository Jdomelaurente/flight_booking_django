# flightapp/management/commands/update_ml_prices.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from app.models import Schedule
from decimal import Decimal
from datetime import timedelta

class Command(BaseCommand):
    help = 'Update ML predicted prices for all open schedules'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force update even if recently updated',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Only update prices older than X hours (default: 24)',
        )
        parser.add_argument(
            '--schedule',
            type=int,
            help='Update specific schedule ID only',
        )
    
    def handle(self, *args, **options):
        # Force load the ML model before processing schedules
        self.stdout.write("? Loading ML model...")
        try:
            from flightapp.ml.predictor import predictor
            if not predictor.model:
                predictor.load_model()
            if predictor.model:
                self.stdout.write(self.style.SUCCESS("? ML Model loaded successfully!"))
            else:
                self.stdout.write(self.style.ERROR("? Failed to load ML model"))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"? Error loading ML model: {e}"))
            return
        
        # Base queryset
        if options['schedule']:
            schedules = Schedule.objects.filter(id=options['schedule'])
            self.stdout.write(f"Updating specific schedule ID: {options['schedule']}")
        else:
            # Get schedules that need updating
            schedules = Schedule.objects.filter(
                status='Open',
                departure_time__gte=timezone.now()
            )
            
            if not options['force']:
                # Only update if no ML price or older than X hours
                cutoff_time = timezone.now() - timedelta(hours=options['hours'])
                schedules = schedules.filter(
                    Q(ml_base_price__isnull=True) |
                    Q(ml_price_updated_at__isnull=True) |
                    Q(ml_price_updated_at__lt=cutoff_time)
                )
        
        total = schedules.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS("No schedules need updating"))
            return
        
        self.stdout.write(f"Found {total} schedules to update...")
        
        updated = 0
        failed = 0
        skipped = 0
        
        for i, schedule in enumerate(schedules, 1):
            try:
                # Show progress
                if i % 10 == 0:
                    self.stdout.write(f"  Progress: {i}/{total}")
                
                # Skip if departure is in the past
                if schedule.departure_time < timezone.now():
                    skipped += 1
                    self.stdout.write(
                        self.style.WARNING(f"  ??  {schedule.flight.flight_number}: Departure in past, skipping")
                    )
                    continue
                
                # Update ML price
                success, price = schedule.update_ml_price(save=True)
                
                if success:
                    updated += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ? {schedule.flight.flight_number}: "
                            f"?{price:,.2f} ({schedule.departure_time.strftime('%Y-%m-%d %H:%M')})"
                        )
                    )
                else:
                    failed += 1
                    self.stdout.write(
                        self.style.ERROR(f"  ? {schedule.id}: Failed to update")
                    )
                    
            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(f"  ? {schedule.id}: {str(e)[:100]}")
                )
        
        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"? UPDATE COMPLETE\n"
                f"   Total: {total}\n"
                f"   Updated: {updated}\n"
                f"   Failed: {failed}\n"
                f"   Skipped: {skipped}"
            )
        )
        self.stdout.write("=" * 60)