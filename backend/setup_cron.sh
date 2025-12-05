#!/bin/bash

# BC Fire Weather Dashboard - Cron Job Setup Script
# This script helps you set up automated daily data updates

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================================================"
echo "BC Fire Weather Dashboard - Cron Job Setup"
echo "========================================================================"
echo ""

# Get the absolute path to the project directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
VENV_PATH="$PROJECT_DIR/.venv"
MANAGE_PY="$SCRIPT_DIR/manage.py"

echo "Project directory: $PROJECT_DIR"
echo "Backend directory: $SCRIPT_DIR"
echo "Virtual environment: $VENV_PATH"
echo ""

# Check if virtual environment exists
if [ ! -d "$VENV_PATH" ]; then
    echo -e "${YELLOW}Warning: Virtual environment not found at $VENV_PATH${NC}"
    echo "Please create a virtual environment first."
    exit 1
fi

# Check if manage.py exists
if [ ! -f "$MANAGE_PY" ]; then
    echo -e "${YELLOW}Warning: manage.py not found at $MANAGE_PY${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Project structure verified${NC}"
echo ""

# Generate the cron command
CRON_COMMAND="0 2 * * * cd $SCRIPT_DIR && source $VENV_PATH/bin/activate && python $MANAGE_PY update_weather_data >> $PROJECT_DIR/logs/cron_update.log 2>&1"

echo "The following cron job will be added:"
echo "----------------------------------------------------------------------"
echo "$CRON_COMMAND"
echo "----------------------------------------------------------------------"
echo ""
echo "This will run daily at 2:00 AM and:"
echo "  • Update weather data for the last 7 days"
echo "  • Log output to logs/cron_update.log"
echo ""

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"
echo -e "${GREEN}✓ Created logs directory${NC}"
echo ""

# Ask for confirmation
read -p "Do you want to add this cron job? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Backup existing crontab
    crontab -l > "$PROJECT_DIR/crontab_backup_$(date +%Y%m%d_%H%M%S).txt" 2>/dev/null || true
    
    # Add the cron job (check if it already exists first)
    (crontab -l 2>/dev/null | grep -v "update_weather_data"; echo "$CRON_COMMAND") | crontab -
    
    echo ""
    echo -e "${GREEN}✓ Cron job added successfully!${NC}"
    echo ""
    echo "Current crontab:"
    echo "----------------------------------------------------------------------"
    crontab -l
    echo "----------------------------------------------------------------------"
    echo ""
    echo "Logs will be written to: $PROJECT_DIR/logs/cron_update.log"
    echo ""
    echo "To view logs:"
    echo "  tail -f $PROJECT_DIR/logs/cron_update.log"
    echo ""
    echo "To remove the cron job later:"
    echo "  crontab -e"
    echo "  (then delete the line with 'update_weather_data')"
    echo ""
else
    echo ""
    echo "Cron job NOT added."
    echo ""
    echo "To add it manually later, run:"
    echo "  crontab -e"
    echo ""
    echo "And add this line:"
    echo "  $CRON_COMMAND"
    echo ""
fi

echo "========================================================================"
echo "Manual Update Commands"
echo "========================================================================"
echo ""
echo "To update data manually:"
echo "  cd $SCRIPT_DIR"
echo "  source $VENV_PATH/bin/activate"
echo "  python $MANAGE_PY update_weather_data"
echo ""
echo "To backfill all missing data:"
echo "  python $MANAGE_PY update_weather_data --backfill"
echo ""
echo "To import a specific date range:"
echo "  python $MANAGE_PY import_bcws_data --start-date 2025-11-01 --end-date 2025-11-30"
echo ""
echo "========================================================================"
