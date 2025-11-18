# Weather API Documentation

Base URL: `http://localhost:8000/api/`

## Table of Contents
- [Weather Stations](#weather-stations)
- [Hourly Observations](#hourly-observations)
- [Custom Actions](#custom-actions)
- [Response Examples](#response-examples)

---

## Weather Stations

### List All Stations
```
GET /api/stations/
```

**Query Parameters:**
- `active` (boolean): Filter by active status (`true`/`false`)
- `has_data` (boolean): Only show stations with observations
- `search` (string): Search by station name (case-insensitive)

**Response:**
```json
[
  {
    "id": 1,
    "station_id": "1108395",
    "name": "VANCOUVER INTL A",
    "province": "BC",
    "latitude": "49.19",
    "longitude": "-123.18",
    "elevation": "4.30",
    "is_active": true
  }
]
```

### Get Single Station
```
GET /api/stations/{id}/
```

**Response:**
```json
{
  "id": 1,
  "station_id": "1108395",
  "name": "VANCOUVER INTL A",
  "province": "BC",
  "latitude": "49.19",
  "longitude": "-123.18",
  "elevation": "4.30",
  "is_active": true,
  "last_updated": "2025-11-17T12:00:00Z",
  "observation_count": 8760,
  "latest_observation": "2025-11-17T11:00:00Z"
}
```

### Get Station with Recent Observations
```
GET /api/stations/{id}/with_observations/
```

**Response:**
```json
{
  "id": 1,
  "station_id": "1108395",
  "name": "VANCOUVER INTL A",
  "province": "BC",
  "latitude": "49.19",
  "longitude": "-123.18",
  "elevation": "4.30",
  "is_active": true,
  "last_updated": "2025-11-17T12:00:00Z",
  "recent_observations": [
    {
      "id": 1234,
      "observation_time": "2025-11-17T11:00:00Z",
      "temperature": "15.5",
      "dew_point": "12.3",
      "relative_humidity": 75,
      "precipitation": "0.2",
      "wind_direction": 18,
      "wind_speed": "12.5",
      "visibility": "24.1",
      "station_pressure": "101.32",
      "humidex": null,
      "wind_chill": null,
      "weather_description": "Cloudy"
    }
  ]
}
```

### Get Station Statistics
```
GET /api/stations/{id}/statistics/
```

**Query Parameters:**
- `start_date` (ISO datetime): Start of date range
- `end_date` (ISO datetime): End of date range
- `days` (integer): Alternative to start_date - number of days back (default: 7)

**Example:**
```
GET /api/stations/1/statistics/?days=30
```

**Response:**
```json
{
  "station_id": "1108395",
  "station_name": "VANCOUVER INTL A",
  "start_date": "2025-10-18T12:00:00Z",
  "end_date": "2025-11-17T12:00:00Z",
  "avg_temperature": "12.5",
  "min_temperature": "5.0",
  "max_temperature": "18.2",
  "total_precipitation": "125.4",
  "avg_precipitation": "0.17",
  "avg_humidity": "75.2",
  "min_humidity": 45,
  "max_humidity": 95,
  "avg_wind_speed": "15.3",
  "max_wind_speed": "45.2",
  "total_observations": 720
}
```

---

## Hourly Observations

### List Observations
```
GET /api/observations/
```

**Query Parameters:**
- `station` (integer): Filter by station database ID
- `station_id` (string): Filter by station's ECCC ID (e.g., "1108395")
- `start_date` (ISO datetime): Filter observations after this date
- `end_date` (ISO datetime): Filter observations before this date
- `hours` (integer): Get observations from last N hours
- `limit` (integer): Limit number of results (default: 100, max: 1000)

**Examples:**
```
GET /api/observations/?station_id=1108395&hours=24&limit=50
GET /api/observations/?start_date=2025-11-01T00:00:00Z&end_date=2025-11-17T23:59:59Z
```

**Response:**
```json
[
  {
    "id": 1234,
    "station": 1,
    "station_id": "1108395",
    "station_name": "VANCOUVER INTL A",
    "observation_time": "2025-11-17T11:00:00Z",
    "temperature": "15.5",
    "dew_point": "12.3",
    "relative_humidity": 75,
    "precipitation": "0.2",
    "wind_direction": 18,
    "wind_speed": "12.5",
    "visibility": "24.1",
    "station_pressure": "101.32",
    "humidex": null,
    "wind_chill": null,
    "weather_description": "Cloudy"
  }
]
```

### Get Single Observation
```
GET /api/observations/{id}/
```

### Get Recent Observations (All Stations)
```
GET /api/observations/recent/
```

**Query Parameters:**
- `hours` (integer): Number of hours back (default: 1)
- `limit` (integer): Max results per station (default: 1)

**Response:** Returns recent observations from all stations with data in the specified timeframe.

### Get Latest Observation per Station
```
GET /api/observations/latest/
```

**Response:**
```json
{
  "1108395": {
    "id": 1234,
    "station": 1,
    "station_id": "1108395",
    "station_name": "VANCOUVER INTL A",
    "observation_time": "2025-11-17T11:00:00Z",
    "temperature": "15.5",
    ...
  },
  "1108447": {
    "id": 5678,
    "station": 2,
    "station_id": "1108447",
    "station_name": "VICTORIA INTL A",
    "observation_time": "2025-11-17T11:00:00Z",
    "temperature": "14.2",
    ...
  }
}
```

---

## Common Use Cases

### Dashboard Map View
Get all stations with their latest observations:
```
GET /api/stations/?has_data=true
GET /api/observations/latest/
```

### Station Detail Page
Get station info and recent data:
```
GET /api/stations/{id}/with_observations/
```

### Historical Charts
Get observations for a specific timeframe:
```
GET /api/observations/?station_id=1108395&start_date=2025-11-01&end_date=2025-11-17&limit=1000
```

### Statistics Summary
Get aggregated statistics:
```
GET /api/stations/{id}/statistics/?days=30
```

### Search Stations
Find stations by name:
```
GET /api/stations/?search=vancouver
```

---

## Data Types

### Wind Direction
- Value: 0-36 (representing 0-360 degrees in 10-degree increments)
- 0 = Calm
- 9 = 90° (East)
- 18 = 180° (South)
- 27 = 270° (West)
- 36 = 360° (North)

### Temperature Fields
- `temperature`: Air temperature (°C)
- `dew_point`: Dew point temperature (°C)
- `humidex`: Humidex value (°C) - only in summer
- `wind_chill`: Wind chill (°C) - only in winter

### Null Values
Most weather fields can be `null` if data was unavailable at that time.

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 400 Bad Request
```json
{
  "detail": "Invalid query parameter"
}
```

---

## CORS

CORS is enabled for development. Update `CORS_ALLOWED_ORIGINS` in `settings.py` for production.

---

## Pagination

List endpoints return all results by default. Use the `limit` parameter to control response size:
- Default limit: 100 observations
- Maximum limit: 1000 observations

For larger datasets, use date range filtering to reduce the result set.

---

## Rate Limiting

No rate limiting is currently implemented. Consider adding it for production deployment.
