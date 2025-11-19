"""
Django management command to import BC Wildfire Service fire weather data.
Downloads daily CSV files from the BC Wildfire Service Data Mart.
"""

import csv
import requests
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import pytz
from weather.models import WeatherStation, HourlyObservation


class Command(BaseCommand):
    help = 'Import BC Wildfire Service fire weather data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date (YYYY-MM-DD). Default: 2025-01-01',
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date (YYYY-MM-DD). Default: yesterday',
        )
        parser.add_argument(
            '--date',
            type=str,
            help='Import specific date only (YYYY-MM-DD)',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Show detailed progress information',
        )

    def handle(self, *args, **options):
        self.verbose = options.get('verbose', False)
        
        if options['date']:
            # Import single date
            date_str = options['date']
            try:
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                self.import_date(date)
            except ValueError:
                self.stderr.write(self.style.ERROR(f'Invalid date format: {date_str}'))
                return
        else:
            # Import date range
            start_date = options['start_date']
            end_date = options['end_date']

            if start_date:
                try:
                    start = datetime.strptime(start_date, '%Y-%m-%d').date()
                except ValueError:
                    self.stderr.write(self.style.ERROR(f'Invalid start date: {start_date}'))
                    return
            else:
                start = datetime(2025, 1, 1).date()

            if end_date:
                try:
                    end = datetime.strptime(end_date, '%Y-%m-%d').date()
                except ValueError:
                    self.stderr.write(self.style.ERROR(f'Invalid end date: {end_date}'))
                    return
            else:
                # Default to yesterday
                end = (datetime.now() - timedelta(days=1)).date()

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nImporting BC Wildfire Service data from {start} to {end}\n'
                )
            )

            current = start
            success_count = 0
            error_count = 0
            total_observations = 0
            unique_stations = set()

            while current <= end:
                try:
                    result = self.import_date(current)
                    obs_count = result['observations']
                    station_count = result['stations']
                    
                    if obs_count > 0:
                        success_count += 1
                        total_observations += obs_count
                        unique_stations.update(result['station_codes'])
                        
                        if self.verbose:
                            self.stdout.write(
                                self.style.SUCCESS(
                                    f'  ✓ {current}: {obs_count} observations from {station_count} stations'
                                )
                            )
                        else:
                            self.stdout.write(
                                self.style.SUCCESS(f'  ✓ {current}: {obs_count} observations')
                            )
                    else:
                        if self.verbose:
                            self.stdout.write(f'  - {current}: No data available')
                except Exception as e:
                    error_count += 1
                    self.stderr.write(
                        self.style.ERROR(f'  ✗ {current}: {str(e)}')
                    )

                current += timedelta(days=1)

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n{"="*70}\n'
                    f'Import Complete!\n'
                    f'{"="*70}\n'
                    f'Date Range: {start} to {end}\n'
                    f'Success: {success_count} days\n'
                    f'Errors: {error_count} days\n'
                    f'Total Observations: {total_observations:,}\n'
                    f'Unique Stations: {len(unique_stations)}\n'
                    f'{"="*70}\n'
                )
            )

    def import_date(self, date):
        """Import data for a specific date."""
        year = date.year
        date_str = date.strftime('%Y-%m-%d')
        url = f'https://www.for.gov.bc.ca/ftp/HPR/external/!publish/BCWS_DATA_MART/{year}/{date_str}.csv'

        try:
            # Download CSV
            response = requests.get(url, timeout=30)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                # File not available (future date or no data)
                return {'observations': 0, 'stations': 0, 'station_codes': set()}
            raise
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download data: {str(e)}")

        # Parse CSV
        content = response.content.decode('utf-8-sig')  # utf-8-sig removes BOM
        lines = content.splitlines()
        
        if len(lines) <= 1:
            # No data rows (only header or empty)
            return {'observations': 0, 'stations': 0, 'station_codes': set()}
            
        reader = csv.DictReader(lines)

        observations = []
        stations_created = set()
        pacific = pytz.timezone('America/Vancouver')

        for row in reader:
            try:
                # Get station code and name
                # First column might have quotes: "STATION_CODE" 
                station_code = None
                station_name = None
                
                # Try different possible keys
                for key in row.keys():
                    if 'STATION_CODE' in key:
                        station_code = row[key]
                    if 'STATION_NAME' in key or key == 'STATION_NAME':
                        station_name = row[key]
                    if station_code and station_name:
                        break
                
                if not station_code or not station_name:
                    continue
                    
                station_code = str(station_code).strip().strip('"')
                station_name = str(station_name).strip().strip('"')

                # Get station metadata
                latitude = self.parse_decimal(row.get('LATITUDE'))
                longitude = self.parse_decimal(row.get('LONGITUDE'))
                elevation = self.parse_decimal(row.get('ELEVATION'))

                # Create or update station
                station, created = WeatherStation.objects.get_or_create(
                    station_code=station_code,
                    defaults={
                        'name': station_name,
                        'latitude': latitude,
                        'longitude': longitude,
                        'elevation': elevation,
                    }
                )
                
                # Update station metadata if it changed
                if not created:
                    updated = False
                    if station.name != station_name:
                        station.name = station_name
                        updated = True
                    if latitude and station.latitude != latitude:
                        station.latitude = latitude
                        updated = True
                    if longitude and station.longitude != longitude:
                        station.longitude = longitude
                        updated = True
                    if elevation and station.elevation != elevation:
                        station.elevation = elevation
                        updated = True
                    if updated:
                        station.save()
                
                stations_created.add(station_code)

                # Parse observation time (format: 2025111700 = YYYYMMDDHH)
                datetime_str = row.get('DATE_TIME', '').strip()
                if not datetime_str:
                    continue
                    
                # Parse as naive datetime
                observation_time_naive = datetime.strptime(datetime_str, '%Y%m%d%H')
                
                # Make timezone-aware (Pacific time)
                observation_time = pacific.localize(observation_time_naive)

                # Create observation
                obs = HourlyObservation(
                    station=station,
                    observation_time=observation_time,
                    # Basic weather measurements (hourly values from CSV)
                    temperature=self.parse_decimal(row.get('HOURLY_TEMPERATURE')),
                    relative_humidity=self.parse_int(row.get('HOURLY_RELATIVE_HUMIDITY')),
                    precipitation=self.parse_decimal(row.get('HOURLY_PRECIPITATION')),
                    wind_speed=self.parse_decimal(row.get('HOURLY_WIND_SPEED')),
                    wind_direction=self.parse_int(row.get('HOURLY_WIND_DIRECTION')),
                    wind_gust=self.parse_decimal(row.get('HOURLY_WIND_GUST')),
                    # Hourly Fire Weather Indices
                    hourly_ffmc=self.parse_decimal(row.get('HOURLY_FINE_FUEL_MOISTURE_CODE')),
                    hourly_isi=self.parse_decimal(row.get('HOURLY_INITIAL_SPREAD_INDEX')),
                    hourly_fwi=self.parse_decimal(row.get('HOURLY_FIRE_WEATHER_INDEX')),
                    # Daily Fire Weather Indices
                    ffmc=self.parse_decimal(row.get('FINE_FUEL_MOISTURE_CODE')),
                    dmc=self.parse_decimal(row.get('DUFF_MOISTURE_CODE')),
                    dc=self.parse_decimal(row.get('DROUGHT_CODE')),
                    isi=self.parse_decimal(row.get('INITIAL_SPREAD_INDEX')),
                    bui=self.parse_decimal(row.get('BUILDUP_INDEX')),
                    fwi=self.parse_decimal(row.get('FIRE_WEATHER_INDEX')),
                    danger_rating=row.get('DANGER_RATING', '').strip() or None,
                    # Additional measurements
                    snow_depth=self.parse_decimal(row.get('SNOW_DEPTH')),
                    solar_radiation=self.parse_decimal(row.get('SOLAR_RADIATION_LICOR')),
                )

                observations.append(obs)

            except Exception as e:
                self.stderr.write(
                    self.style.WARNING(
                        f'Skipping row for station {row.get("STATION_CODE")}: {str(e)}'
                    )
                )
                continue

        # Bulk create observations
        if observations:
            with transaction.atomic():
                HourlyObservation.objects.bulk_create(
                    observations,
                    ignore_conflicts=True,
                    batch_size=1000
                )
                
                # Update last_updated for all affected stations
                for station_code in stations_created:
                    WeatherStation.objects.filter(station_code=station_code).update(
                        last_updated=timezone.now()
                    )

        return {
            'observations': len(observations),
            'stations': len(stations_created),
            'station_codes': stations_created
        }

    def parse_decimal(self, value):
        """Parse a decimal value, handling empty strings and errors."""
        if not value or value.strip() == '':
            return None
        try:
            return Decimal(str(value).strip())
        except (InvalidOperation, ValueError):
            return None

    def parse_int(self, value):
        """Parse an integer value, handling empty strings and errors."""
        if not value or value.strip() == '':
            return None
        try:
            return int(float(str(value).strip()))
        except (ValueError, InvalidOperation):
            return None
