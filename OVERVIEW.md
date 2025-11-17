# BC Weather Dashboard v2 – AI Notes

Goal:
- Build a fast weather dashboard for BC wildfire stations.

Stack:
- Backend: Django + Django REST Framework + Postgres (no Docker, no auth).
- Frontend: React + TypeScript + Vite.
- Map: Leaflet (React-Leaflet).
- Charts: any simple React chart lib (Recharts/Chart.js).

Core features (v2):
- Map of weather stations.
- Station list + search.
- Date range selector.
- For selected station + date range:
  - Summary stats (temp, RH, wind, precip).
  - Time series charts (temp, RH, wind).

Out of scope (v2):
- Fire history.
- User accounts.
- Exports (PDF/CSV).
- Forecasts / FWI.
- Docker.