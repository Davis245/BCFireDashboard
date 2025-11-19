# BC Wildfire Data Import - Updated Guide

## What's New

The `import_bcws_data.py` script has been updated with the following improvements:

### Key Updates

1. **Fixed Field Mappings**: Corrected all field mappings to match your database models
   - `temperature`, `relative_humidity`, `precipitation` (not `hourly_*`)
   - Proper handling of integer fields (humidity, wind direction)

2. **Station Metadata Management**: 
   - Now imports and updates latitude, longitude, and elevation from CSV
   - Automatically updates station info if it changes

3. **Timezone Support**: 
   - Proper Pacific timezone handling (`pytz`)
   - Observation times are now timezone-aware

4. **Better Progress Tracking**:
   - Shows total observations imported
   - Tracks unique stations processed
   - Verbose mode for detailed output
   - Summary statistics at completion

5. **Improved Error Handling**:
   - Gracefully handles missing CSV files (404s)
   - Better validation of CSV data
   - Continues on row errors without stopping

6. **Performance**:
   - Updates `last_updated` timestamp for stations
   - Efficient bulk create with conflict handling
   - Transaction safety

## Installation

First, install the new dependency:

```bash
cd /Users/davisfranklin/BCFireWeatherDashboard/backend
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage Examples

### Import Recent Data (Last Week)

```bash
# Import from Nov 11 to yesterday
python manage.py import_bcws_data --start-date 2025-11-11

# Same with verbose output
python manage.py import_bcws_data --start-date 2025-11-11 --verbose
```

### Import Specific Date

```bash
# Import just Nov 17, 2025
python manage.py import_bcws_data --date 2025-11-17
```

### Import Date Range

```bash
# Import January 2025
python manage.py import_bcws_data --start-date 2025-01-01 --end-date 2025-01-31

# Import all of 2025 so far
python manage.py import_bcws_data --start-date 2025-01-01 --verbose
```

### Import Historical Data

```bash
# Import 2024 data (this will take a while!)
python manage.py import_bcws_data --start-date 2024-01-01 --end-date 2024-12-31
```

## Expected Output

### Normal Mode
```
Importing BC Wildfire Service data from 2025-11-11 to 2025-11-17

  ✓ 2025-11-11: 2845 observations
  ✓ 2025-11-12: 2867 observations
  ✓ 2025-11-13: 2891 observations
  ✓ 2025-11-14: 2903 observations
  ✓ 2025-11-15: 2878 observations
  ✓ 2025-11-16: 2889 observations
  ✓ 2025-11-17: 2901 observations

======================================================================
Import Complete!
======================================================================
Date Range: 2025-11-11 to 2025-11-17
Success: 7 days
Errors: 0 days
Total Observations: 20,174
Unique Stations: 124
======================================================================
```

### Verbose Mode
```
Importing BC Wildfire Service data from 2025-11-17 to 2025-11-17

  ✓ 2025-11-17: 2901 observations from 124 stations

======================================================================
Import Complete!
======================================================================
Date Range: 2025-11-17 to 2025-11-17
Success: 1 days
Errors: 0 days
Total Observations: 2,901
Unique Stations: 124
======================================================================
```

## Data Fields Imported

The script imports all available fields from the BC Wildfire Service:

**Basic Weather:**
- Temperature (°C)
- Relative Humidity (%)
- Precipitation (mm)
- Wind Speed (km/h)
- Wind Direction (degrees)
- Wind Gust (km/h)

**Fire Weather Indices (Hourly):**
- Hourly Fine Fuel Moisture Code (FFMC)
- Hourly Initial Spread Index (ISI)
- Hourly Fire Weather Index (FWI)

**Fire Weather Indices (Daily):**
- Fine Fuel Moisture Code (FFMC)
- Duff Moisture Code (DMC)
- Drought Code (DC)
- Initial Spread Index (ISI)
- Buildup Index (BUI)
- Fire Weather Index (FWI)

**Additional:**
- Danger Rating (Low, Moderate, High, Very High, Extreme)
- Snow Depth (cm)
- Solar Radiation

**Station Metadata:**
- Station Code
- Station Name
- Latitude
- Longitude
- Elevation (m)

## Troubleshooting

### Missing Data
If certain dates show "No data available", the BC Wildfire Service may not have published data for that date yet.

### Duplicate Data
The script uses `ignore_conflicts=True` for bulk inserts, so re-running the same date range is safe and won't create duplicates.

### Verify Import

Check what was imported:

```bash
python manage.py shell
```

```python
from weather.models import WeatherStation, HourlyObservation
from datetime import datetime

# Check station count
print(f"Total stations: {WeatherStation.objects.count()}")

# Check observations
print(f"Total observations: {HourlyObservation.objects.count():,}")

# Check latest data
latest = HourlyObservation.objects.first()
print(f"Latest observation: {latest.observation_time}")
print(f"Station: {latest.station.name}")
print(f"Temperature: {latest.temperature}°C")
print(f"Humidity: {latest.relative_humidity}%")

# Check a specific date
date = datetime(2025, 11, 17).date()
count = HourlyObservation.objects.filter(observation_time__date=date).count()
print(f"Observations on {date}: {count:,}")
```

### Database Size

Monitor your database growth:

```bash
python manage.py shell -c "
from weather.models import HourlyObservation
from django.db import connection
cursor = connection.cursor()
cursor.execute(\"SELECT pg_size_pretty(pg_total_relation_size('weather_hourlyobservation'))\")
print(f'HourlyObservation table size: {cursor.fetchone()[0]}')
"
```

## Performance Notes

- **Import Speed**: ~2,000-3,000 observations per day (varies by # of active stations)
- **Database Growth**: ~1-2 MB per day of data
- **Safe to Re-run**: Script handles duplicates automatically
- **Network**: Requires internet connection to download CSV files

## Next Steps

After importing data, you can:

1. Set up automated daily imports (using cron or similar)
2. Build API endpoints to query the data
3. Create frontend visualizations
4. Add data analysis and reporting features

## Data Source

- **Provider**: BC Wildfire Service
- **URL**: https://www.for.gov.bc.ca/ftp/HPR/external/!publish/BCWS_DATA_MART/
- **Format**: Daily CSV files (one per date)
- **License**: BC Government Open Data License
- **Attribution Required**: Yes - must credit BC Wildfire Service
