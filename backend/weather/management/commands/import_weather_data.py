"""
Django management command to import historical ECCC climate data for BC stations.
Downloads hourly climate data from 2000 onwards and stores in the database.
"""

import csv
import requests
from datetime import datetime
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from weather.models import WeatherStation, HourlyObservation


class Command(BaseCommand):
    help = 'Import ECCC hourly climate data for BC stations from 2000 onwards'

    def add_arguments(self, parser):
        parser.add_argument(
            '--station-id',
            type=str,
            help='Import data for a specific station ID (e.g., 1010066)',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Import data for a specific year only',
        )
        parser.add_argument(
            '--start-year',
            type=int,
            default=2000,
            help='Start year for data import (default: 2000)',
        )
        parser.add_argument(
            '--end-year',
            type=int,
            default=datetime.now().year,
            help='End year for data import (default: current year)',
        )
        parser.add_argument(
            '--list-stations',
            action='store_true',
            help='List all available BC stations from the directory',
        )

    def handle(self, *args, **options):
        if options['list_stations']:
            self.list_stations()
            return

        station_id = options.get('station_id')
        year = options.get('year')
        start_year = options.get('start_year')
        end_year = options.get('end_year')

        if year:
            start_year = year
            end_year = year

        if station_id:
            self.import_station_data(station_id, start_year, end_year)
        else:
            self.stdout.write(
                self.style.WARNING(
                    'No station specified. Use --station-id or --list-stations to see available stations.'
                )
            )

    def list_stations(self):
        """List all CSV files available in the BC hourly data directory."""
        self.stdout.write(self.style.SUCCESS('Fetching list of available BC stations...'))
        
        # Try to get the directory listing
        base_url = 'https://dd.weather.gc.ca/today/climate/observations/hourly/csv/BC/'
        
        try:
            response = requests.get(base_url)
            response.raise_for_status()
            
            # Parse the HTML to find CSV files
            # This is a simple approach - in production you might want to use BeautifulSoup
            import re
            csv_files = re.findall(r'climate_hourly_BC_(\d+)_\d{4}_P1H\.csv', response.text)
            station_ids = sorted(set(csv_files))
            
            self.stdout.write(self.style.SUCCESS(f'\nFound {len(station_ids)} BC stations with hourly data:'))
            for station_id in station_ids:
                self.stdout.write(f'  - {station_id}')
            
            self.stdout.write(self.style.SUCCESS(f'\nTo import data for a station, run:'))
            self.stdout.write(f'  python manage.py import_weather_data --station-id XXXXXXX')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error fetching station list: {e}'))

    def import_station_data(self, station_id, start_year, end_year):
        """Import data for a specific station across multiple years."""
        self.stdout.write(
            self.style.SUCCESS(
                f'Importing data for station {station_id} from {start_year} to {end_year}...'
            )
        )

        # Get or create the station
        station, created = WeatherStation.objects.get_or_create(
            station_id=station_id,
            defaults={
                'name': f'Station {station_id}',  # Will be updated from CSV
                'province': 'BC',
            }
        )

        if created:
            self.stdout.write(self.style.SUCCESS(f'Created new station: {station_id}'))
        else:
            self.stdout.write(f'Found existing station: {station.name}')

        total_imported = 0
        total_skipped = 0

        for year in range(start_year, end_year + 1):
            imported, skipped = self.import_year_data(station, year)
            total_imported += imported
            total_skipped += skipped

        # Update last_updated timestamp
        station.last_updated = timezone.now()
        station.save()

        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Imported {total_imported} observations, skipped {total_skipped} duplicates.'
            )
        )

    def import_year_data(self, station, year):
        """Import data for a specific station and year."""
        url = f'https://dd.weather.gc.ca/today/climate/observations/hourly/csv/BC/climate_hourly_BC_{station.station_id}_{year}_P1H.csv'
        
        self.stdout.write(f'  Fetching {year} data from: {url}')

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV
            csv_data = response.text.splitlines()
            reader = csv.DictReader(csv_data)
            
            observations = []
            imported_count = 0
            skipped_count = 0
            
            for row in reader:
                # Update station metadata from first row
                if not station.name or station.name.startswith('Station '):
                    station.name = row.get('Station Name', f'Station {station.station_id}')
                    station.latitude = self.parse_decimal(row.get('Latitude (y)'))
                    station.longitude = self.parse_decimal(row.get('Longitude (x)'))
                    station.elevation = self.parse_decimal(row.get('Elevation'))
                    station.save()
                
                # Parse observation time
                obs_time = self.parse_datetime(row)
                if not obs_time:
                    continue
                
                # Check if observation already exists
                if HourlyObservation.objects.filter(
                    station=station,
                    observation_time=obs_time
                ).exists():
                    skipped_count += 1
                    continue
                
                # Create observation object
                # Handle both possible column name formats
                temp_col = 'Temp (°C)' if 'Temp (°C)' in row else 'Temp (�C)'
                dew_col = 'Dew Point Temp (°C)' if 'Dew Point Temp (°C)' in row else 'Dew Point Temp (�C)'
                
                observation = HourlyObservation(
                    station=station,
                    observation_time=obs_time,
                    temperature=self.parse_decimal(row.get(temp_col)),
                    dew_point=self.parse_decimal(row.get(dew_col)),
                    relative_humidity=self.parse_int(row.get('Rel Hum (%)')),
                    precipitation=self.parse_decimal(row.get('Precip. Amount (mm)')),
                    wind_direction=self.parse_int(row.get('Wind Dir (10s deg)')),
                    wind_speed=self.parse_decimal(row.get('Wind Spd (km/h)')),
                    visibility=self.parse_decimal(row.get('Visibility (km)')),
                    station_pressure=self.parse_decimal(row.get('Stn Press (kPa)')),
                    humidex=self.parse_decimal(row.get('Hmdx')),
                    wind_chill=self.parse_decimal(row.get('Wind Chill')),
                    weather_description=self.safe_get_weather(row),
                )
                
                observations.append(observation)
                imported_count += 1
                
                # Bulk insert every 1000 observations
                if len(observations) >= 1000:
                    HourlyObservation.objects.bulk_create(observations, ignore_conflicts=True)
                    observations = []
                    self.stdout.write('.', ending='')
                    self.stdout.flush()
            
            # Insert remaining observations
            if observations:
                HourlyObservation.objects.bulk_create(observations, ignore_conflicts=True)
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n    ✓ {year}: Imported {imported_count}, skipped {skipped_count}'
                )
            )
            
            return imported_count, skipped_count
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                self.stdout.write(
                    self.style.WARNING(f'    ✗ {year}: No data available (404)')
                )
            else:
                self.stdout.write(
                    self.style.ERROR(f'    ✗ {year}: HTTP error {e.response.status_code}')
                )
            return 0, 0
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'    ✗ {year}: Error - {str(e)}')
            )
            return 0, 0

    def parse_datetime(self, row):
        """Parse datetime from CSV row."""
        try:
            # ECCC format: "2024-01-15 13:00"
            date_time_str = row.get('Date/Time (LST)', '').strip()
            if not date_time_str:
                return None
            
            # Parse as naive datetime
            dt = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
            
            # Make timezone aware (LST is Local Standard Time for the station)
            # For BC, this is typically PST (UTC-8) or PDT (UTC-7)
            # For simplicity, we'll store as-is and treat as UTC
            # In production, you might want to handle timezone conversion
            return timezone.make_aware(dt, timezone.utc)
            
        except (ValueError, AttributeError) as e:
            return None

    def parse_decimal(self, value):
        """Parse a decimal value from string, handling missing/invalid values."""
        if not value or value.strip() == '':
            return None
        try:
            return Decimal(value.strip())
        except (InvalidOperation, ValueError):
            return None

    def parse_int(self, value):
        """Parse an integer value from string, handling missing/invalid values."""
        if not value or value.strip() == '':
            return None
        try:
            return int(float(value.strip()))
        except (ValueError, TypeError):
            return None

    def safe_get_weather(self, row):
        """Safely get weather description, handling missing values."""
        weather = row.get('Weather', '')
        if weather and weather.strip() and weather.strip().upper() not in ('NA', 'N/A', ''):
            return weather.strip()
        return None
