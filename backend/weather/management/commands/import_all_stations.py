"""
Django management command to import all BC stations from 2000 onwards.
This is a batch operation that will take several hours to complete.
"""

import re
import requests
import time
from django.core.management.base import BaseCommand
from django.core.management import call_command
from weather.models import WeatherStation


class Command(BaseCommand):
    help = 'Import all BC stations from 2000 to present (batch operation)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--start-year',
            type=int,
            default=2025,
            help='Start year for data import (default: 2025 - current year only)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually importing',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit to first N stations (for testing)',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip stations that already have data',
        )

    def handle(self, *args, **options):
        start_year = options['start_year']
        dry_run = options['dry_run']
        limit = options.get('limit')
        skip_existing = options['skip_existing']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*70}\nBC Fire Weather Dashboard - Full Data Import\n{"="*70}'
            )
        )
        self.stdout.write(f'Start Year: {start_year}')
        self.stdout.write(f'End Year: 2025 (current)')
        self.stdout.write(f'Mode: {"DRY RUN" if dry_run else "LIVE IMPORT"}')
        if limit:
            self.stdout.write(f'Limit: First {limit} stations only')
        if skip_existing:
            self.stdout.write(f'Skip Existing: Yes')
        self.stdout.write(f'{"="*70}\n')

        # Fetch list of available stations
        self.stdout.write('Fetching list of BC stations...')
        station_ids = self.get_station_list()
        
        if not station_ids:
            self.stdout.write(self.style.ERROR('Failed to fetch station list'))
            return
        
        self.stdout.write(
            self.style.SUCCESS(f'Found {len(station_ids)} BC stations\n')
        )
        
        # Apply limit if specified
        if limit:
            station_ids = station_ids[:limit]
            self.stdout.write(f'Limited to first {limit} stations\n')
        
        # Filter out stations with existing data if requested
        if skip_existing:
            existing_stations = set(
                WeatherStation.objects.filter(
                    observations__isnull=False
                ).distinct().values_list('station_id', flat=True)
            )
            original_count = len(station_ids)
            station_ids = [sid for sid in station_ids if sid not in existing_stations]
            self.stdout.write(
                f'Skipping {original_count - len(station_ids)} stations with existing data\n'
            )
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\nDRY RUN - Would import:'))
            for i, station_id in enumerate(station_ids, 1):
                self.stdout.write(f'  {i}. Station {station_id} ({start_year}-2025)')
            self.stdout.write(f'\nTotal: {len(station_ids)} stations')
            years = 2025 - start_year + 1
            estimated_hours = len(station_ids) * years * 8760
            self.stdout.write(
                f'Estimated observations: ~{estimated_hours:,} records'
            )
            self.stdout.write(
                f'Estimated time: {len(station_ids) * years * 2 / 60:.1f} hours '
                f'(assuming 2 sec per year per station)'
            )
            return
        
        # Confirm before proceeding
        self.stdout.write(
            self.style.WARNING(
                f'\n⚠️  About to import {len(station_ids)} stations from {start_year}-2025'
            )
        )
        self.stdout.write(
            self.style.WARNING(
                '⚠️  This will take several hours and use significant database space'
            )
        )
        
        confirm = input('\nProceed with import? (yes/no): ')
        if confirm.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Import cancelled'))
            return
        
        # Start import
        self.stdout.write(
            self.style.SUCCESS(f'\n{"="*70}\nStarting import...\n{"="*70}\n')
        )
        
        start_time = time.time()
        success_count = 0
        error_count = 0
        total_observations = 0
        
        for i, station_id in enumerate(station_ids, 1):
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n[{i}/{len(station_ids)}] Processing Station {station_id}...'
                )
            )
            
            try:
                # Call the import_weather_data command for this station
                call_command(
                    'import_weather_data',
                    station_id=station_id,
                    start_year=start_year,
                    stdout=self.stdout,
                    stderr=self.stderr,
                )
                
                # Get observation count for this station
                try:
                    station = WeatherStation.objects.get(station_id=station_id)
                    obs_count = station.observations.count()
                    total_observations += obs_count
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Station {station_id} complete: {obs_count:,} observations'
                        )
                    )
                except WeatherStation.DoesNotExist:
                    pass
                
                success_count += 1
                
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(f'  ✗ Station {station_id} failed: {str(e)}')
                )
            
            # Show progress summary every 10 stations
            if i % 10 == 0:
                elapsed = time.time() - start_time
                rate = i / elapsed
                remaining = (len(station_ids) - i) / rate if rate > 0 else 0
                self.stdout.write(
                    self.style.SUCCESS(
                        f'\n--- Progress: {i}/{len(station_ids)} stations '
                        f'({i/len(station_ids)*100:.1f}%) ---'
                    )
                )
                self.stdout.write(
                    f'Elapsed: {elapsed/3600:.1f}h | '
                    f'Remaining: {remaining/3600:.1f}h | '
                    f'Total obs: {total_observations:,}\n'
                )
        
        # Final summary
        elapsed = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*70}\nImport Complete!\n{"="*70}'
            )
        )
        self.stdout.write(f'Success: {success_count} stations')
        self.stdout.write(f'Errors: {error_count} stations')
        self.stdout.write(f'Total observations imported: {total_observations:,}')
        self.stdout.write(f'Total time: {elapsed/3600:.2f} hours')
        self.stdout.write(f'Average: {elapsed/len(station_ids):.1f} seconds per station')
        self.stdout.write(f'{"="*70}\n')

    def get_station_list(self):
        """Fetch list of BC stations from ECCC."""
        base_url = 'https://dd.weather.gc.ca/today/climate/observations/hourly/csv/BC/'
        
        try:
            response = requests.get(base_url, timeout=30)
            response.raise_for_status()
            
            # Parse HTML to find CSV files
            csv_files = re.findall(
                r'climate_hourly_BC_(\d+)_\d{4}_P1H\.csv',
                response.text
            )
            station_ids = sorted(set(csv_files))
            
            return station_ids
            
        except Exception as e:
            self.stderr.write(f'Error fetching station list: {e}')
            return []
