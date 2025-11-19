# Quick Start - Data Import Success! ✅

## Current Database Status

Your BC Fire Weather Dashboard now has:
- **293 Weather Stations** across BC
  - **269 stations (91.8%)** with latitude/longitude coordinates
  - **258 stations (88.1%)** with both coordinates AND observation data
- **53,512 Hourly Observations**
- **Data Range**: November 10-18, 2025 (8 days)

## Import Commands

### Import Station Locations
```bash
cd /Users/davisfranklin/BCFireWeatherDashboard/backend
source .venv/bin/activate

# Import/update all station coordinates from BC Gov
python manage.py import_station_locations

# Dry run to see what would change
python manage.py import_station_locations --dry-run
```

### Import Weather Data
```bash
cd /Users/davisfranklin/BCFireWeatherDashboard/backend
source .venv/bin/activate

# Import yesterday's data
python manage.py import_bcws_data --date 2025-11-17

# Import last 7 days
python manage.py import_bcws_data --start-date 2025-11-10
```

### Import with Verbose Output
```bash
python manage.py import_bcws_data --date 2025-11-17 --verbose
```

### Import Specific Date Range
```bash
# Import all of November so far
python manage.py import_bcws_data --start-date 2025-11-01 --end-date 2025-11-17

# Import last month (October)
python manage.py import_bcws_data --start-date 2025-10-01 --end-date 2025-10-31
```

## What Was Fixed

1. ✅ **BOM Handling**: CSV files have a UTF-8 BOM that was preventing parsing
   - Solution: Changed from `decode('utf-8')` to `decode('utf-8-sig')`

2. ✅ **Field Mapping**: CSV headers have quotes in column names
   - Solution: Dynamic key matching to find correct column names

3. ✅ **Field Sizes**: Solar radiation and snow depth values exceeded database limits
   - Solution: Increased field precision in models and created migration
   - `snow_depth`: 6 digits → 8 digits
   - `solar_radiation`: 8 digits → 10 digits

4. ✅ **Timezone Support**: Added proper Pacific timezone handling with pytz

5. ✅ **Station Locations**: Added latitude/longitude/elevation import
   - Source: BC Government WFS (Web Feature Service)
   - **269 stations** now have precise coordinates for mapping
   - Automatic update/create for new stations

## Verify Your Data

### Check Database Status
```bash
python manage.py shell -c "
from weather.models import WeatherStation, HourlyObservation
print(f'Stations: {WeatherStation.objects.count()}')
print(f'Observations: {HourlyObservation.objects.count():,}')
"
```

### View Sample Data
```bash
python manage.py shell
```

```python
from weather.models import WeatherStation, HourlyObservation

# Get a station
station = WeatherStation.objects.first()
print(f"{station.name} ({station.latitude}, {station.longitude})")

# Get recent observations
recent = HourlyObservation.objects.filter(station=station)[:5]
for obs in recent:
    print(f"{obs.observation_time}: {obs.temperature}°C, {obs.relative_humidity}% RH")

# Get stations with coordinates
mapped_stations = WeatherStation.objects.exclude(latitude__isnull=True).count()
print(f"Stations with coordinates: {mapped_stations}")
```

## Next Steps

Now that you have data, you can:

1. **Start the Backend API**
   ```bash
   python manage.py runserver
   # API available at http://localhost:8000/api/
   ```

2. **Test the API Endpoints**
   - All stations: http://localhost:8000/api/stations/
   - All observations: http://localhost:8000/api/observations/
   - Station detail: http://localhost:8000/api/stations/1/

3. **Start the Frontend**
   ```bash
   cd ../frontend
   npm run dev
   # Dashboard at http://localhost:5173
   ```

4. **Import More Historical Data**
   ```bash
   # Import all of 2025
   python manage.py import_bcws_data --start-date 2025-01-01 --end-date 2025-11-17
   
   # This will take several hours but runs safely in the background
   nohup python manage.py import_bcws_data --start-date 2025-01-01 > import.log 2>&1 &
   ```

## Automated Daily Updates

To keep your data fresh, set up a daily cron job:

```bash
# Edit your crontab
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * cd /Users/davisfranklin/BCFireWeatherDashboard/backend && /Users/davisfranklin/BCFireWeatherDashboard/backend/.venv/bin/python manage.py import_bcws_data --date $(date -v-1d +\%Y-\%m-\%d) >> /Users/davisfranklin/BCFireWeatherDashboard/backend/import.log 2>&1
```

## Data Fields Available

Each observation includes:
- **Weather**: temperature, humidity, precipitation, wind speed/direction/gust
- **Fire Indices (Hourly)**: FFMC, ISI, FWI
- **Fire Indices (Daily)**: FFMC, DMC, DC, ISI, BUI, FWI
- **Other**: danger rating, snow depth, solar radiation

Each station includes:
- Station code, name, latitude, longitude, elevation
- Last updated timestamp
- Active status

## Troubleshooting

**No data imported (0 observations)**:
- Check that the date exists on the BC Wildfire Service
- Future dates won't have data yet
- Some historical dates may be missing

**Database connection errors**:
- Make sure PostgreSQL is running
- Check `core/settings.py` for database credentials

**Field overflow errors**:
- Already fixed by migration 0002
- If you see this, run: `python manage.py migrate`

## Files Modified

- ✅ `weather/management/commands/import_bcws_data.py` - Fixed CSV parsing
- ✅ `weather/models.py` - Increased field sizes
- ✅ `requirements.txt` - Added pytz
- ✅ Created migration `0002_alter_hourlyobservation_snow_depth_and_more.py`

Your dashboard is now ready to display real BC wildfire weather data! 🔥📊🗺️
