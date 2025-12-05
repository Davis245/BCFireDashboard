"""
Django management command to automatically update BC Wildfire Service weather data.
This command is designed to be run daily via cron job to keep data current.
It intelligently fetches missing data and handles errors gracefully.
"""

import logging
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db.models import Max
from weather.models import HourlyObservation

# Configure logging
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Automatically update weather data (designed for daily cron jobs)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days-back',
            type=int,
            default=7,
            help='Number of days to look back for missing data (default: 7)',
        )
        parser.add_argument(
            '--backfill',
            action='store_true',
            help='Backfill all missing data from last observation to yesterday',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Email address for error notifications',
        )

    def handle(self, *args, **options):
        days_back = options['days_back']
        backfill = options['backfill']
        email = options.get('email')

        self.stdout.write(
            self.style.SUCCESS(
                '\n' + '='*70 + '\n'
                'BC Fire Weather Dashboard - Automated Data Update\n'
                f'Running at: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
                '='*70 + '\n'
            )
        )

        try:
            if backfill:
                self.backfill_missing_data()
            else:
                self.update_recent_data(days_back)

            self.stdout.write(
                self.style.SUCCESS(
                    '\n' + '='*70 + '\n'
                    '✓ Update completed successfully!\n'
                    '='*70 + '\n'
                )
            )

        except Exception as e:
            error_msg = f'Error during data update: {str(e)}'
            self.stderr.write(self.style.ERROR(f'\n✗ {error_msg}\n'))
            logger.error(error_msg, exc_info=True)
            
            if email:
                self.send_error_notification(email, error_msg)
            
            raise

    def update_recent_data(self, days_back):
        """Update data for the last N days, including yesterday."""
        end_date = (datetime.now() - timedelta(days=1)).date()
        start_date = end_date - timedelta(days=days_back - 1)

        self.stdout.write(f'\nUpdating data for last {days_back} days...')
        self.stdout.write(f'Date range: {start_date} to {end_date}\n')

        # Import the date range
        call_command(
            'import_bcws_data',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            verbose=True
        )

    def backfill_missing_data(self):
        """Backfill all missing data from last observation to yesterday."""
        # Find the most recent observation in the database
        latest_observation = HourlyObservation.objects.aggregate(
            Max('observation_time')
        )['observation_time__max']

        if not latest_observation:
            self.stdout.write(
                self.style.WARNING(
                    'No existing data found. Please use import_bcws_data with a start date.'
                )
            )
            return

        # Start from the day after the latest observation
        start_date = latest_observation.date() + timedelta(days=1)
        end_date = (datetime.now() - timedelta(days=1)).date()

        if start_date > end_date:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nData is already up to date! Latest observation: {latest_observation.date()}'
                )
            )
            return

        days_missing = (end_date - start_date).days + 1

        self.stdout.write(
            self.style.WARNING(
                f'\nBackfilling missing data...\n'
                f'Last observation: {latest_observation.date()}\n'
                f'Missing dates: {start_date} to {end_date} ({days_missing} days)\n'
            )
        )

        # Import the missing date range
        call_command(
            'import_bcws_data',
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            verbose=True
        )

    def send_error_notification(self, email, error_msg):
        """Send email notification on error (requires email configuration)."""
        from django.core.mail import mail_admins
        
        try:
            subject = 'BC Fire Weather Dashboard - Data Update Failed'
            message = f"""
The automated weather data update failed with the following error:

{error_msg}

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Please check the logs and fix the issue.
            """
            
            mail_admins(subject, message, fail_silently=False)
            self.stdout.write(
                self.style.SUCCESS(f'Error notification sent to {email}')
            )
        except Exception as e:
            self.stderr.write(
                self.style.WARNING(
                    f'Failed to send email notification: {str(e)}\n'
                    'Make sure EMAIL_* settings are configured in settings.py'
                )
            )
