# Automated Data Updates

This document explains how to keep your BC Fire Weather Dashboard up-to-date with the latest data from the BC Wildfire Service.

## Overview

The dashboard includes two management commands for data updates:

1. **`import_bcws_data`** - Low-level import for specific date ranges
2. **`update_weather_data`** - High-level automated update (recommended for daily use)

## Quick Start

### Manual Update (Run Once)

Update the last 7 days of data:
```bash
cd backend
source ../.venv/bin/activate
python manage.py update_weather_data
```

Or use the convenience script:
```bash
cd backend
./start_import.sh
```

### Backfill Missing Data

If you haven't updated in a while, backfill all missing data:
```bash
python manage.py update_weather_data --backfill
```

This will automatically:
- Find the most recent observation in your database
- Import all missing dates from then until yesterday
- Skip any dates that already exist (duplicate protection)

## Automated Updates (Cron Job)

### Setup

Run the setup script to configure daily automated updates:
```bash
cd backend
./setup_cron.sh
```

This will:
- Create a cron job that runs daily at 2:00 AM
- Update the last 7 days of data (catches any missed days)
- Log output to `logs/cron_update.log`

### Manual Cron Setup

If you prefer to set up cron manually:

1. Edit your crontab:
   ```bash
   crontab -e
   ```

2. Add this line:
   ```
   0 2 * * * cd /path/to/BCFireWeatherDashboard/backend && source /path/to/.venv/bin/activate && python manage.py update_weather_data >> /path/to/logs/cron_update.log 2>&1
   ```

3. Replace `/path/to/` with your actual project path

### View Cron Logs

```bash
tail -f logs/cron_update.log
```

## Management Commands

### update_weather_data

**Purpose**: Automated daily updates with intelligent gap filling

**Options**:
- `--days-back N` - Update last N days (default: 7)
- `--backfill` - Fill all missing data from last observation to yesterday
- `--email EMAIL` - Send error notifications to this email (requires email config)

**Examples**:
```bash
# Update last 7 days (default)
python manage.py update_weather_data

# Update last 30 days
python manage.py update_weather_data --days-back 30

# Backfill all missing data
python manage.py update_weather_data --backfill

# With email notifications
python manage.py update_weather_data --email admin@example.com
```

**How it works**:
1. Calculates date range (yesterday minus N days)
2. Calls `import_bcws_data` with that range
3. Duplicate observations are automatically ignored
4. Logs errors and optionally sends email alerts

### import_bcws_data

**Purpose**: Low-level import for specific dates or date ranges

**Options**:
- `--date YYYY-MM-DD` - Import single date
- `--start-date YYYY-MM-DD` - Start of date range
- `--end-date YYYY-MM-DD` - End of date range (default: yesterday)
- `--verbose` - Show detailed progress

**Examples**:
```bash
# Import a specific date
python manage.py import_bcws_data --date 2025-12-05

# Import a date range
python manage.py import_bcws_data --start-date 2025-11-01 --end-date 2025-11-30

# Import from start date to yesterday
python manage.py import_bcws_data --start-date 2025-01-01

# Verbose output
python manage.py import_bcws_data --date 2025-12-05 --verbose
```

## Data Source

Data is downloaded from the BC Wildfire Service Data Mart:
```
https://www.for.gov.bc.ca/ftp/HPR/external/!publish/BCWS_DATA_MART/{year}/{date}.csv
```

Each CSV file contains:
- Hourly observations from ~280 weather stations
- Temperature, humidity, wind, precipitation
- Fire weather indices (FFMC, ISI, FWI, danger rating)
- Snow depth and solar radiation

## Duplicate Protection

Both commands use `ignore_conflicts=True` when inserting observations, so:
- ✅ Safe to run multiple times on the same date
- ✅ No duplicate data will be created
- ✅ Existing observations are left unchanged

## Monitoring

### Check Database Status

```bash
python manage.py shell
```

Then in the Python shell:
```python
from weather.models import WeatherStation, HourlyObservation
from django.db.models import Max, Min, Count

# Total counts
print(f"Stations: {WeatherStation.objects.count()}")
print(f"Observations: {HourlyObservation.objects.count()}")

# Date range
date_range = HourlyObservation.objects.aggregate(
    min_date=Min('observation_time'),
    max_date=Max('observation_time')
)
print(f"Data from: {date_range['min_date']} to {date_range['max_date']}")

# Observations per station
stats = HourlyObservation.objects.values('station__name').annotate(
    count=Count('id')
).order_by('-count')[:10]
print("\nTop 10 stations by observation count:")
for s in stats:
    print(f"  {s['station__name']}: {s['count']}")
```

### Check for Missing Dates

```python
from weather.models import HourlyObservation
from django.db.models.functions import TruncDate
from datetime import datetime, timedelta

# Get all unique dates in database
dates_in_db = set(
    HourlyObservation.objects
    .annotate(date=TruncDate('observation_time'))
    .values_list('date', flat=True)
    .distinct()
)

# Find missing dates
start = min(dates_in_db)
end = max(dates_in_db)
current = start

missing_dates = []
while current <= end:
    if current not in dates_in_db:
        missing_dates.append(current)
    current += timedelta(days=1)

print(f"Missing dates: {missing_dates}")
```

## Troubleshooting

### Cron Job Not Running

1. Check crontab is set:
   ```bash
   crontab -l
   ```

2. Check logs:
   ```bash
   tail -100 logs/cron_update.log
   ```

3. Test the command manually:
   ```bash
   cd backend
   source ../.venv/bin/activate
   python manage.py update_weather_data
   ```

### No Data for Recent Dates

BC Wildfire Service typically publishes data with a 1-day delay:
- Today's date (Dec 5): No data available yet
- Yesterday (Dec 4): Data should be available
- Older dates: All data available

### Import Errors

Common issues:
- **404 errors**: Date too recent (not published yet) or too old (removed from server)
- **Timeout errors**: Network issues, try again later
- **CSV parsing errors**: BC changed data format (report as issue)

## Email Notifications

To enable email notifications on errors:

1. Configure Django email settings in `backend/core/settings.py`:
   ```python
   EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
   EMAIL_HOST = 'smtp.gmail.com'
   EMAIL_PORT = 587
   EMAIL_USE_TLS = True
   EMAIL_HOST_USER = 'your-email@gmail.com'
   EMAIL_HOST_PASSWORD = 'your-app-password'
   ADMINS = [('Admin Name', 'admin@example.com')]
   ```

2. Use the `--email` option:
   ```bash
   python manage.py update_weather_data --email admin@example.com
   ```

3. Update your cron job to include the email flag

## Best Practices

1. **Run daily**: Set up cron job to run every night
2. **Use --days-back 7**: Catches any missed days due to downtime
3. **Monitor logs**: Check `logs/cron_update.log` weekly
4. **Backfill after gaps**: If dashboard was offline, run `--backfill` when back online
5. **Don't run too frequently**: BC Wildfire Service updates data once daily

## Current Data Status

After the recent backfill:
- **Date Range**: November 10, 2025 - December 4, 2025 (25 days)
- **Total Observations**: 159,489
- **Unique Stations**: 293
- **Stations with Coordinates**: 269 (91.8%)

## Next Steps

- Set up automated cron job: `./setup_cron.sh`
- Monitor logs regularly
- Consider implementing the historical charts feature to visualize this data
