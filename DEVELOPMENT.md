# BC Fire Dashboard - Development Guide

## Quick Start

### Start Backend
```bash
cd backend
source .venv/bin/activate  # macOS/Linux
python manage.py runserver
```

### Start Frontend
```bash
cd frontend
npm run dev
```

## Project Structure Created

### Backend Files ✅
- `backend/manage.py` - Django management script
- `backend/core/` - Django project configuration
  - `settings.py` - All Django settings (includes REST framework, CORS, PostgreSQL config)
  - `urls.py` - Main URL routing
  - `wsgi.py` & `asgi.py` - WSGI/ASGI applications
- `backend/weather/` - Weather app
  - `models.py` - Ready for data models
  - `views.py` - Ready for API views
  - `serializers.py` - Ready for DRF serializers
  - `urls.py` - App-specific URL routing
  - `admin.py` - Django admin configuration
  - `apps.py` - App configuration
  - `management/commands/` - Custom management commands
  - `tests/` - Test files
- `backend/requirements.txt` - Python dependencies
- `backend/.gitignore` - Python/Django specific ignores
- `backend/.env.example` - Environment variables template

### Frontend Files ✅
- `frontend/package.json` - npm dependencies and scripts
- `frontend/tsconfig.json` - TypeScript configuration
- `frontend/vite.config.ts` - Vite configuration with proxy
- `frontend/index.html` - HTML entry point
- `frontend/src/`
  - `main.tsx` - React entry point
  - `App.tsx` - Main App component with Router
  - `App.css` & `index.css` - Base styles
  - `components/` - Reusable components
    - `WeatherMap.tsx` - Map component (Leaflet)
    - `StationList.tsx` - Station list with search
    - `DateRangeSelector.tsx` - Date picker
    - `WeatherSummary.tsx` - Summary statistics
    - `WeatherCharts.tsx` - Time series charts (Recharts)
  - `pages/` - Page components
    - `Dashboard.tsx` - Main dashboard page
    - `StationDetail.tsx` - Station detail page
  - `services/`
    - `api.ts` - Axios API client
  - `types/`
    - `weather.ts` - TypeScript type definitions
- `frontend/.gitignore` - Node/React specific ignores
- `frontend/.env.example` - Frontend environment variables

## Dependencies Installed ✅

### Backend
- Django 4.2.7
- djangorestframework 3.14.0
- psycopg2-binary 2.9.9
- django-cors-headers 4.3.1

### Frontend
- React 18.2.0
- React Router DOM 6.20.0
- TypeScript 5.2.2
- Vite 5.0.8
- Leaflet & React-Leaflet 4.2.1
- Recharts 2.10.3
- Axios 1.6.2

## Before You Start Coding

### 1. Set up PostgreSQL Database
```bash
# Create database
createdb bc_fire_weather

# Or using psql
psql
CREATE DATABASE bc_fire_weather;
\q
```

### 2. Run Initial Migrations
```bash
cd backend
source .venv/bin/activate
python manage.py migrate
```

### 3. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

## Configuration Notes

### Backend (Django)
- **Port**: 8000
- **Database**: PostgreSQL (configured in `settings.py`)
- **CORS**: Enabled for `http://localhost:5173`
- **API Root**: `/api/`
- **Admin Panel**: `/admin/`

### Frontend (React + Vite)
- **Port**: 5173
- **Proxy**: `/api` requests forwarded to `http://localhost:8000`
- **Hot Module Replacement**: Enabled

## Next Development Steps

### Backend
1. Define models in `weather/models.py`
   - WeatherStation (name, location, etc.)
   - WeatherData (timestamp, temp, humidity, wind, precip, etc.)

2. Create serializers in `weather/serializers.py`
   - WeatherStationSerializer
   - WeatherDataSerializer

3. Create viewsets in `weather/views.py`
   - WeatherStationViewSet
   - WeatherDataViewSet

4. Register viewsets in `weather/urls.py`

5. Run migrations after creating models:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Frontend
1. Implement API service methods in `services/api.ts`
2. Implement component logic in `components/`
3. Set up routing in `App.tsx`
4. Add state management (React hooks)
5. Style components

## Useful Commands

### Backend
```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Run tests
python manage.py test weather
```

### Frontend
```bash
# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## API Documentation

Once you implement the API, it will be available at:
- `GET /api/` - API root
- Django REST Framework's browsable API will be available for testing

## Troubleshooting

### Backend Issues
- If you get database connection errors, check PostgreSQL is running and credentials in `settings.py`
- If imports fail, ensure virtual environment is activated

### Frontend Issues
- If you see module not found errors, run `npm install` again
- Clear Vite cache: `rm -rf node_modules/.vite`
- The TypeScript errors you see are just type definition warnings and won't prevent the app from running

## Ready to Code! 🚀

All files are set up and dependencies are installed. You can now start implementing the functionality according to your OVERVIEW.md specifications.
