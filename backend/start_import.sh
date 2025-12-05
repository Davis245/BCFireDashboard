#!/bin/bash

# BC Fire Weather Dashboard - Daily Update Script
# Run this manually to update yesterday's data
# Or use setup_cron.sh to schedule it automatically

set -e

# Get the absolute path to the backend directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_DIR/.venv"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================================================"
echo "BC Fire Weather Dashboard - Manual Data Update"
echo "========================================================================"
echo ""

# Check virtual environment
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Error: Virtual environment not found at $VENV_PATH${NC}"
    exit 1
fi

# Activate virtual environment and run update
cd "$SCRIPT_DIR"
source "$VENV_PATH/bin/activate"

echo "Running data update..."
echo ""

python manage.py update_weather_data

echo ""
echo -e "${GREEN}✓ Update complete!${NC}"
echo ""
echo "To view database stats:"
echo "  python manage.py shell -c \"from weather.models import *; print(f'Stations: {WeatherStation.objects.count()}, Observations: {HourlyObservation.objects.count()}')\""
echo ""
