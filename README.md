# BC Fire Dashboard

A fast weather dashboard for BC wildfire stations.

## Tech Stack

### Backend
- **Django** 4.2.7 - Web framework
- **Django REST Framework** - API development
- **PostgreSQL** - Database
- **django-cors-headers** - CORS support

### Frontend
- **React** 18.2.0 - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Navigation
- **Leaflet** (React-Leaflet) - Interactive maps
- **Recharts** - Data visualization
- **Axios** - HTTP client

## Project Structure

```
BCFireDashboard/
├── backend/
│   ├── core/                  # Django project settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── weather/               # Weather app
│   │   ├── models.py          # Data models
│   │   ├── views.py           # API views
│   │   ├── serializers.py     # DRF serializers
│   │   ├── urls.py            # URL routing
│   │   ├── admin.py           # Django admin
│   │   ├── management/        # Custom management commands
│   │   └── tests/             # Test files
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── WeatherMap.tsx
│   │   │   ├── StationList.tsx
│   │   │   ├── DateRangeSelector.tsx
│   │   │   ├── WeatherSummary.tsx
│   │   │   └── WeatherCharts.tsx
│   │   ├── pages/             # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   └── StationDetail.tsx
│   │   ├── services/          # API services
│   │   │   └── api.ts
│   │   ├── types/             # TypeScript types
│   │   │   └── weather.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

3. Install dependencies (already done):
   ```bash
   pip install -r requirements.txt
   ```

4. Set up PostgreSQL database:
   ```bash
   createdb bc_fire_weather
   ```
   
   Update `backend/core/settings.py` with your database credentials if needed.

5. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. Create a superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```
   
   Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies (already done):
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```
   
   Frontend will be available at `http://localhost:5173`

## Core Features (v2)

- ✅ Map of weather stations
- ✅ Station list with search functionality
- ✅ Date range selector
- ✅ For selected station + date range:
  - Summary statistics (temperature, relative humidity, wind, precipitation)
  - Time series charts (temperature, relative humidity, wind)

## Out of Scope (v2)

- Fire history
- User accounts/authentication
- PDF/CSV exports
- Weather forecasts
- Fire Weather Index (FWI)
- Docker deployment

## Development Notes

- No Docker setup required
- No authentication implemented (as per project scope)
- CORS is configured for local development
- Vite proxy configured to forward `/api` requests to Django backend

## API Endpoints

API endpoints will be available at:
- `http://localhost:8000/api/` - Main API root
- `http://localhost:8000/admin/` - Django admin panel

## Next Steps

1. Define weather station and data models in `backend/weather/models.py`
2. Create serializers and viewsets for the API
3. Implement React components for map, charts, and data display
4. Connect frontend to backend API
5. Add data fetching and state management