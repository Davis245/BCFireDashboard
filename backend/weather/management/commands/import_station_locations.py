"""
Django management command to import BC Wildfire weather station locations.
Downloads station metadata from BC Government WFS endpoint.
"""

import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from weather.models import WeatherStation


class Command(BaseCommand):
    help = 'Import BC Wildfire weather station locations from BC Gov WFS'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be updated without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options.get('dry_run', False)
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made\n'))
        
        self.stdout.write(
            self.style.SUCCESS('Fetching station locations from BC Gov WFS...\n')
        )
        
        # Fetch all stations from WFS
        wfs_url = "https://openmaps.gov.bc.ca/geo/pub/wfs"
        params = {
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeName": "pub:WHSE_LAND_AND_NATURAL_RESOURCE.PROT_WEATHER_STATIONS_SP",
            "outputFormat": "json",
            "count": 1000  # Get up to 1000 stations
        }
        
        try:
            response = requests.get(wfs_url, params=params, timeout=30)
            response.raise_for_status()
            geojson = response.json()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Failed to fetch data: {e}'))
            return
        
        features = geojson.get('features', [])
        self.stdout.write(f'Retrieved {len(features)} stations from WFS\n')
        
        # Process each station
        updated_count = 0
        created_count = 0
        skipped_count = 0
        
        for feature in features:
            props = feature.get('properties', {})
            
            station_code = str(props.get('STATION_CODE', '')).strip()
            station_name = props.get('STATION_NAME', '').strip()
            latitude = props.get('LATITUDE')
            longitude = props.get('LONGITUDE')
            elevation = props.get('ELEVATION')
            
            if not station_code:
                skipped_count += 1
                continue
            
            if dry_run:
                # Just show what would be done
                exists = WeatherStation.objects.filter(station_code=station_code).exists()
                action = "UPDATE" if exists else "CREATE"
                self.stdout.write(
                    f'  {action}: {station_code:6} {station_name:30} '
                    f'({latitude:.6f}, {longitude:.6f}) @ {elevation}m'
                )
                if exists:
                    updated_count += 1
                else:
                    created_count += 1
            else:
                # Actually update/create the station
                station, created = WeatherStation.objects.update_or_create(
                    station_code=station_code,
                    defaults={
                        'name': station_name,
                        'latitude': latitude,
                        'longitude': longitude,
                        'elevation': elevation,
                        'is_active': True,
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ Created: {station_code:6} {station_name:30} '
                            f'({latitude:.6f}, {longitude:.6f})'
                        )
                    )
                else:
                    updated_count += 1
                    # Optionally show updated stations
                    # self.stdout.write(f'  ↻ Updated: {station_code:6} {station_name}')
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*70}\n'
                f'Import Complete!\n'
                f'{"="*70}\n'
                f'Created: {created_count} stations\n'
                f'Updated: {updated_count} stations\n'
                f'Skipped: {skipped_count} stations\n'
                f'Total: {created_count + updated_count} stations\n'
                f'{"="*70}\n'
            )
        )
        
        if not dry_run:
            # Show how many existing stations now have coordinates
            total = WeatherStation.objects.count()
            with_coords = WeatherStation.objects.exclude(latitude__isnull=True).count()
            self.stdout.write(
                f'Stations with coordinates: {with_coords}/{total} ({100*with_coords/total:.1f}%)\n'
            )
