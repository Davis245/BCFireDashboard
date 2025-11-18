"""
Django management command to update weather data for all tracked stations.
This should be run hourly via cron to keep data current.
"""

import re
import requests
import csv
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from weather.models import WeatherStation, HourlyObservation


class Command(BaseCommand):
    help = 'Update weather data for all active stations (run hourly)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--station-id',
            type=str,
            help='Update specific station only',
        )
        parser.add_argument(
            '--hours',
            type=int,
            default=48,
            help='Fetch data from the last N hours (default: 48)',
        )

    def handle(self, *args, **options):
        station_id = options.get('station_id')
        hours_back = options.get('hours')
        
        if station_id:
            stations = WeatherStation.objects.filter(
                station_id=station_id,
                is_active=True
            )
        else:
            # Get all active stations with observations
            stations = WeatherStation.objects.filter(
                is_active=True,
                observations__isnull=False
            ).distinct()
        
        total_stations = stations.count()
        
        if total_stations == 0:
            self.stdout.write(
                self.style.WARNING('No active stations to update')
            )
            return
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Updating {total_stations} active stations...'
            )
        )
        
        success_count = 0
        error_count = 0
        total_new_obs = 0
        
        for i, station in enumerate(stations, 1):
            self.stdout.write(
                f'[{i}/{total_stations}] {station.name} ({station.station_id})...',
                ending=' '
            )
            
            try:
                new_obs = self.update_station(station, hours_back)
                total_new_obs += new_obs
                
                if new_obs > 0:
                    self.stdout.write(
                        self.style.SUCCESS(f'✓ {new_obs} new observations')
                    )
                else:
                    self.stdout.write('✓ up to date')
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'✗ Error: {str(e)}')
                )
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nUpdate complete: {success_count} success, {error_count} errors'
            )
        )
        self.stdout.write(f'New observations: {total_new_obs}')

    def update_station(self, station, hours_back):
        """Update a single station with recent data."""
        current_year = datetime.now().year
        
        # Try current year first
        url = f'https://dd.weather.gc.ca/today/climate/observations/hourly/csv/BC/climate_hourly_BC_{station.station_id}_{current_year}_P1H.csv'
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Parse CSV
            csv_data = response.text.splitlines()
            reader = csv.DictReader(csv_data)
            
            # Get cutoff time (only import observations newer than this)
            cutoff_time = timezone.now() - timedelta(hours=hours_back)
            
            observations = []
            new_count = 0
            
            for row in reader:
                # Parse observation time
                obs_time = self.parse_datetime(row)
                if not obs_time or obs_time < cutoff_time:
                    continue
                
                # Check if observation already exists
                if HourlyObservation.objects.filter(
                    station=station,
                    observation_time=obs_time
                ).exists():
                    continue
                
                # Create observation object
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
                new_count += 1
            
            # Bulk insert new observations
            if observations:
                HourlyObservation.objects.bulk_create(
                    observations,
                    ignore_conflicts=True
                )
            
            # Update last_updated timestamp
            station.last_updated = timezone.now()
            station.save(update_fields=['last_updated'])
            
            return new_count
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # Try previous year if current year not available
                if datetime.now().month == 1:
                    return self.update_station_year(
                        station,
                        current_year - 1,
                        cutoff_time
                    )
            raise

    def update_station_year(self, station, year, cutoff_time):
        """Update station for a specific year."""
        url = f'https://dd.weather.gc.ca/today/climate/observations/hourly/csv/BC/climate_hourly_BC_{station.station_id}_{year}_P1H.csv'
        
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        csv_data = response.text.splitlines()
        reader = csv.DictReader(csv_data)
        
        observations = []
        new_count = 0
        
        for row in reader:
            obs_time = self.parse_datetime(row)
            if not obs_time or obs_time < cutoff_time:
                continue
            
            if HourlyObservation.objects.filter(
                station=station,
                observation_time=obs_time
            ).exists():
                continue
            
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
            new_count += 1
        
        if observations:
            HourlyObservation.objects.bulk_create(
                observations,
                ignore_conflicts=True
            )
        
        return new_count

    def parse_datetime(self, row):
        """Parse datetime from CSV row."""
        try:
            date_time_str = row.get('Date/Time (LST)', '').strip()
            if not date_time_str:
                return None
            
            dt = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M')
            return timezone.make_aware(dt, timezone.utc)
            
        except (ValueError, AttributeError):
            return None

    def parse_decimal(self, value):
        """Parse a decimal value from string."""
        if not value or value.strip() == '':
            return None
        try:
            return Decimal(value.strip())
        except (InvalidOperation, ValueError):
            return None

    def parse_int(self, value):
        """Parse an integer value from string."""
        if not value or value.strip() == '':
            return None
        try:
            return int(float(value.strip()))
        except (ValueError, TypeError):
            return None

    def safe_get_weather(self, row):
        """Safely get weather description."""
        weather = row.get('Weather', '')
        if weather and weather.strip() and weather.strip().upper() not in ('NA', 'N/A', ''):
            return weather.strip()
        return None
