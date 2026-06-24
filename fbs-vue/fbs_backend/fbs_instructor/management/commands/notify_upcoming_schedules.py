from django.core.management.base import BaseCommand
from fbs_instructor.utils import check_and_send_upcoming_notifications
import time

class Command(BaseCommand):
    help = 'Checks for upcoming section schedules and notifies instructors 5 minutes in advance'

    def add_arguments(self, parser):
        parser.add_argument(
            '--loop',
            action='store_true',
            help='Run in a continuous loop every 60 seconds (useful for development)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting schedule notification checker...'))
        
        if options['loop']:
            self.stdout.write(self.style.WARNING('Running in loop mode. Press Ctrl+C to stop.'))
            while True:
                count = check_and_send_upcoming_notifications()
                if count > 0:
                    self.stdout.write(self.style.SUCCESS(f"Sent {count} notifications."))
                time.sleep(60)
        else:
            count = check_and_send_upcoming_notifications()
            self.stdout.write(self.style.SUCCESS(f"Finished check. Sent {count} notifications."))
