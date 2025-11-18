# Weather Data Import Guide

## Overview

This guide explains how to import historical ECCC weather data (2000-present) for all 167 BC stations and set up hourly updates.

## Import Estimates

- **Total Stations**: 167 BC weather stations
- **Time Period**: 2000-2025 (26 years)
- **Estimated Records**: ~38 million hourly observations
- **Estimated Time**: 100-150 hours (4-6 days)
- **Database Size**: ~15-25 GB

## Quick Start

### Option 1: Full Import (Recommended)

Run the full import in the background:

```bash
cd /Users/davisfranklin/BCFireWeatherDashboard/backend
./start_import.sh
```

This will:
- Start the import process in the background
- Create a log file: `import_log.txt`
- Skip stations that already have data (safe to re-run)
- Continue running even if you close the terminal

**Monitor progress:**
```bash
tail -f import_log.txt
```

**Check if still running:**
```bash
ps aux | grep import_all_stations
```

**Stop the import:**
```bash
# Find the process ID
ps aux | grep import_all_stations
# Kill it
kill <PID>
```

### Option 2: Test Import (Small Sample)

Test with just a few stations first:

```bash
.venv/bin/python manage.py import_all_stations --limit 5
```

### Option 3: Manual Station Import

Import specific stations manually:

```bash
# Import one station for 2023 only
.venv/bin/python manage.py import_weather_data --station-id 1108395 --year 2023

# Import one station from 2020-2025
.venv/bin/python manage.py import_weather_data --station-id 1108395 --start-year 2020

# Import one station from 2000-present
.venv/bin/python manage.py import_weather_data --station-id 1108395 --start-year 2000
```

## Set Up Hourly Updates

Once the initial import is complete (or partially complete), set up automatic hourly updates:

```bash
cd /Users/davisfranklin/BCFireWeatherDashboard/backend
./setup_cron.sh
```

This will:
- Add a cron job to run every hour (at :00 minutes)
- Update all active stations with the latest data
- Log output to `logs/update_weather.log`

**View update logs:**
```bash
tail -f logs/update_weather.log
```

**Manually trigger an update:**
```bash
.venv/bin/python manage.py update_weather_data
```

## Available Commands

### `import_all_stations`

Import all BC stations from 2000 onwards.

**Options:**
- `--dry-run` - Show what would be imported without actually importing
- `--limit N` - Only import first N stations (for testing)
- `--skip-existing` - Skip stations that already have observations
- `--start-year YYYY` - Start from a different year (default: 2000)

**Examples:**
```bash
# Dry run to see the plan
.venv/bin/python manage.py import_all_stations --dry-run

# Import first 10 stations (testing)
.venv/bin/python manage.py import_all_stations --limit 10

# Import all stations, skip ones with existing data
.venv/bin/python manage.py import_all_stations --skip-existing

# Import from 2020 onwards only
.venv/bin/python manage.py import_all_stations --start-year 2020
```

### `import_weather_data`

Import data for a specific station.

**Options:**
- `--station-id XXXXXXX` - Station Climate ID (required)
- `--year YYYY` - Import specific year only
- `--start-year YYYY` - Start year (default: 2000)
- `--end-year YYYY` - End year (default: current year)
- `--list-stations` - List all available BC stations

**Examples:**
```bash
# List all available stations
.venv/bin/python manage.py import_weather_data --list-stations

# Import Vancouver Intl Airport for 2023
.venv/bin/python manage.py import_weather_data --station-id 1108395 --year 2023

# Import from 2000-2025
.venv/bin/python manage.py import_weather_data --station-id 1108395 --start-year 2000
```

### `update_weather_data`

Update all active stations with latest data (run hourly).

**Options:**
- `--station-id XXXXXXX` - Update specific station only
- `--hours N` - Fetch data from last N hours (default: 48)

**Examples:**
```bash
# Update all active stations
.venv/bin/python manage.py update_weather_data

# Update specific station
.venv/bin/python manage.py update_weather_data --station-id 1108395

# Fetch last 72 hours of data
.venv/bin/python manage.py update_weather_data --hours 72
```

## Monitoring Import Progress

The import process provides progress updates:

```
[1/167] Processing Station 1015630...
  ✓ 2000: Imported 8760, skipped 0
  ✓ 2001: Imported 8760, skipped 0
  ...
  ✓ Station 1015630 complete: 227,760 observations

--- Progress: 10/167 stations (6.0%) ---
Elapsed: 0.5h | Remaining: 7.5h | Total obs: 2,277,600
```

## Troubleshooting

### Import Stopped or Failed

The import is safe to restart. Use `--skip-existing` to resume:

```bash
.venv/bin/python manage.py import_all_stations --skip-existing
```

### Check Database Size

```bash
# Connect to database and check size
.venv/bin/python manage.py shell -c "
from weather.models import WeatherStation, HourlyObservation
print(f'Stations: {WeatherStation.objects.count()}')
print(f'Observations: {HourlyObservation.objects.count():,}')
"
```

### Verify Data for a Station

```bash
.venv/bin/python manage.py shell -c "
from weather.models import WeatherStation
station = WeatherStation.objects.get(station_id='1108395')
print(f'{station.name}: {station.observations.count():,} observations')
print(f'Date range: {station.observations.last().observation_time} to {station.observations.first().observation_time}')
"
```

### Remove Cron Job

```bash
# Edit crontab
crontab -e

# Or remove all cron jobs
crontab -r
```

## Performance Tips

1. **Run during off-hours**: The import is network and database intensive
2. **Monitor disk space**: Ensure you have at least 30GB free
3. **Check Neon limits**: Monitor your Neon database usage during import
4. **Resume if interrupted**: Use `--skip-existing` to safely resume

## Next Steps

After data is imported:
1. ✅ Set up hourly cron updates
2. Create API endpoints to query the data
3. Build frontend visualizations
4. Add fire weather index calculations
5. Set up monitoring/alerting

## Data Attribution

This data is from Environment and Climate Change Canada (ECCC):
- Source: ECCC Meteorological Service of Canada
- License: ECCC Data Server End-use Licence v2.1
- Requirement: Must attribute ECCC as data source
